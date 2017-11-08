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
        camera.pop('_id')

    return cameras

def update_cameras(cameras : list):

    old_cameras = get_cameras()

    new_ids = [c['id'] for c in cameras]
    del_ids = [c['id'] for c in old_cameras if not c.get('id') is None and c.get('id') not in new_ids]

    for c in cameras:
        set_camera(c)

    delete_cameras(del_ids)
    pass

def delete_cameras(ids : list):

    if len(ids) == 0:
        return

    #print('delete cameras: ', ids)

    result = db.cameras.remove({'id': {'$in': ids }})
    pass

def delete_empty_cameras():
      
    db.cameras.remove({'alerts' : {'$exists': False}})
    db.cameras.remove({'alerts' : {'$exists': True, '$eq': 0}})
    pass

def set_camera( camera : dict ):
      
    try:  

        if db.cameras.find_one({'id': camera['id']}, {'alerts': False }) is None:
            # create new
            result = db.cameras.insert_one(camera)
        else:
            # update one
            result = db.cameras.update_one({'id': camera['id'] }, { '$set': camera})
    
    except:
        return False
      
    return True

def set_camera_by_name( camera : dict ):
      
    try:  

        if db.cameras.find_one({'name' : camera['name']}, {'alerts': False }) is None:
            # create new
            result = db.cameras.insert_one(camera)
        else:
            # update one
            result = db.cameras.update_one({'name' : camera['name']}, { '$set': camera})

    except:
        return False
      
    return True

def get_camera( camera_id : int ):

    try:  

        camera = db.cameras.find_one({ 'id' : camera_id }, { 'alerts': False } )

        if camera is None: 
            return None, 'camera {0} not found'.format(camera_id)

        camera.pop('_id')
        return camera, None

    except:
        return None, 'camera {0} not found'.format(camera_id)

def get_camera_alerts( camera_id : int ):

  try:  

    #camera = db.cameras.find_one({ '_id' : ObjectId(camera_id) }, { 'alerts':True } )
    camera = db.cameras.find_one({ 'id' : camera_id }, { 'alerts':True } )

    if camera is None: 
      return None, 'camera {0} not found'.format(camera_id)

    alerts = camera.get('alerts')
    if alerts is None:
      return [], None

    return alerts, None

  except:
    return None, 'camera {0} not found'.format(camera_id)

def append_camera_alert( camera_id : int, alert : dict ):

    try:  

        alert_id = str(ObjectId())
        alert['id'] = alert_id

        result = db.cameras.update_one({'id' : camera_id }, { '$push': { 'alerts' : alert }} )
        if result.modified_count == 0: 
          return None, 'camera {0} not found'.format(camera_id)
    
        return alert_id, None

    except:
        return None, 'camera {0} not found'.format(camera_id)

def get_camera_alert( camera_id: int, alert_id: int):

  try:  

    camera = db.cameras.find_one({ 'id' : camera_id }, { 'alerts':True } )
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

def delete_camera_alert( camera_id: int, alert_id: str ):

    try:
    
        camera = db.cameras.find_one({ 'id': camera_id }, { 'alerts':True } )
        if camera is None:
          return None, 'camera {0} not found'.format(camera_id)

        alerts = camera.get('alerts')

        if alerts is None:
          return None, 'camera {0} alert {1} not found'.format(camera_id, alert_id)

        new_alerts = [a for a in alerts if a['id'] != alert_id]

        if len(alerts)==len(new_alerts):
          return None, 'camera {0} alert {1} not found'.format(camera_id, alert_id)

        result = db.cameras.update_one({'id': camera_id }, { '$set': { 'alerts' : new_alerts }} )
        return {}, None

    except:
        return None, 'camera {0} not found'.format(camera_id)

def update_camera_alert( camera_id: int, alert_id : str, alert : dict ):

#  print('update alert: {0}: {1}'.format(alert_id, alert))
    try:

        alert['id'] = alert_id

        camera = db.cameras.find_one({ 'id' : camera_id }, { 'alerts':True } )
        if camera is None:
          return None, 'camera {0} not found'.format(camera_id)

        alerts = camera.get('alerts')

        if alerts is not None:
          for i,a in enumerate(alerts):
            if a['id'] == alert_id:
              alerts[i] = alert
              result = db.cameras.update_one({'id': camera_id }, { '$set': { 'alerts' : alerts }} )
              return {}, None

        return None, 'camera {0} alert {1} not found'.format(camera_id, alert_id)

    except:
        return None, 'camera {0} not found'.format(camera_id)
