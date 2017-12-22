import requests
from alert_object import AlertObject
import reco_config
import logging

class RogClient(object):

    access_token = None

    def __init__(self):
        pass

    def post_alert(self, alert: AlertObject):

        logging.debug(alert.as_dict())

        try:

            res = self.do_post(alert)

            if not self.is_request_succeeded(res):

                if res != 401:
                    return False

                if not self.do_auth():
                    return False

                res = self.do_post(alert)

                if not self.is_request_succeeded(res):
                    return False

            if alert.alert_type:

                logging.info('rog post alert, type: %s, camera: [%d] \'%s\', alert_id: \'%s\'',
                            alert.alert_type, alert.camera_id, alert.camera_name, alert.alert_id)

            else:

                logging.info('rog post TA alert, camera: [%d] \'%s\', alert_id: \'%s\'',
                            alert.camera_id, alert.camera_name, alert.alert_id)

            #logging.info("details: %s", alert.as_debug())

            return True

        except:

            logging.error('rog post alert exception')
            return False


    ###################################

    def is_request_succeeded(self, status_code):
        return status_code == 200 or status_code == 201

    def do_auth(self):
        r = requests.post('{0}/api/v1/sessions'.format(reco_config.rogapi_url),
                          json={'session': {
                              'email': reco_config.rogapi_username,
                              'password': reco_config.rogapi_password
                          }})

        if not self.is_request_succeeded(r.status_code):
            logging.error("rog auth failed, status: %d", r.status_code)
            return False

        auth = r.json()

        self.access_token = auth['jwt']
        return True

    def do_post(self, alert: AlertObject):

        if self.access_token is None:
            return 401  # auth required

        #print('do_post: ', payload)
        #return 200

        data = alert.as_dict()

        if data.get('camera_id', None):
            
            # post first alert { 'camera_id', 'alert_type', ... }

            r = requests.post('{0}/api/v1/alert'.format(reco_config.rogapi_url),
                            headers={'Authorization': '{0}'.format(self.access_token)},
                            json=alert.as_dict())

        else:

            # post after alerts { 'alert_id', 'image' }

            r = requests.post('{0}/api/v1/add_alert_image'.format(reco_config.rogapi_url),
                            headers={'Authorization': '{0}'.format(self.access_token)},
                            json=alert.as_dict())
            
        if not self.is_request_succeeded(r.status_code):
            logging.error("rog post alert failed, camera: [%d], status: %d", alert.camera_id, r.status_code)
            logging.error("%s", alert.as_debug())

        return r.status_code

    def get_alert_ids(self):

        if self.access_token is None:
            self.do_auth()

        if self.access_token is None:
            return None            

        r = requests.get('{0}/api/v1/alert_types'.format(reco_config.rogapi_url))

        if not self.is_request_succeeded(r.status_code):
            return None

        data = r.json()

        if data is None:
            return None

        return data.get("data", None)
        

      
