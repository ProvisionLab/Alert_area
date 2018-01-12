from pymongo import MongoClient
from bson.objectid import ObjectId 
import logging

import bvc_config

# connect to database

client = MongoClient(bvc_config.mongoDB_connectStr)
db = client.bvcstorage


def drop():
    db.users.drop()
    db.cameras.drop()

def get_subs_users():
    
    users = [ {'id':u['uid'], 'cameras': u['cameras'] } for u in db.users.find({})]

    return users

def get_subs_cameras():
    
    cameras = [ {
        'id':c['id'], 
        'users': c['users'],
        'enabled': 'enabled' if c.get('enabled', True) else 'disabled',
        'alerts': len(c.get('alerts',[]))
        } for c in db.cameras.find({})]

    return cameras
    
def get_subscribes():
    
    return {
        'users': get_subs_users(),
        'cameras': get_subs_cameras(),
    }

def is_camera_active(camera):
    
    if not camera.get('enabled', True):
        return False

    if not bool(camera.get('users')):
        return False

    if not bool(camera.get('alerts')):
        return False

    return True

def get_active_cameras():
    """
    returns cids of all active cameras
    """
    
    cursor = db.cameras.find({})

    cids = [ c['id'] for c in cursor if is_camera_active(c) ]

    return cids

def get_cameras_by_cids(cids:list):
    """
    returns cameras from its ids
    """
    
    cursor = db.cameras.find({'id': {'$in': cids }}, {'alerts':False, 'users':False})
    
    cameras = [ camera for camera in cursor if camera.get('enabled', True)]

    for camera in cameras:
        camera.pop('_id')

    return cameras

def get_enabled_cameras():
    
    cursor = db.cameras.find({}, {'alerts':False})

    cameras = [ camera for camera in cursor if camera.get('enabled', True) and len(camera.get('users',[])) > 0]

    for camera in cameras:
        camera.pop('_id')
    
    return cameras

def get_cameras(user_id: int):

    user = db.users.find_one({'uid' : user_id})

    if user is None:
        return []

    cids = user['cameras']

    # returns camera list or []

    cursor = db.cameras.find({'id': {'$in': cids }}, { 'alerts':False, 'users':False })

    cameras = [ camera for camera in cursor ]

    for camera in cameras:
        camera.pop('_id')

    return cameras

def delete_camera(camera_id):
    """
    @return True oon success, False if not found
    """
    
    camera = db.cameras.find_one({'id': camera_id}, {'users': True })

    if camera is None:
        return False

    users = camera.get('users', [])

    for uid in users:
        user = db.users.find_one({'uid': uid}, {'cameras':True})
        if user:
            u_cameras = user.get('cameras', [])
            u_cameras = [cid for cid in u_cameras if cid != camera_id]
            db.users.update_one({'uid': uid}, { '$set': { 'cameras' : u_cameras }})
        
    db.cameras.remove({'id': camera_id})
    return True

def append_camera(user_id: int, camera: dict):
    
    return set_camera(user_id, camera)

def update_cameras(user_id: int, cameras: list):

    try:

        new_ids = [c['id'] for c in cameras]

        logging.info('update cameras: %s, user: %d', str(new_ids), user_id)

        user = db.users.find_one({'uid' : user_id})

        del_ids = []

        if user is None:
            user = {'uid': user_id, 'cameras': new_ids}
            db.users.insert_one(user)
            logging.info('new user created, uid: %d', user_id)
        else:
            old_ids = user['cameras']
            del_ids = [cid for cid in old_ids if cid not in new_ids]
            db.users.update_one({'uid' : user_id}, { '$set': { 'cameras' : new_ids }})
        
        for c in cameras:
            set_camera(user_id, c)

        delete_cameras(user_id, del_ids)

    except:
        return False
    
    return True

def delete_cameras(user_id: int, cids : list):
    """
    removes user_id from cameras
    removes camera if it has no users

    """

    if len(cids) == 0:
        return

    cursor = db.cameras.find({'id': {'$in': cids }}, {'alerts':False})
    cameras = [c for c in cursor]

    del_ids = []

    # update cameras.users

    for camera in cameras:
        users = camera.get('users', [])
        assert(isinstance(users,list))
        new_users = [u for u in users if u != user_id]
        if len(users) > len(new_users):
            cid = camera['id']
            if len(new_users) > 0:
                db.cameras.update_one({'id': cid}, { '$set': { 'users' : new_users }})
            else:
                del_ids.append(camera['id'])

    # delete cameras with no users
    if len(del_ids) > 0:
        logging.warning('delete cameras: %s', str(cids))
        db.cameras.remove({'id': {'$in': del_ids }})

    pass

def delete_empty_cameras():
      
    db.cameras.remove({'alerts' : {'$exists': False}})
    db.cameras.remove({'alerts' : {'$exists': True, '$eq': 0}})
    pass

def set_camera(user_id: int, camera: dict):
    """
    creates or updates camera
    """
    try:

        alerts = camera.get('alerts')
        
        if alerts is not None:
            for alert in alerts:
                alert['id'] = str(ObjectId())

        old_camera = db.cameras.find_one({'id': camera['id']}, {'alerts': False })

        if old_camera is None:
            # create new
            logging.info('new camera created: %s', str(camera))
            camera['users'] = [user_id]
            result = db.cameras.insert_one(camera)
        else:
            # update one
            users = old_camera.get('users', [])
            if user_id not in users:
                users.append(user_id)
            camera['users'] = users
            result = db.cameras.update_one({'id': camera['id'] }, {'$set': camera})
    
    except:
        return False
      
    return True

def set_camera_by_name(camera : dict):
      
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

def set_camera_enabled(camera_id: int, enabled: bool):
    
    try:

        result = db.cameras.update_one({'id': camera_id }, { '$set': { 'enabled' : enabled }} )

        return {}, None

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

        if alerts is not None:
            for i,a in enumerate(alerts):
                if a['id'] == alert_id:
                    return a, None

        return None, 'camera {0} alert {1} not found'.format(camera_id, alert_id)

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

        return None, 'camera {0}, alert {1} not found'.format(camera_id, alert_id)

    except:
        return None, 'camera {0} not found'.format(camera_id)

def help():
    print("examples:")
    print("cameras = get_cameras()")
    print("camera = get_camera(24)")
    print("set_camera({'id':24, 'name':'First', 'url': 'rtsp://1.2.3.4:500', 'enabled':True})")
    print("append_camera({'id':24, 'name':'First', 'url': 'rtsp://1.2.3.4:500', 'enabled':True})")
    print("alerts = get_camera_alerts(24)")
    print("set_camera_enabled(24, True)")
    