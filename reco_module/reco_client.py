import requests
import json
import reco_reco
import time
import signal

api_url = 'http://localhost:5000/'

access_token = None

def do_auth(username, password):
  r = requests.post(
    api_url+'api/auth', 
    json={'username':username,'password':password})

  if r.status_code!=200:
    return False

  global access_token
  access_token = r.json()['access_token']
  return True

def do_get_cameras():

  r = requests.get('{0}api/cameras/all/'.format(api_url),
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

  if r.status_code!=200:
    return None
  
  return r.json()['cameras']

def get_camera_alerts(access_token:str, camera_id:str):

  r = requests.get('{0}api/cameras/{1}/alerts/'.format(api_url,camera_id),
      headers = {'Authorization': 'JWT {0}'.format(access_token) })

  if r.status_code!=200:
    return None
  
  return r.json()['alerts']

def post_reco_alert(access_token:str, camera_id:str, alert_id:str):

  r = requests.post('{0}api/alerts/'.format(api_url),
      headers = {'Authorization': 'JWT {0}'.format(access_token) },
      json={'camera_id' : camera_id, 'alert_id' : alert_id})

  if r.status_code==200:
    print('reco alert {0}/{1}'.format(camera_id, alert_id))
  else:
    print('failed to post alert')

  pass

def stop_execution(signal, frame):
  print('You pressed Ctrl+C!')
  reco_reco.stop_recognition()

if __name__ == '__main__':

  signal.signal(signal.SIGINT, stop_execution)

  if do_auth('reco1','reco1passwd'):
       
    cameras = do_get_cameras()

    for camera in cameras:

      reco_reco.start_recognition(access_token, camera)

    reco_reco.wait_threads()

    print('Quit')
    pass
 
  