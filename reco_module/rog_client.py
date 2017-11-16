import requests
from alert_object import AlertObject
import reco_config

class UpstreamClient(object):

    access_token = None

    def __init__(self):
        pass

    def post_alert(self, alert: AlertObject):
        
        if reco_config.DEBUG:
            print(alert.as_dict())

        res = self.do_post(alert)

        if not self.is_request_succeeded(res):

            if res != 401:
                print("post alert failed: ", res)
                return False

            if not self.do_auth():
                print("post alert auth failed")
                return False

            res = self.do_post(alert)

            if not self.is_request_succeeded(res):
                print("post alert failed: ", res)
                return False
    
        print('post alert {2} / {0} \'{1}\''.format(alert.camera_id, alert.camera_name, alert.alert_type))
        
        return True

    ###################################

    def is_request_succeeded(self, status_code):
        return status_code == 200 or status_code == 201

    def do_auth(self):
        r = requests.post('{0}/api/v2/sessions'.format(reco_config.usapi_url),
                            json={'session': {'email': reco_config.usapi_username, 'password': reco_config.usapi_password}})

        if not self.is_request_succeeded(r.status_code):
            print('auth failed: ', r.status_code)
            return False

        auth = r.json()

        self.access_token = auth['jwt']

        return True

    def do_post(self, alert: AlertObject):
        
        if self.access_token is None:
            return 401  # auth required

        #print('do_post: ', payload)
        #return 200
        
        r = requests.post('{0}/api/v2/bvc_alert'.format(reco_config.usapi_url),
                            headers={'Authorization': '{0}'.format(self.access_token)},
                            json=alert.as_dict())

        if not self.is_request_succeeded(r.status_code):
            print("do_post failed: ", r.status_code, r.json())
        
        return r.status_code
 