import unittest

import requests
import json

##################################################

rogapi_url = 'https://rog-api-dev.herokuapp.com'
rogapi_username = 'bvc-dev@gorog.co'
rogapi_password = 'password123!!!'

#api_url = 'http://localhost:5000'
#api_url = 'https://54.69.73.20'  # BVC Dev Server
api_url = 'https://dev.gorog.co'  # BVC Dev Server

bvc_verify_ssl=True

bvc_username = 'rogt-1'
bvc_password = 'qwerty1'

reco_username = 'reco-1'
reco_password = '0123456789'

session = requests.Session()
session.verify = bvc_verify_ssl

def get_user_id(username, password):

    r = requests.post('{}/api/v1/sessions'.format(rogapi_url), verify=True,
        json={'session': {'email': username, 'password': password}})

    return r.json()['user']['id'] if r.status_code == 200 else None


bvc_user_id = get_user_id(rogapi_username,rogapi_password)


def do_auth(self, username, password):

    r = session.post('{}/api/auth'.format(api_url), 
        json={'username': username,'password': password})

    self.assertEqual(r.status_code, 200)

    return r.json()['access_token'] if r.status_code==200 else None

def do_get_cameras(self, access_token):
      
    r = session.get('{}/api/user/{}/cameras'.format(api_url, bvc_user_id), 
        headers = {'Authorization': 'JWT ' + access_token })

    self.assertEqual(r.status_code, 200)

    cameras = r.json()
    check_response_cameras(self,cameras)

    return cameras.get('cameras')

def check_camera(self,camera):

    self.assertTrue(isinstance(camera,dict))

    camera_id = camera.get('id')
    self.assertTrue(isinstance(camera_id,int))

def check_response_camera(self,camera):

    self.assertTrue(isinstance(camera,dict))

    camera = camera.get('camera')
    self.assertTrue(isinstance(camera,dict))

    check_camera(self,camera)

def check_response_cameras(self,cameras):

    self.assertTrue(isinstance(cameras,dict))

    cameras = cameras.get('cameras')
    self.assertTrue(isinstance(cameras,list))

    for camera in cameras:
      check_camera(self,camera)

    self.assertEqual(len(cameras), len(set([x['id'] for x in cameras])))

def check_alert(self,alert):

    self.assertTrue(alert is not None)
    self.assertTrue(type(alert) is dict)

    alert_id = alert.get('id')
    self.assertTrue(alert_id is not None)
    self.assertTrue(type(alert_id) is str)
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
      check_alert(self,alert)

    self.assertEqual(len(alerts), len(set([x['id'] for x in alerts])))

##################################################

class Test_auth(unittest.TestCase):
    
    def setUp(self):
        # set some stuff up

        if bvc_verify_ssl:
            
            try:

                r = requests.get('{}/'.format(api_url), verify=True)
                if r.status_code != 200:
                    self.skipTest("SSL test failed")

            except requests.exceptions.SSLError as e:
                print("SSL test exception: ", e);
                self.skipTest("SSL test failed")

    @unittest.skipIf(not bvc_verify_ssl, "SSL not supported")
    def test_ssl(self):
        
        r = requests.get('{}/'.format(api_url), verify=True)
        self.assertEqual(r.status_code, 200)

    def test_ok(self):

        access_token = do_auth(self, bvc_username, bvc_password)

        self.assertTrue(isinstance(access_token,str))

    def test_fail_1(self):

        r = session.post('{}/api/auth'.format(api_url), 
            json={'username': bvc_username,'password': '111'+bvc_password})

        self.assertEqual(r.status_code, 401)

    def test_fail_2(self):

        r = session.post('{}/api/auth'.format(api_url), 
            json={'username': '111'+bvc_username,'password': bvc_password})

        self.assertEqual(r.status_code, 401)

class Test_unknown_resource(unittest.TestCase):

    def test_1(self):

        r = session.get(api_url+'/api/cameras1')

        self.assertEqual(r.status_code, 404)

class Test_get_cameras(unittest.TestCase):
      
    def setUp(self):
          
        self.access_token = do_auth(self, reco_username, reco_password)
        self.assertTrue(isinstance(self.access_token,str))

    def test_get_active_cameras(self):

        r = session.get('{}/api/active_cameras'.format(api_url), 
            headers = {'Authorization': 'JWT ' + self.access_token })

        self.assertEqual(r.status_code, 200)

        cameras = r.json()
        check_response_cameras(self, cameras)
  
    def test_get_user_cameras(self):
    
        r = session.get('{}/api/user/{}/cameras'.format(api_url, bvc_user_id), 
            headers = {'Authorization': 'JWT ' + self.access_token })

        self.assertEqual(r.status_code, 200)

        cameras = r.json()
        check_response_cameras(self, cameras)

    def test_bad_auth(self):

        r = session.get('{}/api/active_cameras'.format(api_url),
            headers = {'Authorization': 'JWT 12345' })

        self.assertTrue(r.status_code==401)

