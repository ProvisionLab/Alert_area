import unittest

from rogapi import ROG_Client

import cv2, numpy as np
import base64
import uuid
import datetime

from requests.exceptions import HTTPError
from requests import Session

use_dev = True

if use_dev:

    rogapi_url='https://rog-api-dev.herokuapp.com'      # dev-server
    rogapi_username = 'bvc-dev@gorog.co'
    rogapi_password = 'password123!!!'

else:
    
    rogapi_url = 'https://rog-api-prod.herokuapp.com'   # prod-server
    rogapi_username = 'bvc-prod@gorog.co'
    rogapi_password = 'q5y2nib,+g!P8zJ+'

#rogapi_username = 'rbartlett802@gmail.com'
#rogapi_password = 'Ginger@777'

alert_type_id = 11 # 'Entering Restricted Area'


def get_dummy_image():
    
    w = 640
    h = 480
    
    blank_image = np.zeros((h,w,3), np.uint8)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    result, encimg = cv2.imencode('.jpg', blank_image, encode_param)

    image = str(base64.b64encode(encimg), "utf-8")
    return image

class Test_auth(unittest.TestCase):
    
    def test_ok(self):
        rog = ROG_Client(rogapi_url, rogapi_username, rogapi_password)
        res = rog.auth()
        self.assertTrue(res)

    def test_invalid_password(self):
        rog = ROG_Client(rogapi_url, rogapi_username, rogapi_password+'xxxx')
        res = rog.auth()
        self.assertFalse(res)

class Test_alert_types(unittest.TestCase):
    
    def setUp(self):
        self.rog = ROG_Client(rogapi_url, rogapi_username, rogapi_password)

    def test_get_alert_types(self):
        ids = self.rog.get_alert_ids()
        print(ids)
        self.assertTrue(isinstance(ids, list))

class Test_get_cameras(unittest.TestCase):

    def setUp(self):
        self.rog = ROG_Client(rogapi_url, rogapi_username, rogapi_password)

    def test_ok(self):

        data = self.rog.get_cameras()

        self.assertTrue(isinstance(data,list))

        for c in data:
            
            rtspUrl = c.get('rtspUrl')
            self.assertTrue(isinstance(rtspUrl,str))
            
            #image = c.get('image')
            #self.assertTrue(isinstance(image,dict))

            name = c.get('name')
            self.assertTrue(isinstance(name,str))

            id = c.get('id')
            self.assertTrue(isinstance(id,int))

            #username = c.get('username')
            #self.assertTrue(isinstance(iusernamed,str))

class Test_post_alert(unittest.TestCase):
    
    def setUp(self):
        
        self.rog = ROG_Client(rogapi_url, rogapi_username, rogapi_password)

        cameras = self.rog.get_cameras()
        self.assertTrue(isinstance(cameras,list) and len(cameras)>0)

        self.assertTrue(isinstance(cameras[0],dict))

        self.camera_id = cameras[0].get('id')
        self.assertTrue(isinstance(self.camera_id,int))

    def test_ok(self):
        
        #bvc_alert_id = str(uuid.uuid4())
        image = get_dummy_image()
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        alert = {
            'camera_id': self.camera_id, 
            #'alert_id': bvc_alert_id, 
            'alert_type_id': alert_type_id,
            'timestamp': ts, 
            'image_1': image,
            'image_2': image,
            'image_3': image,
        }

        alert_id = self.rog.post_alert(alert)
        print(alert_id)

        self.assertTrue(isinstance(alert_id, int))
        self.assertTrue(alert_id > 0)

    def test_camera_not_exists(self):
        
        #bvc_alert_id = str(uuid.uuid4())
        image = get_dummy_image()
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        alert = {
            'camera_id': 999999, 
            #'alert_id': bvc_alert_id, 
            'alert_type_id': alert_type_id,
            'timestamp': ts, 
            'image_1': image,
            'image_2': image,
            'image_3': image,
        }

        with self.assertRaises(HTTPError) as ctx:
            alert_id = self.rog.post_alert(alert)

        #self.assertEqual(ctx.exception.response.status_code, 500)

class Test_add_alert_image(unittest.TestCase):
    
    def setUp(self):
        
        self.rog = ROG_Client(rogapi_url, rogapi_username, rogapi_password)

        cameras = self.rog.get_cameras()
        self.assertTrue(isinstance(cameras,list) and len(cameras)>0)

        self.assertTrue(isinstance(cameras[0],dict))

        self.camera_id = cameras[0].get('id')
        self.assertTrue(isinstance(self.camera_id,int))

    def test_ok(self):
        
        #bvc_alert_id = str(uuid.uuid4())

        image = get_dummy_image()
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        alert = {
            'camera_id': self.camera_id, 
            #'alert_id': bvc_alert_id, 
            'alert_type_id': alert_type_id,
            'timestamp': ts, 
            'image_1': image,
            'image_2': image,
            'image_3': image,
        }

        alert_id = self.rog.post_alert(alert)

        self.assertTrue(alert_id is not None)

        res = self.rog.add_alert_image(alert_id, get_dummy_image())

        self.assertTrue(res)
        
    def test_unknown_alert_id(self):
        
        alert_id = 999999

        with self.assertRaises(HTTPError) as ctx:
            self.rog.add_alert_image(alert_id, get_dummy_image())

        #self.assertEqual(ctx.exception.response.status_code, 404)


