import unittest

from rogapi import ROG_Client

import cv2
import numpy as np
import base64
import uuid
import datetime

def get_dummy_image():
    
    blank_image = np.zeros((1,1,3), np.uint8)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, encimg = cv2.imencode('.jpg', blank_image, encode_param)
    image = str(base64.b64encode(encimg))
    return image

#rogapi_url='https://rog-api-prod.herokuapp.com'    # prod-server
rogapi_url='https://rog-api-dev.herokuapp.com'      # dev-server
rogapi_username = 'bvc-dev@gorog.co'
rogapi_password = 'password123!!!'

class Test_auth(unittest.TestCase):
    
    def test_true(self):
        rog = ROG_Client(rogapi_url, rogapi_username, rogapi_password)
        res = rog.auth()
        self.assertTrue(res)

    def test_false(self):
        rog = ROG_Client(rogapi_url, rogapi_username, rogapi_password+'xxxx')
        res = rog.auth()
        self.assertFalse(res)

class Test_get_cameras(unittest.TestCase):

    def test_true(self):

        rog = ROG_Client(rogapi_url, rogapi_username, rogapi_password)

        data = rog.get_cameras()

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
    
    def test_true(self):
        
        rog = ROG_Client(rogapi_url,rogapi_username, rogapi_password)

        cameras = rog.get_cameras()
        camera_id = cameras[0]['id']

        bvc_alert_id = str(uuid.uuid4())
        image = get_dummy_image()
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        alert = {
            'camera_id': camera_id, 
            'alert_id': bvc_alert_id, 
            'alert_type_id': 5,
            'timestamp': ts, 
            'image_1': image,
            'image_2': image,
            'image_3': image,
        }

        alert_id = rog.post_alert(alert)

        self.assertTrue(alert_id is not None)

        res = rog.add_alert_image(alert_id,get_dummy_image())

        self.assertTrue(res)

    def test_camera_not_exists(self):
        
        rog = ROG_Client(rogapi_url,rogapi_username, rogapi_password)

        bvc_alert_id = str(uuid.uuid4())
        image = get_dummy_image()
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        alert = {
            'camera_id': 999999, 
            'alert_id': bvc_alert_id, 
            'alert_type_id': 5,
            'timestamp': ts, 
            'image_1': image,
            'image_2': image,
            'image_3': image,
        }

        alert_id = rog.post_alert(alert)

        self.assertTrue(alert_id is None)

if __name__ == '__main__':
    
    unittest.main()
    #rog = ROG_Client(rogapi_url,rogapi_username, rogapi_password)
    #res = rog.get_cameras()
    #rog.post_alert(str(uuid.uuid4()),get_dummy_image())
    #res = rog.get_alert_ids()
    #print(res)
