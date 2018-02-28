import unittest

import requests
import json, base64
import cv2, numpy as np
import datetime

##################################################

use_dev = True

if use_dev:

    rogapi_url='https://rog-api-dev.herokuapp.com'      # dev-server
    rogapi_username = 'bvc-dev@gorog.co'
    rogapi_password = 'password123!!!'

    #bvcapi_url = 'http://localhost:5000'
    bvcapi_url = 'https://dev.gorog.co'  # BVC Dev Server
    #bvcapi_url = 'http://dev.gorog.co:5000'  # BVC Dev Server
    #bvcapi_url = 'http://54.69.73.20:5000'  # BVC Dev Server
    bvc_verify_ssl=True

    bvcapi_username = 'rogt-2'
    bvcapi_password = 'qwerty1'

    reco_username = 'reco-1'
    reco_password = '0123456789'

else:
    
    rogapi_url = 'https://rog-api-prod.herokuapp.com'   # prod-server
    rogapi_username = 'bvc-prod@gorog.co'
    rogapi_password = 'q5y2nib,+g!P8zJ+'

    bvcapi_url = 'https://production.gorog.co'  # BVC Prod
    bvc_verify_ssl=True

    bvcapi_username = 'rogt-2'
    bvcapi_password = 'qwerty1'

    reco_username = 'reco-1'
    reco_password = '0123456789'

dummy_alert     = { 'type' : 'RA', 'points' : [[0.0,0.0],[1.0,0.0],[0.5,1.0]]}
dummy_alert_4   = { 'type' : 'RA', 'points' : [[0.0,0.0],[1.0,0.0],[0.5,0.0],[0.5,1.0]]}

#########################################################

session = requests.Session()
session.verify = bvc_verify_ssl

def get_user_id(username, password):

    r = requests.post('{}/api/v1/sessions'.format(rogapi_url), verify=True,
        json={'session': {'email': username, 'password': password}})

    return r.json()['user']['id'] if r.status_code == 200 else None


bvc_user_id = get_user_id(rogapi_username,rogapi_password)

def get_dummy_image():
    
    w = 640
    h = 480
    
    blank_image = np.zeros((h,w,3), np.uint8)

    encode_param = [cv2.IMWRITE_JPEG_QUALITY, 50]
    result, encimg = cv2.imencode('.jpg', blank_image, encode_param)

    image = str(base64.b64encode(encimg), "utf-8")
    return image

