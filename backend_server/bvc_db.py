# 2do: check for exceptions

from pymongo import MongoClient
from bson.objectid import ObjectId 

import bvc_config

# connect to database

client = MongoClient(bvc_config.mongoDB_connectStr)
db = client.bvcstorage


def drop():
  db.cameras.drop()


def append_camera( camera : dict ):
  alerts = camera.get('alerts')
  if alerts is not None:
    for alert in alerts:
       alert['id'] = str(ObjectId())
  result = db.cameras.insert_one(camera)

def get_cameras():

  # returns camera list or []

  cursor = db.cameras.find({}, { 'alerts':False })

  cameras = [ camera for camera in cursor ]

  for camera in cameras:
    camera['id'] = str(camera.pop('_id'))

  return cameras

def get_camera( camera_id : str ):

  try:  

    camera = db.cameras.find_one({ '_id' : ObjectId(camera_id) }, { 'alerts': False } )

    if camera is None: 
      return None, 'camera {0} not found'.format(camera_id)

    camera['id'] = str(camera.pop('_id'))

    return camera, None

  except:
    return None, 'camera {0} not found'.format(camera_id)

def get_camera_alerts( camera_id : str ):

  try:  

    camera = db.cameras.find_one({ '_id' : ObjectId(camera_id) }, { 'alerts':True } )

    if camera is None: 
      return None, 'camera {0} not found'.format(camera_id)

    alerts = camera.get('alerts')
    if alerts is None:
      return [], None

    return alerts, None

  except:
    return None, 'camera {0} not found'.format(camera_id)

def append_camera_alert( camera_id : str, alert : dict ):

  try:  

    alert_id = str(ObjectId())
    alert['id'] = alert_id

    result = db.cameras.update_one({'_id' : ObjectId(camera_id) }, { '$push': { 'alerts' : alert }} )
    if result.modified_count == 0: 
      return None, 'camera {0} not found'.format(camera_id)
 
    return alert_id, None

  except:
    return None, 'camera {0} not found'.format(camera_id)

def get_camera_alert( camera_id : str, alert_id : str):

  try:  

    camera = db.cameras.find_one({ '_id' : ObjectId(camera_id) }, { 'alerts':True } )
    if camera is None:
      return None, 'camera {0} not found'.format(camera_id)

    alerts = camera.get('alerts')

    alert = None

    if alerts is not None:
      for i,a in enumerate(alerts):
        if a['id'] == alert_id:
          alert = a
          break;

    if alert is None:
      return None, 'camera {0} alert {1} not found'.format(camera_id, alert_id)

    return alert, None

  except:
    return None, 'camera {0} not found'.format(camera_id)

def delete_camera_alert( camera_id : str, alert_id : str ):

  try:
  
    camera = db.cameras.find_one({ '_id' : ObjectId(camera_id) }, { 'alerts':True } )
    if camera is None:
      return None, 'camera {0} not found'.format(camera_id)

    alerts = camera.get('alerts')

    if alerts is None:
      return None, 'camera {0} alert {1} not found'.format(camera_id, alert_id)

    new_alerts = [a for a in alerts if a['id'] != alert_id]

    if len(alerts)==len(new_alerts):
      return None, 'camera {0} alert {1} not found'.format(camera_id, alert_id)

    result = db.cameras.update_one({'_id' : ObjectId(camera_id) }, { '$set': { 'alerts' : new_alerts }} )
    return {}, None

  except:
    return None, 'camera {0} not found'.format(camera_id)

def update_camera_alert( camera_id : str, alert_id : str, alert : dict ):

#  print('update alert: {0}: {1}'.format(alert_id, alert))
  try:

    alert['id'] = alert_id

    camera = db.cameras.find_one({ '_id' : ObjectId(camera_id) }, { 'alerts':True } )
    if camera is None:
      return None, 'camera {0} not found'.format(camera_id)

    alerts = camera.get('alerts')

    if alerts is not None:
      for i,a in enumerate(alerts):
        if a['id'] == alert_id:
          alerts[i] = alert
          result = db.cameras.update_one({'_id' : ObjectId(camera_id) }, { '$set': { 'alerts' : alerts }} )
          return {}, None

    return None, 'camera {0} alert {1} not found'.format(camera_id, alert_id)

  except:
    return None, 'camera {0} not found'.format(camera_id)
