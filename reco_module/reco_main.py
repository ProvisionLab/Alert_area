"""
main module
"""
import os
import time
import signal
import uuid
import requests, requests.utils
from capture_worker import CaptureWorker
from rog_client import RogClient
from alert_object import AlertObject, set_alert_type_ids
import reco_config

import reco_logging, logging

class RecoClient(object):
    
    api_url = reco_config.bvcapi_url
    api_key = reco_config.bvcapi_key

    access_token = None

    alerts = None

    bStop = False

    use_cpu = reco_config.use_cpu

    def __init__(self, reco_num: int, reco_count: int):
        
        self.reco_num = reco_num - 1

        self.reco_id = '{}:{}'.format(reco_config.reco_name, self.reco_num)

        self.reco_count = reco_count

        self.threads = []
        self.alerts = []

        self.rogapi = RogClient()

        signal.signal(signal.SIGINT, self.stop_execution)
        pass

    def stop_execution(self, signum, taskfrm):
        """
        SIGINT handler
        """
        #print('Ctrl+C was pressed')
        self.bStop = True

        logging.info("SIGINT reseived, stop all recognitions")

        if len(self.alerts)>4:
            logging.warning("there are many alerts in queue: %d, reseting them", len(self.alerts))
            self.alerts = []

        for t in self.threads:
            t.stop()
        
    def run(self):
        """
        main loop
        periodically reads config state from backend
        starts/stops recognition threads
        """

        #print("press Ctrl+C to quit")

        logging.info("start")

        set_alert_type_ids(self.rogapi.get_alert_ids())

        self.updatate_timer = 0 #time.time()

        while not self.bStop:
            
            try:
                update_delta = time.time() - self.updatate_timer
                if update_delta >= reco_config.update_interval:

                    if not self.update_cameras():
                        break

                    self.updatate_timer = time.time()

                if self.alerts:
                    self.post_all_alerts()
                else:
                    time.sleep(2.0)

            except (requests.exceptions.ConnectionError) as e:
                logging.error("ConnectionError: %s", str(e))
                time.sleep(30)
                pass

            except:
                logging.exception("exception")
                

        logging.info("stopping... this may take some time")

        for t in self.threads:
            t.join()

        logging.info("Quit")

    def update_cameras(self):
        """
        gets cameras from backend
        updates recognizers
        """
        
        if not self.do_auth():
            return False

        status = self.get_status()
        self.do_send_status(status)

        cameras = self.do_get_cameras()

        if cameras is None:
            logging.error("backend cameras request failed, no cameras returned")
            return False

        #if reco_config.filter_cameras:
        #    cameras = [c for c in cameras if c['name'] in reco_config.filter_cameras]

        # remove disabled cameras
        cameras = [c for c in cameras if c.get('enabled',True)]

        self.set_cameras(cameras)

        return True

    def remove_stoped_threads(self):

        del_threads = [t for t in self.threads if t.bExit]        
        self.threads = [t for t in self.threads if not t.bExit]

        for t in del_threads:
            t.join()

    def get_status(self):
        
        total_fps1 = 0.0
        total_fps = 0.0
        cameras_count = 0
        
        for t in self.threads:
            fps1, fps2 = t.get_fps()
            total_fps1 += fps1
            total_fps += fps2

            if fps1 > 0.0:
                cameras_count += 1

            logging.info("camera [%d] \'%s\' FPS: %.1f/%.1f, areas: %d, users: %s", 
                        t.camera['id'], t.camera['name'], 
                        fps1, fps2, 
                        len(t.camera['areas']),
                        str(t.camera.get('users',[])))

        logging.info("total FPS: %.1f/%.2f for %d cameras", total_fps1, total_fps, cameras_count)

        return {'cameras_count' : cameras_count, 'fps' : total_fps}

    def set_cameras(self, cameras):
        """
        sets cameras for recognition
        stops/starts recognition
        updates alert areas of recognizers
        """
        
        # remove stoped threads
        self.remove_stoped_threads()

        # filter cameras by reco_num
        #cameras = [c for c in cameras if (c['id'] % self.reco_count) == self.reco_num]

        # get new cameras alerts
        for c in cameras:
            areas = self.get_camera_alerts(c['id'])
            c['areas'] = areas;
            if not areas:
                logging.warning("camera [%d] \'%s\' has no alerts configured, users: %s", 
                    c['id'], c['name'], str(c.get('users',[])))

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
                    c_areas = t.camera['areas']
                    t.update_areas(c_areas)

        # add new camera threads
        add_cameras = [c for c in cameras if c['id'] not in del_ids and c['id'] not in old_ids]

        for c in add_cameras:
            logging.info("start recognition of camera: [%d] \'%s\', users: %s", c['id'], c['name'], str(c.get('users',[])))

            t = CaptureWorker(self, c)
            t.use_cpu = self.use_cpu

            self.threads.append(t)
            t.start()
            
        self.cameras = cameras
        pass

    def do_auth(self):
        
        username = 'reco-' + self.reco_id
        password = self.api_key

        r = requests.post(
            self.api_url+'/api/auth',
            json={'username':username, 'password':password})

        logging.debug("backend auth status: %d", r.status_code)

        if r.status_code != 200:
            logging.error("backend auth request failed, status: %d", r.status_code)
            return False

        self.access_token = r.json()['access_token']
        return True

    def do_get_cameras(self):

