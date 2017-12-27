import unittest

from rogapi import ROG_Client

import cv2
import numpy as np
import base64
import uuid
import datetime

from requests.exceptions import HTTPError

rogapi_url='https://rog-api-dev.herokuapp.com'      # dev-server
rogapi_username = 'bvc-dev@gorog.co'
rogapi_password = 'password123!!!'

#rogapi_url = 'https://rog-api-prod.herokuapp.com'   # prod-server
#rogapi_username = 'bvc-prod@gorog.co'
#rogapi_password = 'q5y2nib,+g!P8zJ+'

def get_dummy_image():
    
    blank_image = np.zeros((1,1,3), np.uint8)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, encimg = cv2.imencode('.jpg', blank_image, encode_param)
    image = str(base64.b64encode(encimg))
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
            'alert_type_id': 5,
            'timestamp': ts, 
            'image_1': image,
            'image_2': image,
            'image_3': image,
        }

        alert_id = self.rog.post_alert(alert)

        self.assertTrue(alert_id is not None)

    def test_camera_not_exists(self):
        
        #bvc_alert_id = str(uuid.uuid4())
        image = get_dummy_image()
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        alert = {
            'camera_id': 999999, 
            #'alert_id': bvc_alert_id, 
            'alert_type_id': 5,
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
            'alert_type_id': 5,
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

if __name__ == '__main__':
    
    unittest.main()
    #unittest.main(verbosity=2)

    #rog = ROG_Client(rogapi_url,rogapi_username, rogapi_password)
    #res = rog.auth()
    #res = rog.get_cameras()
    #res = rog.post_alert(str(uuid.uuid4()),get_dummy_image())
    #res = rog.get_alert_ids()
    #print(res)
