import requests
import logging

def do_auth(func):
    """
    decorator to auth if need
    """
    
    def reauth(self, *args, **kwargs):

        if not self.jwt_token and not self.auth():
            return None

        try:

            return func(self, *args, **kwargs)

        except requests.exceptions.HTTPError as e:

            if e.response.status_code != 401:
                raise e

        self.jwt_token = None

        if not self.auth():
            return None

        return func(self, *args, **kwargs)

    return reauth        

class BVC_Client(object):

    def __init__(self, url, username, password):

        self.url = url
        self.username = username
        self.password = password

        self.session = requests.Session()
        self.session.verify = False

        self.jwt_token = None

    def auth(self):
        
        r = self.session.post('{}/api/auth'.format(self.url),
            json={'username':self.username, 'password':self.password})

        if r.status_code != 200:
            logging.error("bvc auth failed, status: %d, message: %s", r.status_code, r.text)

        r.raise_for_status()

        res = r.json()

        self.jwt_token = res.get('access_token')
    
        return self.jwt_token is not None

    @do_auth
    def get_user_cameras(self, user_id):
        
        """
        @return [{...}, ...]
        """

        r = self.session.get('{0}/api/user/{1}/cameras'.format(self.url, user_id),
            headers={'Authorization': 'JWT {}'.format(self.jwt_token)})

        if r.status_code != 200:
            logging.error("bvcapi get_user_cameras failed, status: %d", r.status_code)

        r.raise_for_status()

        logging.debug("bvcapi get_user_cameras status: %d", r.status_code)

        return r.json()['cameras']
    @do_auth
    def new_user_cameras(self, user_id, cameras):
      
        """
        @cameras [{...}, ...]
        """

        r = self.session.post('{0}/api/user/{1}/cameras'.format(self.url, user_id),
            headers={'Authorization': 'JWT {}'.format(self.jwt_token)},
            json=cameras)

        if r.status_code // 100 != 2:
            logging.error("bvcapi new_user_cameras failed, status: %d", r.status_code)

        r.raise_for_status()

        logging.debug("bvcapi new_user_cameras status: %d", r.status_code)

        return True

    @do_auth
    def set_user_cameras(self, user_id, cameras):
        
        """
        @cameras [{...}, ...]
        """

        r = self.session.put('{0}/api/user/{1}/cameras'.format(self.url, user_id),
            headers={'Authorization': 'JWT {}'.format(self.jwt_token)},
            json=cameras)

        if r.status_code // 100 != 2:
            logging.error("bvcapi set_user_cameras failed, status: %d", r.status_code)

        r.raise_for_status()

        logging.debug("bvcapi set_user_cameras status: %d", r.status_code)

        return True

    @do_auth
    def new_camera_alert(self, camera_id, alert):
        
        r = self.session.post('{0}/api/cameras/{1}/alerts'.format(self.url, camera_id),
            headers={'Authorization': 'JWT {}'.format(self.jwt_token)},
            json=alert)
        
        if r.status_code // 100 != 2:
            logging.error("bvcapi new_camera_alert failed, status: %d", r.status_code)
        
        r.raise_for_status()
        return True

    @do_auth
    def get_active_cameras(self):
        """
        @return [{...}, ...]
        """

        r = self.session.get('{0}/api/active_cameras'.format(self.url),
            headers={'Authorization': 'JWT {0}'.format(self.jwt_token)})

        if r.status_code != 200:
            logging.error("bvcapi get_active_cameras failed, status: %d", r.status_code)

        r.raise_for_status()

        logging.debug("bvcapi get_cameras status: %d", r.status_code)

        return r.json()['cameras']

    @do_auth
    def post_status(self, status):
        """
        """

        r = self.session.post('{0}/api/reco_status'.format(self.url),
            headers={'Authorization': 'JWT {0}'.format(self.jwt_token)},
            json=status)

        r.raise_for_status()

        logging.debug("/api/reco_status status: %d", r.status_code)

        return None

    @do_auth
    def post_reco_end(self):
        """
        """

        r = self.session.post('{0}/api/reco_end'.format(self.url),
            headers={'Authorization': 'JWT {0}'.format(self.jwt_token)},
            json={})

        r.raise_for_status()

        logging.debug("/api/reco_end: %d", r.status_code)

        return None

    @do_auth
    def get_camera_alerts(self, camera_id):

        r = self.session.get('{0}/api/cameras/{1}/alerts'.format(self.url, camera_id),
                        headers={'Authorization': 'JWT {0}'.format(self.jwt_token)})

        if r.status_code != 200:
            logging.error("bvcapi get_camera_alerts failed, camera: [%d], status: %d", camera_id, r.status_code)

        r.raise_for_status()

        logging.debug("bvcapi get_camera_alerts, camera: [%d], status: %d", camera_id, r.status_code)

        alerts = r.json()['alerts']

        if not isinstance(alerts,list):
            logging.error("bvcapi get_camera_alerts invalid result, camera: [%d], %s", camera_id, alerts)
            return None

        return alerts
    
    @do_auth
    def post_alert(self, alert):
        """
        posts alert to backend
        """
        
        r = self.session.post('{0}/api/alerts'.format(self.url),
                        headers={'Authorization': 'JWT {0}'.format(self.jwt_token)},
                        json=alert.as_dict())

        if r.status_code != 201:
            logging.error('bvcapi: failed to post alert, status: %d', r.status_code)
    
        r.raise_for_status()

        logging.debug("bvcapi post_alert, alert: %s, status: %d", alert, r.status_code)

        logging.info('post alert {2} / {0} \'{1}\''.format(alert.camera_id, alert.camera_name, alert.alert_type))

        return True

    @do_auth
    def post_thumbnail(self, data):
        
        camera_id = data.get('camera_id')
        #print("post_thumbnail", data)
        
        r = self.session.put('{}/api/camera/{}/thumbnail'.format(self.url, camera_id),
                        headers={'Authorization': 'JWT {0}'.format(self.jwt_token)},
                        json=data)
        
        if r.status_code != 204:
            logging.error('bvcapi: failed to post thumbnail, status: %d', r.status_code)

        r.raise_for_status()

        logging.info('post thumbnail [{}]'.format(camera_id))