class TestCaseBase(unittest.TestCase):
    
    access_token = None
   
    def do_auth(self, username, password):

        r = session.post('{}/api/auth'.format(bvcapi_url), 
            json={'username': username,'password': password})

        self.assertEqual(r.status_code, 200)

        access_token = r.json()['access_token']
        self.assertTrue(isinstance(access_token,str))

        return access_token

    def get_headers(self):
        return {'Authorization': 'JWT {0}'.format(self.access_token) }

    def do_add_dummy_camera(self, camera_id, camera_url='rtsp://12.110.253.194:554'):

        r = session.post('{}/api/user/{}/cameras'.format(bvcapi_url, bvc_user_id),
            headers=self.get_headers(),
            json=[{'id': camera_id, 'name': 'test', 'url': camera_url, 'enabled':False}])

        self.assertEqual(r.status_code, 200)

        return camera_id

    def do_delete_camera(self, camera_id):
        
        r = session.delete('{}/api/cameras/{}'.format(bvcapi_url, camera_id),
            headers=self.get_headers())

    def do_get_cameras(self, access_token):
        
        r = session.get('{}/api/user/{}/cameras'.format(bvcapi_url, bvc_user_id), 
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        cameras = r.json()
        self.check_response_cameras(cameras)

        return cameras.get('cameras')

    def do_get_camera(self, camera_id):

        r = session.get('{}/api/camera/{}'.format(bvcapi_url, camera_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        camera = res.get('camera')
        self.assertTrue(isinstance(camera, dict))

        return camera

    def check_camera(self,camera):

        self.assertTrue(isinstance(camera,dict))

        camera_id = camera.get('id')
        self.assertTrue(isinstance(camera_id,int))
        #self.assertTrue(isinstance(camera.get('connectedOnce'),bool))

    def check_response_camera(self,camera):

        self.assertTrue(isinstance(camera,dict))

        camera = camera.get('camera')
        self.assertTrue(isinstance(camera,dict))

        self.check_camera(camera)

    def check_response_cameras(self,cameras):

        self.assertTrue(isinstance(cameras,dict))

        cameras = cameras.get('cameras')
        self.assertTrue(isinstance(cameras,list))

        for camera in cameras:
            self.check_camera(camera)

        self.assertEqual(len(cameras), len(set([x['id'] for x in cameras])))

    def check_alert(self,alert):

        self.assertTrue(isinstance(alert, dict))

        alert_id = alert.get('id')
        self.assertTrue(isinstance(alert_id, str))
        self.assertTrue(len(alert_id) > 0)

        alert_type = alert.get('type')
        self.assertTrue(alert_type is not None)
        self.assertTrue(type(alert_type) is str)
        self.assertTrue(len(alert_type) > 0)

    def check_response_alerts(self,alerts):

        self.assertTrue(alerts is not None)
        self.assertTrue(type(alerts) is dict)

        alerts = alerts.get('alerts')
        self.assertTrue(alerts is not None)
        self.assertTrue(type(alerts) is list)

        for alert in alerts:
            self.check_alert(alert)

        self.assertEqual(len(alerts), len(set([x['id'] for x in alerts])))

##################################################

class Test_auth(TestCaseBase):
    
    def setUp(self):
        # set some stuff up
        pass

    def test_ok(self):

        access_token = self.do_auth(bvcapi_username, bvcapi_password)

        self.assertTrue(isinstance(access_token,str))

    def test_fail_1(self):

        r = session.post('{}/api/auth'.format(bvcapi_url), 
            json={'username': bvcapi_username,'password': '111'+bvcapi_password})

        self.assertEqual(r.status_code, 401)

    def test_fail_2(self):

        r = session.post('{}/api/auth'.format(bvcapi_url), 
            json={'username': '111'+bvcapi_username,'password': bvcapi_password})

        self.assertEqual(r.status_code, 401)

class Test_unknown_resource(TestCaseBase):

    def test_1(self):

        r = session.get(bvcapi_url+'/api/cameras1')

        self.assertEqual(r.status_code, 404)

class Test_get_cameras(TestCaseBase):
      
    def setUp(self):
          
        self.access_token = self.do_auth(reco_username, reco_password)

    def test_get_active_cameras(self):

        r = session.get('{}/api/active_cameras'.format(bvcapi_url), 
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        cameras = r.json()
        self.check_response_cameras(cameras)
  
    def test_get_user_cameras(self):
    
        r = session.get('{}/api/user/{}/cameras'.format(bvcapi_url, bvc_user_id), 
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        cameras = r.json()
        self.check_response_cameras(cameras)

    def test_bad_auth(self):

        r = session.get('{}/api/active_cameras'.format(bvcapi_url),
            headers = {'Authorization': 'JWT 12345' })

        self.assertTrue(r.status_code==401)

class Test_add_camera(TestCaseBase):
    
    def setUp(self):
          
        self.access_token = self.do_auth(reco_username, reco_password)

    def tearDown(self):
        
        # delete cameras

        r = session.delete('{}/api/cameras/{}'.format(bvcapi_url, 9000),
            headers=self.get_headers())

        r = session.delete('{}/api/cameras/{}'.format(bvcapi_url, 9001),
            headers=self.get_headers())

    def test_add_1(self):
        
        r = session.post('{}/api/user/{}/cameras'.format(bvcapi_url, bvc_user_id),
            headers=self.get_headers(),
            json=[{'id': 9000, 'name': 'test', 'url': 'rtsp://12.110.253.194:554', 'enabled':False}])

        self.assertEqual(r.status_code, 200)

        # delete cameras

        r = session.delete('{}/api/cameras/{}'.format(bvcapi_url, 9000),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 204)

        r = session.delete('{}/api/cameras/{}'.format(bvcapi_url, 9000),
            headers=self.get_headers())

        #print(r.text)
        self.assertEqual(r.status_code, 404)

    def test_add_2(self):
        
        r = session.post('{}/api/user/{}/cameras'.format(bvcapi_url, bvc_user_id),
            headers=self.get_headers(),
            json=[
                {'id': 9000, 'name': 'test', 'url': 'rtsp://12.110.253.194:554', 'enabled':False},
                {'id': 9001, 'name': 'test', 'url': 'rtsp://12.110.253.194:554', 'enabled':False},
                ])

        self.assertEqual(r.status_code, 200)

        # delete cameras

        r = session.delete('{}/api/cameras/{}'.format(bvcapi_url, 9000),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 204)

        r = session.delete('{}/api/cameras/{}'.format(bvcapi_url, 9001),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 204)

    def test_put_2(self):
        
        r = session.put('{}/api/user/{}/cameras'.format(bvcapi_url, bvc_user_id),
            headers=self.get_headers(),
            json=[
                {'id': 9000, 'name': 'test', 'url': 'rtsp://12.110.253.194:554', 'enabled':False},
                {'id': 9001, 'name': 'test', 'url': 'rtsp://12.110.253.194:554', 'enabled':False},
                ])

        self.assertEqual(r.status_code, 204)

        r = session.delete('{}/api/cameras/{}'.format(bvcapi_url, 9000),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 204)

        r = session.delete('{}/api/cameras/{}'.format(bvcapi_url, 9001),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 204)

    def test_add_with_alert(self):
        
        r = session.post('{}/api/user/{}/cameras'.format(bvcapi_url, bvc_user_id),
            headers=self.get_headers(),
            json=[{'id': 9000, 'name': 'test', 'url': 'rtsp://12.110.253.194:554', 'enabled':False, 
                'alerts':[dummy_alert]}])

        self.assertEqual(r.status_code, 200)

        # get alerts

        r = session.get('{}/api/cameras/{}/alerts'.format(bvcapi_url, 9000),
            headers=self.get_headers(),
            json=[{'id': 9000, 'name': 'test', 'url': 'rtsp://12.110.253.194:554', 'enabled':False, 
                'alerts':[dummy_alert]}])

        res = r.json()
        # print('new alert: ', res)

        self.assertTrue(isinstance(res, dict))

        alerts = res.get('alerts')
        self.assertTrue(isinstance(alerts, list))
        self.assertEqual(len(alerts), 1)

        alert = alerts[0]
       
        self.check_alert(alert)

        self.assertEqual(alert['type'], 'RA')
        self.assertEqual(len(alert['points']), 3)                

        # delete cameras

        r = session.delete('{}/api/cameras/{}'.format(bvcapi_url, 9000),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token)})

        self.assertEqual(r.status_code, 204)


class Test_get_camera(TestCaseBase):

    def setUp(self):
          
        self.access_token = self.do_auth(reco_username, reco_password)

        self.camera_id = self.do_add_dummy_camera(9000)

    def tearDown(self):
        
        self.do_delete_camera(9000)
        
    def test_1(self):

        r = session.get('{}/api/cameras/{}'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        camera = r.json()
        self.check_response_camera(camera)

    def test_unknown_camera_1(self):

        r = session.get('{}/api/cameras/{}'.format(bvcapi_url, 123456),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 404)
      
    def test_unknown_camera_2(self):

        r = session.get('{}/api/cameras/{}'.format(bvcapi_url, "012345678901234567890123"),
            headers=self.get_headers())

        self.assertNotEqual(r.status_code//100, 2)

    def test_get_enabled(self):

        r = session.get('{}/api/camera/{}/enabled'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))
        value = res.get('value')
        self.assertTrue(isinstance(value, bool))

    def test_set_enabled(self):
        
        # set False
        
        r = session.put('{}/api/camera/{}/enabled'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers(),
            json={'value': False})

        self.assertEqual(r.status_code, 204)
    
        r = session.get('{}/api/camera/{}/enabled'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res.get('value'), False)
        
        # set True

        r = session.put('{}/api/camera/{}/enabled'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers(),
            json={'value': True})

        self.assertEqual(r.status_code, 204)
    
        r = session.get('{}/api/camera/{}/enabled'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res.get('value'), True)

    def test_connectedOnce(self):

        r = session.get('{}/api/camera/{}/connectedOnce'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))
        value = res.get('value')
        self.assertTrue(isinstance(value, bool))

class Test_camera_alerts(TestCaseBase):
      
    def setUp(self):
          
        self.access_token = self.do_auth(bvcapi_username, bvcapi_password)

        self.camera_id = 9000

        r = session.post('{}/api/user/{}/cameras'.format(bvcapi_url, bvc_user_id),
            headers=self.get_headers(),
            json=[{'id': self.camera_id, 'name': 'test', 'url': 'rtsp://12.110.253.194:554', 'enabled':False}])

        self.assertEqual(r.status_code, 200)

    def tearDown(self):
        
        self.do_delete_camera(9000)

    def add_alert(self):
        
        r = session.post('{0}/api/cameras/{1}/alerts'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers(),
            json= dummy_alert)

        self.assertEqual(r.status_code//100, 2)

        alert_id = r.json()['alert']['id']

        return alert_id

    def test_get_1(self):

        r = session.get('{0}/api/cameras/{1}/alerts'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)
        
        self.check_response_alerts(r.json())

    def test_post_1(self):

        # create alert
        r = session.post('{0}/api/cameras/{1}/alerts'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers(),
            json= dummy_alert)

        self.assertEqual(r.status_code, 201)

        res = r.json()

        self.assertTrue(res is not None)
        self.assertTrue(type(res) is dict)

        res = res.get('alert')
        self.assertTrue(isinstance(res, dict))

        alert_id = res.get('id')
        self.assertTrue(isinstance(alert_id, str))
        self.assertTrue(len(alert_id) > 0)

        baseurl = bvcapi_url
        if baseurl[:5] == 'https':
            baseurl = 'http' + baseurl[5:]
        self.assertEqual(r.headers['location'], '{0}/api/cameras/{1}/alerts/{2}'.format(baseurl, self.camera_id, alert_id));

        # get alert
        r = session.get('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id, alert_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        res = r.json()

    #    print('new alert: ', res)

        self.assertTrue(res is not None)
        self.assertTrue(type(res) is dict)

        alert = res.get('alert')
        self.check_alert(alert)

        self.assertEqual(alert['type'], 'RA')
        self.assertEqual(len(alert['points']), 3)

        # update alert

        r = session.put('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id, alert_id),
            headers=self.get_headers(),
            json=dummy_alert_4)

        self.assertEqual(r.status_code, 204)

        # get alert again
        r = session.get('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id, alert_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        res = r.json()

        self.assertTrue(res is not None)
        self.assertTrue(type(res) is dict)

        alert = res.get('alert')
        self.check_alert(alert)

        self.assertEqual(alert['type'], 'RA')
        self.assertEqual(len(alert['points']), 4)

        # delete alert
        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id, alert_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 204)

    def test_delete_1(self):

        # create alert
        alert_id = self.add_alert()

        # try delete

        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, "12345", alert_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 404)

        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id,"123456"),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 404)

        # delete
        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id,alert_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 204)

    def test_delete_all(self):

        # create alert
        alert_id = self.add_alert()

        # try delete

        r = session.delete('{0}/api/cameras/{1}/alerts'.format(bvcapi_url, "12345"),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 404)

        # delete
        r = session.delete('{0}/api/cameras/{1}/alerts'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 204)
       
class Test_thumbnails(TestCaseBase):
    
    def setUp(self):
          
        self.access_token = self.do_auth(reco_username, reco_password)
        self.assertTrue(self.access_token is not None)

        self.camera_id = self.do_add_dummy_camera(9000)

    def tearDown(self):
        
        self.do_delete_camera(9000)
        pass

    def test_1(self):

        # get thumbnail
        r = session.get('{}/api/camera/{}/thumbnail'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 404)

        # get camera
        camera = self.do_get_camera(self.camera_id)
        self.assertEqual(camera.get('thumbnail',False),False)        

        # set thumbnail
        image = get_dummy_image()
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        r = session.put('{}/api/camera/{}/thumbnail'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers(),
            json={'image': image, 'timestamp': ts})

        self.assertEqual(r.status_code, 204)

        # get thumbnail
        r = session.get('{}/api/camera/{}/thumbnail'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res,dict))

        self.assertEqual(res.get('image'), image)
        self.assertEqual(res.get('timestamp'), ts)

        # get camera
        camera = self.do_get_camera(self.camera_id)
        self.assertEqual(camera.get('thumbnail',False),True)

        # delete thumbnail
        r = session.put('{}/api/camera/{}/thumbnail'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers(),
            json={'image': None})

        self.assertEqual(r.status_code, 204)

        # get thumbnail
        r = session.get('{}/api/camera/{}/thumbnail'.format(bvcapi_url, self.camera_id),
            headers=self.get_headers())

        self.assertEqual(r.status_code, 404)

        # get camera
        camera = self.do_get_camera(self.camera_id)
        self.assertEqual(camera.get('thumbnail',False),False)
            
if __name__ == '__main__':

    print("Testing URL: \'{}\', user: {}".format(bvcapi_url,bvc_user_id))

    unittest.main(failfast=True)
    #unittest.main(argv=["", "Test_auth"], failfast=True)
    #unittest.main(argv=["", "Test_auth.test_ssl"])
    #unittest.main(argv=["", "Test_get_cameras"])
    #unittest.main(argv=["", "Test_add_camera"])
    #unittest.main(argv=["", "Test_add_camera.test_add_1"])
    #unittest.main(argv=["", "Test_add_camera.test_put_2"])
    #unittest.main(argv=["", "Test_add_camera.test_add_with_alert"])
    #unittest.main(argv=["", "Test_get_camera"])
    #unittest.main(argv=["", "Test_get_camera.test_1"])
    #unittest.main(argv=["", "Test_camera_alerts"])
    #unittest.main(argv=["", "Test_camera_alerts.test_post_1"])
    #unittest.main(argv=["", "Test_thumbnails"])
