import requests
import logging

class ROG_Client(object):

    def __init__(self, url: str, username: str, password: str):

        self.url = url
        self.username = username
        self.password = password
        self.jwt_token = None

        self.session = requests.Session()

    def do_auth(func):
        """
        decorator to auth on demand
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

    def auth(self):
        
        r = self.session.post('{}/api/v1/sessions'.format(self.url),
                            json={'session': {
                                'email': self.username,
                                'password': self.password
                            }})

        if r.status_code != 200:
            logging.error("rog auth failed, status: %d, message: %s", r.status_code, r.text)
            return False    

        """
        {
            'user': {
                'cameraLicenses': int, 
                'firstName': str, 
                'email': str, 
                'lastName': str, 
                'phone': str, 
                'id': int
                }, 
            'jwt': str
        }
        """

        res = r.json()

        self.jwt_token = res.get('jwt')
    
        user_id = res['user']['id']
    
        return self.jwt_token is not None

    @do_auth
    def get_cameras(self):
        
        """
        @return {'data':[...]}, None if error
        """
        
        r = self.session.get('{}/api/v1/me/cameras'.format(self.url),
                        headers={'Authorization': '{0}'.format(self.jwt_token)})

        if r.status_code != 200:
            logging.error("rog get_cameras failed, status: %d, message: %s", r.status_code, r.text)

        r.raise_for_status()

        res = r.json()

        """
        {
            'data': [
                {
                    'rtspUrl': 'rtsp://xxxx:xxxx@xx.xx.xx.xx:xxx', 
                    'image': {
                        'original': 'https://xxxxx.jpg?v=xxxxx', 
                        'thumb': 'https://xxxxx.jpg?v=xxxxx'
                        }, 
                    'name': str, 
                    'id': int, 
                    'username': str
                }, 
                ...
            ]
        }
        """

        return res.get("data", None)
    
    @do_auth
    def post_alert(self, alert):
        """
        @alert  {
                'camera_id': int, 
                'alert_id': str, 
                'alert_type_id': int,
                'timestamp': str, # ISO Extended Z timestamp
                'image_1': str, # base64
                'image_2': str, # base64
                'image_3': str, # base64
                }
        @return: alert_id for add_alert_image
        """

        r = self.session.post('{}/api/v1/alert'.format(self.url),
                            headers={'Authorization': '{}'.format(self.jwt_token)},
                            json={'alert':alert})

        if r.status_code != 201:
            logging.error("rog post_alert failed, status: %d, message: %s", r.status_code, r.text)

            alert['image_3'] = alert.get('image_3','')[:16]
            alert['image_1'] = alert.get('image_1','')[:16]
            alert['image_2'] = alert.get('image_2','')[:16]
            logging.error("%s", str(alert))
    
        r.raise_for_status()

        res = r.json()

        logging.info("rog post_alert, status: %d, response: %s", r.status_code, res)

        """
        {'data': {'id': 53452, 'timestamp': '2017-12-25T19:58:11.912366Z'}}
        """
        
        return res.get('data', {}).get('id')
        #return alert.get('alert_id')

    @do_auth
    def add_alert_image(self, alert_id, image):
        """
        @alert_id: str
        @image: str, base64
        @return: bool
        """
        
        data = {
                'alert_id': alert_id, 
                'image': image,
        }

        r = self.session.post('{}/api/v1/add_alert_image'.format(self.url),
                            headers={'Authorization': '{0}'.format(self.jwt_token)},
                            json=data)

        if r.status_code != 201:
            logging.error("rog add_alert_image failed, status: %d, message: %s", r.status_code, r.text)

            data['image'] = data.get('image','')[:16]
            logging.error("%s", str(data))
            
        r.raise_for_status()

        logging.info("rog add_alert_image, status: %d, message: %s", r.status_code, r.text)

        res = r.json()

        """
        {'data': {'id': 53452, 'timestamp': '2017-12-25T19:58:11.912366Z'}}
        """

        data = res.get('data');
        if data is None:
            return False

        alert_id = data.get('id')
        return alert_id is not None;

    def get_alert_ids(self):
    
        r = self.session.get('{0}/api/v1/alert_types'.format(self.url))

        r.raise_for_status()

        data = r.json()

        if data is None:
            return None

        return data.get("data", None)
