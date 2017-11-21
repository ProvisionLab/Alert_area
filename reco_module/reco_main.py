"""
"""
import time
import signal
import requests
from reco_thread import RecoThread
from rog_client import UpstreamClient
from alert_object import AlertObject
import reco_config


class RecoClient(object):
    
    api_url = reco_config.api_url

    access_token = None

    alerts = None

    bStop = False

    def __init__(self):
        self.alerts = []
        signal.signal(signal.SIGINT, self.stop_execution)

        self.usapi = UpstreamClient()
        pass

    def stop_execution(self, signum, taskfrm):
        print('Ctrl+C was pressed')
        self.bStop = True

        for t in self.threads:
            t.stop()
        
    def run(self):
        
        self.threads = []

        print("press Ctrl+C to quit")

        self.updatate_timer = 0 #time.time()

        while not self.bStop:
            
            update_delta = time.time() - self.updatate_timer
            if update_delta >= reco_config.update_interval:
                if not self.update():
                    break
                self.updatate_timer = time.time()

            if self.alerts:
                self.post_all_alerts()
            else:
                time.sleep(0.1)

        print('stoping... this may take some time')

        for t in self.threads:
            t.join()

        print('Quit')

    def update(self):

        if not self.update_cameras():
            return False

        return True

    def update_cameras(self):
        
        if not self.do_auth(reco_config.api_username, reco_config.api_password):
            print("backend auth request failed")
            return False

        cameras = self.do_get_cameras()

        if cameras is None:
            print("backend cameras request failed")
            return False

        if reco_config.cameras:
            cameras = [c for c in cameras if c['name'] in reco_config.cameras]

        self.set_cameras(cameras)

        return True

    def set_cameras(self, cameras):
        
        # remove stoped threads
        del_threads = [t for t in self.threads if t.bExit]        
        self.threads = [t for t in self.threads if not t.bExit]

        for t in del_threads:
            t.join()

        # remove disabled cameras
        cameras = [c for c in cameras if c.get('enabled',True)]

        # get new cameras alerts
        for c in cameras:
            areas = self.get_camera_alerts(c['id'])
            c['areas'] = areas;

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
            print("stop recognition of camera: ", t.camera['name'])
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
            print("start recognition of camera: ", c['name'])
            t = RecoThread(self, c, c['areas'])
            self.threads.append(t)
            t.start()
            
        self.cameras = cameras

        pass

    def do_auth(self, username, password):
        r = requests.post(
            self.api_url+'/api/auth',
            json={'username':username, 'password':password})

        if r.status_code != 200:
            return False

        self.access_token = r.json()['access_token']
        return True

    def do_get_cameras(self):

        r = requests.get('{0}/api/cameras/all/'.format(self.api_url),
                            headers={'Authorization': 'JWT {0}'.format(self.access_token)})

        if r.status_code != 200:
            return None
        
        return r.json()['cameras']

    def get_camera_alerts(self, camera_id: str):

        r = requests.get('{0}/api/cameras/{1}/alerts/'.format(self.api_url, camera_id),
                        headers={'Authorization': 'JWT {0}'.format(self.access_token)})

        if r.status_code != 200:
            print('get_camera_alerts {0} failed: {1}'.format(camera_id, r.status_code))
            return None

        alerts = r.json()['alerts']

        if not isinstance(alerts,list):
            print('get_camera_alerts {0} invalid result: {1}'.format(camera_id, alerts))
            return None

        return alerts

    def post_reco_alert(self, alert: AlertObject):
        
        self.alerts.append(alert)

    def post_alert_internal(self, alert):
        
        r = requests.post('{0}/api/alerts/'.format(self.api_url),
                        headers={'Authorization': 'JWT {0}'.format(self.access_token)},
                        json=alert.as_dict())

        if r.status_code == 200:
            print('post alert {2} / {0} \'{1}\''.format(alert.camera_id, alert.camera_name, alert.alert_type))
        else:
            print('failed to post alert')

    def post_all_alerts(self):
        
        while self.alerts:
            alert = self.alerts.pop(0)

            alert.encode_image()

            if reco_config.send_alerts_to_rog:
                self.usapi.post_alert(alert)        
            else:
                self.post_alert_internal(alert)      
           
if __name__ == '__main__':
    
    app = RecoClient()
    app.run()
