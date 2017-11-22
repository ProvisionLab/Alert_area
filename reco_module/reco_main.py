"""
main module
"""
import time
import signal
import requests, requests.utils
from reco_thread import RecoThread
from rog_client import RogClient
from alert_object import AlertObject
import reco_config

import reco_logging, logging

class RecoClient(object):
    
    api_url = reco_config.api_url

    access_token = None

    alerts = None

    bStop = False

    def __init__(self):

        self.threads = []
        self.alerts = []

        self.rogapi = RogClient()

        signal.signal(signal.SIGINT, self.stop_execution)
        pass

    def stop_execution(self, signum, taskfrm):
        """
        SIGINT handler
        """
        print('Ctrl+C was pressed')
        self.bStop = True

        logging.info("SIGINT reseived, stop all recognitions")

        for t in self.threads:
            t.stop()
        
    def run(self):
        """
        main loop
        periodically reads config state from backend
        starts/stops recognition threads
        """

        print("press Ctrl+C to quit")

        logging.info("start")

        self.updatate_timer = 0 #time.time()

        while not self.bStop:
            
            update_delta = time.time() - self.updatate_timer
            if update_delta >= reco_config.update_interval:

                if not self.update_cameras():
                    break

                self.updatate_timer = time.time()

            if self.alerts:
                self.post_all_alerts()
            else:
                time.sleep(2.0)

        logging.info("stopping... this may take some time")

        for t in self.threads:
            t.join()

        logging.info("Quit")

    def update_cameras(self):
        """
        gets cameras from backend
        updates recognizers
        """
        
        if not self.do_auth(reco_config.api_username, reco_config.api_password):
            return False

        cameras = self.do_get_cameras()

        if cameras is None:
            logging.error("backend cameras request failed, no cameras returned")
            return False

        if reco_config.filter_cameras:
            cameras = [c for c in cameras if c['name'] in reco_config.filter_cameras]

        # remove disabled cameras
        cameras = [c for c in cameras if c.get('enabled',True)]

        self.set_cameras(cameras)

        return True

    def remove_stoped_threads(self):

        del_threads = [t for t in self.threads if t.bExit]        
        self.threads = [t for t in self.threads if not t.bExit]

        for t in del_threads:
            t.join()

    def set_cameras(self, cameras):
        """
        sets cameras for recognition
        stops/starts recognition
        updates alert areas of recognizers
        """
        
        # remove stoped threads
        self.remove_stoped_threads()

        # get new cameras alerts
        for c in cameras:
            areas = self.get_camera_alerts(c['id'])
            c['areas'] = areas;
            if not areas:
                logging.warning("camera [%d] \'%s\' has no alerts configured", c['id'], c['name'])

        # remove cameras with no alert areas
        cameras = [c for c in cameras if c['areas']]
      
        #
        old_cameras = [t.camera for t in self.threads]

        old_ids = [c['id'] for c in old_cameras]
        new_ids = [c['id'] for c in cameras]
        del_ids = [c['id'] for c in old_cameras if c.get('id') not in new_ids]

        # delete cameras

        del_threads = [t for t in self.threads if t.camera['id'] in del_ids]
        new_threads = [t for t in self.threads if t.camera['id'] not in del_ids]

        for t in del_threads:
            logging.info("stop recognition of camera: [%d] \'%s\'", t.camera['id'], t.camera['name'])
            t.stop()

        self.threads = new_threads

        # update alert areas
        for t in self.threads:
            camera_id = t.camera['id']
            for c in cameras:
                if c['id'] == camera_id:
                    t.camera = c
                    t.update_areas(c['areas'])   

        # add new camera threads
        add_cameras = [c for c in cameras if c['id'] not in del_ids and c['id'] not in old_ids]

        for c in add_cameras:
            logging.info("start recognition of camera: [%d] \'%s\'", c['id'], c['name'])
            t = RecoThread(self, c, c['areas'])
            self.threads.append(t)
            t.start()
            
        self.cameras = cameras
        pass

    def do_auth(self, username, password):

        r = requests.post(
            self.api_url+'/api/auth',
            json={'username':username, 'password':password})

        logging.debug("backend auth status: %d", r.status_code)

        if r.status_code != 200:
            logging.error("backend auth request failed for username %s, status: %d", reco_config.api_username, r.status_code)
            return False

        self.access_token = r.json()['access_token']
        return True

    def do_get_cameras(self):

        r = requests.get('{0}/api/cameras/all/'.format(self.api_url),
                            headers={'Authorization': 'JWT {0}'.format(self.access_token)})

        logging.debug("backend get_cameras status: %d", r.status_code)

        if r.status_code != 200:
            logging.error("backend get_cameras failed, status: %d", r.status_code)
            return None
        
        return r.json()['cameras']

    def get_camera_alerts(self, camera_id: str):

        r = requests.get('{0}/api/cameras/{1}/alerts/'.format(self.api_url, camera_id),
                        headers={'Authorization': 'JWT {0}'.format(self.access_token)})

        logging.debug("backend get_camera_alerts, camera: [%d], status: %d", camera_id, r.status_code)

        if r.status_code != 200:
            logging.error("backend get_camera_alerts failed, camera: [%d], status: %d", camera_id, r.status_code)
            return None

        alerts = r.json()['alerts']

        if not isinstance(alerts,list):
            logging.error("backend get_camera_alerts invalid result, camera: [%d], %s", camera_id, alerts)
            return None

        return alerts

    def post_reco_alert(self, alert: AlertObject):
        """
        appends alert to alerts queue
        """

        self.alerts.append(alert)

    def post_alert_internal(self, alert):
        """
        posts alert to backend
        """
        
        r = requests.post('{0}/api/alerts/'.format(self.api_url),
                        headers={'Authorization': 'JWT {0}'.format(self.access_token)},
                        json=alert.as_dict())

        logging.debug("backend post_alert, alert: %s, status: %d", alert, r.status_code)

        if r.status_code == 200:
            logging.info('post alert {2} / {0} \'{1}\''.format(alert.camera_id, alert.camera_name, alert.alert_type))
        else:
            logging.error('backend: failed to post alert, status: %d', r.status_code)

    def post_all_alerts(self):
        """
        posts all alerts from queue
        """

        while self.alerts:
            alert = self.alerts.pop(0)

            alert.encode_image()

            if reco_config.send_alerts_to_rog:
                self.rogapi.post_alert(alert)
            else:
                self.post_alert_internal(alert)

def get_user_agent(name="BVC reco_module"):
    return name

if __name__ == '__main__':
    
    requests.utils.default_user_agent = get_user_agent

    app = RecoClient()
    app.run()
