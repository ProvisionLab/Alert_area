"""
"""
import time
import signal
#import json
import requests
from reco_thread import RecoThread
import reco_config

class RecoClient(object):
    
    api_url = 'http://localhost:5000/'
    access_token = None

    alerts = None

    bStop = False

    def __init__(self):
        self.alerts = []
        signal.signal(signal.SIGINT, self.stop_execution)
        pass

    def stop_execution(self, signum, taskfrm):
        print('Ctrl+C was pressed')
        self.bStop = True
        RecoThread.stop_recognition()

    def run(self):
        
        if self.do_auth('reco1', 'reco1passwd'):
            cameras = self.do_get_cameras()

            if cameras is None:
                print("server cameras request failed")
                return

            threads = []

            if reco_config.cameras:
                cameras = [c for c in cameras if c['name'] in reco_config.cameras]

            for camera in cameras:
                threads.append(RecoThread(self, camera))

            for t in threads:
                t.start()

            print("press Ctrl+C to quit")

            while not self.bStop and RecoThread.exist_any_recognition():
                if self.alerts:
                    self.post_all_alerts()
                else:
                    time.sleep(0.1)

            print('stoping...')

            for t in threads:
                t.join()

            print('Quit')

        pass


    def do_auth(self, username, password):
        r = requests.post(
            self.api_url+'api/auth',
            json={'username':username, 'password':password})

        if r.status_code != 200:
            return False

        self.access_token = r.json()['access_token']
        return True

    def do_get_cameras(self):

        r = requests.get('{0}api/cameras/all/'.format(self.api_url),
                            headers={'Authorization': 'JWT {0}'.format(self.access_token)})

        if r.status_code != 200:
            return None
        
        return r.json()['cameras']

    def get_camera_alerts(self, camera_id: str):

        r = requests.get('{0}api/cameras/{1}/alerts/'.format(self.api_url, camera_id),
                        headers={'Authorization': 'JWT {0}'.format(self.access_token)})

        if r.status_code != 200:
            return None

        return r.json()['alerts']

    def post_reco_alert(self, camera_id: str, alert_id: str):
        
        print('reco alert {0}/{1}'.format(camera_id, alert_id))
        self.alerts.append({'camera_id':camera_id, 'alert_id':alert_id, 'time' : time.time()})
        return

        r = requests.post('{0}api/alerts/'.format(self.api_url),
                        headers={'Authorization': 'JWT {0}'.format(self.access_token)},
                        json={'camera_id' : camera_id, 'alert_id' : alert_id})

        if r.status_code == 200:
            print('reco alert {0}/{1}'.format(camera_id, alert_id))
        else:
            print('failed to post alert')

        pass

    def post_all_alerts(self):
        
        while self.alerts:
            a = self.alerts.pop(0)

            r = requests.post('{0}api/alerts/'.format(self.api_url),
                            headers={'Authorization': 'JWT {0}'.format(self.access_token)},
                            json=a)

            if r.status_code == 200:
                print('post alert {0}/{1}'.format(a['camera_id'], a['alert_id']))
            else:
                print('failed to post alert')
            

if __name__ == '__main__':
    
    app = RecoClient()
    app.run()