class Test_simple(unittest.TestCase):

    def setUp(self):
        
        self.session = Session();

        self.url = rogapi_url
        self.username = rogapi_username
        self.password = rogapi_password

        # auth

        r = self.session.post('{}/api/v1/sessions'.format(self.url),
                    json={'session': {
                        'email': self.username,
                        'password': self.password
                    }})

        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.jwt_token = res.get('jwt')
        self.user_id = res['user']['id']        

        # get cameras

        r = self.session.get('{}/api/v1/me/cameras'.format(self.url),
                    headers={'Authorization': '{}'.format(self.jwt_token)})

        self.assertEqual(r.status_code, 200)

        res = r.json()
        cameras = res.get("data", None)        

        self.assertTrue(isinstance(cameras,list) and len(cameras)>0)
        self.assertTrue(isinstance(cameras[0],dict))

        self.camera_id = cameras[0].get('id')
        self.assertTrue(isinstance(self.camera_id,int))
        
    def test_alert(self):
        
        # post
        
        image = get_dummy_image()
        ts = datetime.datetime.utcnow().isoformat()+'Z'
        
        alert = {
            'camera_id': self.camera_id, 
            #'bvc_alert_id': '9999992',
            'alert_type_id': alert_type_id,
            'timestamp': ts, 
            'image_1': image,
            'image_2': image,
            'image_3': image,
        }

        r = self.session.post('{}/api/v1/alert'.format(self.url),
                headers={'Authorization': '{}'.format(self.jwt_token)},
                json={'alert':alert}
                )
        
        print("\nresponse: ", r.text)
        self.assertEqual(r.status_code, 201)

        res = r.json()

        alert_id = res.get('data', {}).get('id')
        self.assertTrue(isinstance(alert_id, int))        
        pass

    def test_add_image(self):
        
        image = get_dummy_image()
        ts = datetime.datetime.utcnow().isoformat()+'Z'
        
        alert = {
            'camera_id': self.camera_id, 
            #'bvc_alert_id': '9999991',
            'alert_type_id': alert_type_id,
            'timestamp': ts, 
            'image_1': image,
            'image_2': image,
            'image_3': image,
        }

        r = self.session.post('{}/api/v1/alert'.format(self.url),
                headers={'Authorization': '{}'.format(self.jwt_token)},
                json={'alert':alert}
                )
        
        #print("\nresponse: ", r.status_code, r.text)
        self.assertEqual(r.status_code, 201)

        res = r.json()

        alert_id = res.get('data', {}).get('id')
        self.assertTrue(isinstance(alert_id, int))        

        data = {
            'alert_id': alert_id,
            'image': image,
        }

        r = self.session.post('{}/api/v1/add_alert_image'.format(self.url),
                headers={'Authorization': '{}'.format(self.jwt_token)},
                json=data
                )

        #print("\nresponse 1: ", r.status_code, r.text)
        self.assertEqual(r.status_code, 201)

        r = self.session.post('{}/api/v1/add_alert_image'.format(self.url),
                headers={'Authorization': '{}'.format(self.jwt_token)},
                json=data
                )

        #print("\nresponse 2: ", r.status_code, r.text)
        self.assertEqual(r.status_code, 201)

        pass

    def test_remote_camera_image(self):
        
        image = get_dummy_image()
        
        data = {
            'user_id': self.user_id, 
            'camera_id': self.camera_id, 
            'image': image,
            #'image': 'hello',
        }

        r = self.session.post('{}/api/v1/me/remote_camera_image'.format(self.url),
                headers={'Authorization': '{}'.format(self.jwt_token)},
                json=data
                )

        data['image'] = 'image';
        print(data)

        print(r.status_code, r.text)

        self.assertEqual(r.status_code, 201)
        pass

class Test_post_thumbnail(unittest.TestCase):
    
    def setUp(self):
        
        self.rog = ROG_Client(rogapi_url, rogapi_username, rogapi_password)

        cameras = self.rog.get_cameras()
        self.assertTrue(isinstance(cameras,list) and len(cameras)>0)

        self.assertTrue(isinstance(cameras[0],dict))

        self.camera_id = cameras[0].get('id')
        self.assertTrue(isinstance(self.camera_id,int))

    def test_ok(self):
        
        #bvc_alert_id = str(uuid.uuid4())

        image = get_dummy_image()
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        data = {
            'user_id': self.rog.user_id,
            'camera_id': self.camera_id, 
            'image': image,
            #'timestamp': ts, 
        }

        self.rog.remote_camera_image(data)

    def test_connection_fail(self):
        
        #bvc_alert_id = str(uuid.uuid4())

        self.rog.post_connection_fail(self.camera_id)

if __name__ == '__main__':
    
    #unittest.main()
    #unittest.main(verbosity=2)

    #rog = ROG_Client(rogapi_url, rogapi_username, rogapi_password)
    #res = rog.auth()

    #unittest.main(argv=["", "Test_auth"])
    #unittest.main(argv=["", "Test_alert_types"],verbosity=2)
    #unittest.main(argv=["", "Test_post_alert.test_ok"],verbosity=2)
    #unittest.main(argv=["", "Test_add_alert_image.test_ok"],verbosity=2)
    #unittest.main(argv=["", "Test_post_thumbnail"],verbosity=2)
    unittest.main(argv=["", "Test_post_thumbnail.test_ok"])
    #unittest.main(argv=["", "Test_post_thumbnail.test_connection_fail"])
    
    #unittest.main(argv=["", "Test_simple"],verbosity=2)
    #unittest.main(argv=["", "Test_simple.test_alert"],verbosity=2)
    #unittest.main(argv=["", "Test_simple.test_add_image"],verbosity=2)
    #unittest.main(argv=["", "Test_simple.test_remote_camera_image"],verbosity=2)