#        r = requests.get('{0}/api/cameras/enabled'.format(self.api_url),
#                            headers={'Authorization': 'JWT {0}'.format(self.access_token)})
        r = requests.get('{0}/api/active_cameras'.format(self.api_url),
                            headers={'Authorization': 'JWT {0}'.format(self.access_token)})

        logging.debug("backend get_cameras status: %d", r.status_code)

        if r.status_code != 200:
            logging.error("backend get_enabled_cameras failed, status: %d", r.status_code)
            return None
        
        return r.json()['cameras']

    def do_send_status(self, status):
        
        r = requests.post('{0}/api/rs'.format(self.api_url),
                            headers={'Authorization': 'JWT {0}'.format(self.access_token)},
                            json=status)

        logging.debug("/api/rs status: %d", r.status_code)
   

    def get_camera_alerts(self, camera_id: str):

        r = requests.get('{0}/api/cameras/{1}/alerts'.format(self.api_url, camera_id),
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
        
        r = requests.post('{0}/api/alerts'.format(self.api_url),
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

        alerts = []

        while self.alerts:
            alerts.append(self.alerts.pop(0))

        if len(alerts) > reco_config.max_alert_queue_size:
            logging.warning('alerts queue too long (%d), droping', len(alerts))
            alerts = alerts[:reco_config.max_alert_queue_size]

        start_time = time.time()

        for alert in alerts:

            alert.encode_images()

            if reco_config.send_alerts_to_rog:
                self.rogapi.post_alert(alert)
            else:
                self.post_alert_internal(alert)

            if (time.time() - start_time) > 10.0:
                self.alerts = alerts + self.alerts
                break;

            if self.bStop:
                break

def get_user_agent(name="BVC reco_module"):
    return name

pid = None
pid_fname = None

if __name__ == '__main__':
    
    requests.utils.default_user_agent = get_user_agent

    reco_num = int(os.environ.get('RECO_PROC_ID', '1'))
    reco_count = int(os.environ.get('RECO_TOTAL_PROCS', '1'))

    pid = str(os.getpid())
    pid_fname = 'reco_proc_'+str(reco_num)+'.pid'
    f = open(pid_fname, 'w')
    f.write(pid)
    f.close()

    app = RecoClient(reco_num, reco_count)
    #app.use_cpu = reco_count > 1 and reco_num == reco_count
    app.run()

    os.remove(pid_fname)
