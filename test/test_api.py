import unittest

import requests
import json

##################################################

use_dev = True

if use_dev:

    rogapi_url='https://rog-api-dev.herokuapp.com'      # dev-server
    rogapi_username = 'bvc-dev@gorog.co'
    rogapi_password = 'password123!!!'

    #bvcapi_url = 'http://localhost:5000'
    bvcapi_url = 'https://dev.gorog.co'  # BVC Dev Server
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


def do_auth(self, username, password):

    r = session.post('{}/api/auth'.format(bvcapi_url), 
        json={'username': username,'password': password})

    self.assertEqual(r.status_code, 200)

    return r.json()['access_token'] if r.status_code==200 else None

def do_get_cameras(self, access_token):
      
    r = session.get('{}/api/user/{}/cameras'.format(bvcapi_url, bvc_user_id), 
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
        pass

    def test_ok(self):

        access_token = do_auth(self, bvcapi_username, bvcapi_password)

        self.assertTrue(isinstance(access_token,str))

    def test_fail_1(self):

        r = session.post('{}/api/auth'.format(bvcapi_url), 
            json={'username': bvcapi_username,'password': '111'+bvcapi_password})

        self.assertEqual(r.status_code, 401)

    def test_fail_2(self):

        r = session.post('{}/api/auth'.format(bvcapi_url), 
            json={'username': '111'+bvcapi_username,'password': bvcapi_password})

        self.assertEqual(r.status_code, 401)

class Test_unknown_resource(unittest.TestCase):

    def test_1(self):

        r = session.get(bvcapi_url+'/api/cameras1')

        self.assertEqual(r.status_code, 404)

class Test_get_cameras(unittest.TestCase):
      
    def setUp(self):
          
        self.access_token = do_auth(self, reco_username, reco_password)
        self.assertTrue(isinstance(self.access_token,str))

    def test_get_active_cameras(self):

        r = session.get('{}/api/active_cameras'.format(bvcapi_url), 
            headers = {'Authorization': 'JWT ' + self.access_token })

        self.assertEqual(r.status_code, 200)

        cameras = r.json()
        check_response_cameras(self, cameras)
  
    def test_get_user_cameras(self):
    
        r = session.get('{}/api/user/{}/cameras'.format(bvcapi_url, bvc_user_id), 
            headers = {'Authorization': 'JWT ' + self.access_token })

        self.assertEqual(r.status_code, 200)

        cameras = r.json()
        check_response_cameras(self, cameras)

    def test_bad_auth(self):

        r = session.get('{}/api/active_cameras'.format(bvcapi_url),
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

        r = session.get('{}/api/cameras/{}'.format(bvcapi_url, self.camera_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token)})

        self.assertEqual(r.status_code, 200)

        camera = r.json()
        check_response_camera(self, camera)

    def test_unknown_camera_1(self):

        r = session.get('{}/api/cameras/{}'.format(bvcapi_url, 123456),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token)})

        self.assertEqual(r.status_code, 404)
      
    def test_unknown_camera_2(self):

        r = session.get('{}/api/cameras/{}'.format(bvcapi_url, "012345678901234567890123"),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token)})

        self.assertEqual(r.status_code, 404)

class Test_camera_alerts(unittest.TestCase):
      
    def setUp(self):
          
        self.access_token = do_auth(self, bvcapi_username, bvcapi_password)
        self.assertTrue(self.access_token is not None)

        cameras = do_get_cameras(self, self.access_token)
        self.assertTrue(len(cameras) > 0)

        self.camera_id = cameras[0].get('id')
        self.assertTrue(isinstance(self.camera_id,int))

    def add_alert(self):
        
        r = session.post('{0}/api/cameras/{1}/alerts'.format(bvcapi_url, self.camera_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            json= dummy_alert)

        self.assertEqual(r.status_code//100, 2)

        alert_id = r.json()['alert']['id']

        return alert_id

    def test_get_1(self):

        r = session.get('{0}/api/cameras/{1}/alerts'.format(bvcapi_url, self.camera_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 200)
        
        check_response_alerts(self,r.json())

    def test_post_1(self):

        # create alert
        r = session.post('{0}/api/cameras/{1}/alerts'.format(bvcapi_url, self.camera_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            json= dummy_alert)

        self.assertEqual(r.status_code, 201)

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

        baseurl = bvcapi_url
        if baseurl[:5] == 'https':
            baseurl = 'http' + baseurl[5:]
        self.assertEqual(r.headers['location'], '{0}/api/cameras/{1}/alerts/{2}'.format(baseurl, self.camera_id, alert_id));

        # get alert
        r = session.get('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id, alert_id),
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

        r = session.put('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id, alert_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            json=dummy_alert_4)

        self.assertEqual(r.status_code, 200)

        res = r.json()

        # get alert again
        r = session.get('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id, alert_id),
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
        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id, alert_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 204)

    def test_delete_1(self):

        # create alert
        alert_id = self.add_alert()

        # try delete

        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, "12345", alert_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 404)

        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id,"123456"),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 404)

        # delete
        r = session.delete('{0}/api/cameras/{1}/alerts/{2}'.format(bvcapi_url, self.camera_id,alert_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 204)

    def test_delete_all(self):

        # create alert
        alert_id = self.add_alert()

        # try delete

        r = session.delete('{0}/api/cameras/{1}/alerts'.format(bvcapi_url, "12345"),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 404)

        # delete
        r = session.delete('{0}/api/cameras/{1}/alerts'.format(bvcapi_url, self.camera_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) })

        self.assertEqual(r.status_code, 204)
       
    
if __name__ == '__main__':

    print("Testing URL: \'{}\'".format(bvcapi_url))      

    unittest.main(failfast=True)
    #unittest.main(argv=["", "Test_auth"], failfast=True)
    #unittest.main(argv=["", "Test_auth.test_ssl"])
    #unittest.main(argv=["", "Test_get_cameras"])
    #unittest.main(argv=["", "Test_get_camera"])
    #unittest.main(argv=["", "Test_camera_alerts"])
