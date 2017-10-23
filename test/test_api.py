import unittest

import requests
import json

##################################################

api_url = 'http://localhost:5000/'

def do_auth(username, password):
  r = requests.post(
    api_url+'api/auth', 
    json={'username':username,'password':password})

  return r.json()['access_token'] if r.status_code==200 else None


def do_get_cameras(atoken):
  r = requests.get(
    api_url+'api/cameras/all/', 
    headers = {'Authorization': 'JWT ' + atoken }
    )
  
  return r.json()['cameras'] if r.status_code==200 else None

def check_camera(self,camera):

    self.assertTrue(camera is not None)
    self.assertTrue(type(camera) is dict)

    camera_id = camera.get('id')
    self.assertTrue(camera_id is not None)
    self.assertTrue(type(camera_id) is str)
    self.assertTrue(len(camera_id) > 0)

def check_response_camera(self,camera):

    self.assertTrue(camera is not None)
    self.assertTrue(type(camera) is dict)

    camera = camera.get('camera')
    self.assertTrue(camera is not None)
    self.assertTrue(type(camera) is dict)

    check_camera(self,camera)

def check_response_cameras(self,cameras):

    self.assertTrue(cameras is not None)
    self.assertTrue(type(cameras) is dict)

    cameras = cameras.get('cameras')
    self.assertTrue(cameras is not None)
    self.assertTrue(type(cameras) is list)

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

  def test_1(self):
    access_token = do_auth('reco1','reco1passwd')
    self.assertTrue(access_token is not None)

  def test_2(self):
    access_token = do_auth('reco1','reco1passwd111')
    self.assertTrue(access_token is None)

  def test_3(self):
    access_token = do_auth('reco1222','reco1passwd')
    self.assertTrue(access_token is None)

class Test_unknown_resource(unittest.TestCase):

  def test_1(self):

    r = requests.get(
      api_url+'api/cameras1/'
      )

    self.assertEqual(r.status_code, 404)

class Test_get_cameras(unittest.TestCase):

  def test_1(self):

    access_token = do_auth('reco1','reco1passwd')
    self.assertTrue(access_token is not None)

    r = requests.get(
      api_url+'api/cameras/all/', 
      headers = {'Authorization': 'JWT ' + access_token }
      )

    self.assertEqual(r.status_code, 200)

    cameras = r.json()
    check_response_cameras(self,cameras)
  
  def test_bad_auth(self):

    r = requests.get(
      api_url+'api/cameras/all/', 
      headers = {'Authorization': 'JWT 12345' })

    self.assertTrue(r.status_code==401)

class Test_get_camera(unittest.TestCase):

  def test_1(self):

    access_token = do_auth('reco1','reco1passwd')
    self.assertTrue(access_token is not None)

    cameras = do_get_cameras(access_token)
    self.assertTrue(cameras is not None)

    camera_id = cameras[0]['id']

    r = requests.get('{0}api/cameras/{1}/'.format(api_url,camera_id),
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

    self.assertEqual(r.status_code, 200)

    camera = r.json()
    check_response_camera(self,camera)

  def test_unknown_camera_1(self):

    access_token = do_auth('reco1','reco1passwd')
    self.assertTrue(access_token is not None)

    r = requests.get(
      api_url+'api/cameras/123456/', 
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

    self.assertEqual(r.status_code, 404)
    
  def test_unknown_camera_2(self):

    access_token = do_auth('reco1','reco1passwd')
    self.assertTrue(access_token is not None)

    r = requests.get(
      api_url+'api/cameras/012345678901234567890123/', 
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

    self.assertEqual(r.status_code, 404)

class Test_camera_alerts(unittest.TestCase):

  def test_get_1(self):

    access_token = do_auth('reco1','reco1passwd')
    self.assertTrue(access_token is not None)

    cameras = do_get_cameras(access_token)
    self.assertTrue(cameras is not None)

    camera_id = cameras[0]['id']

    r = requests.get('{0}api/cameras/{1}/alerts/'.format(api_url,camera_id),
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

    self.assertEqual(r.status_code, 200)
    
    check_response_alerts(self,r.json())

  def test_post_1(self):

    access_token = do_auth('reco1','reco1passwd')
    self.assertTrue(access_token is not None)

    cameras = do_get_cameras(access_token)
    self.assertTrue(cameras is not None)

    camera_id = cameras[0]['id']

    # create alert
    r = requests.post('{0}api/cameras/{1}/alerts/'.format(api_url,camera_id),
      headers = {'Authorization': 'JWT {0}'.format(access_token) },
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
    r = requests.get('{0}api/cameras/{1}/alerts/{2}/'.format(api_url, camera_id, alert_id),
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

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

    r = requests.put('{0}api/cameras/{1}/alerts/{2}/'.format(api_url, camera_id, alert_id),
      headers = {'Authorization': 'JWT {0}'.format(access_token) },
      json={'type' : 'RA', 'points' : [[0.0,0.0],[1.0,0.0],[0.6,1.0],[0.4,1.0]]})

    self.assertEqual(r.status_code, 200)

    res = r.json()

    # get alert again
    r = requests.get('{0}api/cameras/{1}/alerts/{2}/'.format(api_url, camera_id, alert_id),
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

    self.assertEqual(r.status_code, 200)

    res = r.json()

    self.assertTrue(res is not None)
    self.assertTrue(type(res) is dict)

    alert = res.get('alert')
    check_alert(self, alert)

    self.assertEqual(alert['type'], 'RA')
    self.assertEqual(len(alert['points']), 4)

    # delete alert
    r = requests.delete('{0}api/cameras/{1}/alerts/{2}/'.format(api_url,camera_id,alert_id),
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

    self.assertEqual(r.status_code, 200)
    r.json()

  def test_delete_1(self):

    access_token = do_auth('reco1','reco1passwd')
    self.assertTrue(access_token is not None)

    cameras = do_get_cameras(access_token)
    self.assertTrue(cameras is not None)

    camera_id = cameras[0]['id']

    # create alert
    r = requests.post('{0}api/cameras/{1}/alerts/'.format(api_url,camera_id),
      headers = {'Authorization': 'JWT {0}'.format(access_token) },
      json= { 'type' : 'RA', 'points' : [[0.0,0.0],[1.0,0.0],[0.5,1.0]]})

    self.assertEqual(r.status_code, 200)

    alert_id = r.json()['alert']['id']

    self.assertEqual(r.status_code, 200)

    # try delete

    r = requests.delete('{0}api/cameras/{1}/alerts/{2}/'.format(api_url,"12345",alert_id),
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

    self.assertEqual(r.status_code, 404)

    r = requests.delete('{0}api/cameras/{1}/alerts/{2}/'.format(api_url,camera_id,"123456"),
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

    self.assertEqual(r.status_code, 404)

    # delete
    r = requests.delete('{0}api/cameras/{1}/alerts/{2}/'.format(api_url,camera_id,alert_id),
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

    self.assertEqual(r.status_code, 200)
    r.json()
    
if __name__ == '__main__':
    unittest.main()