class Test_get_camera(unittest.TestCase):

    def setUp(self):
          
        self.access_token = do_auth(self, reco_username, reco_password)
        self.assertTrue(self.access_token is not None)

        cameras = do_get_cameras(self, self.access_token)
        self.assertTrue(len(cameras) > 0)

        self.camera_id = cameras[0].get('id')
        self.assertTrue(isinstance(self.camera_id,int))
 
    def test_1(self):

        r = session.get('{}/api/cameras/{}'.format(api_url, self.camera_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token)})

        self.assertEqual(r.status_code, 200)

        camera = r.json()
        check_response_camera(self, camera)

    def test_unknown_camera_1(self):

        r = session.get('{}/api/cameras/{}'.format(api_url, 123456),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token)})

        self.assertEqual(r.status_code, 404)
      
    def test_unknown_camera_2(self):

        r = session.get('{}/api/cameras/{}'.format(api_url, "012345678901234567890123"),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token)})

        self.assertEqual(r.status_code, 404)

class Test_camera_alerts(unittest.TestCase):
      
    def setUp(self):
          
        self.access_token = do_auth(self, bvc_username, bvc_password)
        self.assertTrue(self.access_token is not None)

        cameras = do_get_cameras(self, self.access_token)
        self.assertTrue(len(cameras) > 0)

        self.camera_id = cameras[0].get('id')
        self.assertTrue(isinstance(self.camera_id,int))

    def test_get_1(self):

        r = session.get('{0}/api/cameras/{1}/alerts'.format(api_url, self.camera_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 200)
        
        check_response_alerts(self,r.json())

    def test_post_1(self):

        # create alert
        r = session.post('{0}/api/cameras/{1}/alerts'.format(api_url, self.camera_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            json= { 'type' : 'RA', 'points' : [[0.0,0.0],[1.0,0.0],[0.5,1.0]]})

        self.assertEqual(r.status_code, 200)

        res = r.json()

        self.assertTrue(res is not None)
        self.assertTrue(type(res) is dict)

        res = res.get('alert')
        self.assertTrue(res is not None)
        self.assertTrue(type(res) is dict)

        alert_id = res.get('id')
        self.assertTrue(alert_id is not None)
        self.assertTrue(type(alert_id) is str)
        self.assertTrue(len(alert_id) > 0)

        # get alert
        r = session.get('{0}/api/cameras/{1}/alerts/{2}'.format(api_url, self.camera_id, alert_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 200)

        res = r.json()

    #    print('new alert: ', res)

        self.assertTrue(res is not None)
        self.assertTrue(type(res) is dict)

        alert = res.get('alert')
        check_alert(self, alert)

        self.assertEqual(alert['type'], 'RA')
        self.assertEqual(len(alert['points']), 3)

        # update alert

        r = session.put('{0}/api/cameras/{1}/alerts/{2}'.format(api_url, self.camera_id, alert_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            json={'type' : 'RA', 'points' : [[0.0,0.0],[1.0,0.0],[0.6,1.0],[0.4,1.0]]})

        self.assertEqual(r.status_code, 200)

        res = r.json()

        # get alert again
        r = session.get('{0}/api/cameras/{1}/alerts/{2}'.format(api_url, self.camera_id, alert_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 200)

        res = r.json()

        self.assertTrue(res is not None)
        self.assertTrue(type(res) is dict)

        alert = res.get('alert')
        check_alert(self, alert)

        self.assertEqual(alert['type'], 'RA')
        self.assertEqual(len(alert['points']), 4)

        # delete alert
        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(api_url, self.camera_id, alert_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 200)
        r.json()

    def test_delete_1(self):

        # create alert
        r = session.post('{0}/api/cameras/{1}/alerts'.format(api_url, self.camera_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            json= { 'type' : 'RA', 'points' : [[0.0,0.0],[1.0,0.0],[0.5,1.0]]})

        self.assertEqual(r.status_code, 200)

        alert_id = r.json()['alert']['id']

        self.assertEqual(r.status_code, 200)

        # try delete

        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(api_url, "12345", alert_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 404)

        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(api_url, self.camera_id,"123456"),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 404)

        # delete
        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(api_url, self.camera_id,alert_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 200)
        r.json()
    
if __name__ == '__main__':

    print("Testing URL: \'{}\'".format(api_url))      

    unittest.main(failfast=True)
    #unittest.main(argv=["", "Test_auth"], failfast=True)
    #unittest.main(argv=["", "Test_auth.test_ssl"])
    #unittest.main(argv=["", "Test_get_cameras"])
    #unittest.main(argv=["", "Test_get_camera"])
    #unittest.main(argv=["", "Test_camera_alerts"])
