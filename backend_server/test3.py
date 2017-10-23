import bvc_db



cameras = bvc_db.get_cameras()

print(cameras)

camera_id = cameras[1]['id']

camera = bvc_db.get_camera(camera_id)

print('camera with id {0}: {1}'.format(camera_id, camera))

result = bvc_db.append_camera_alert(camera_id, { 'type' : 'RA', 'points' : [[0.0,0.0],[0.1,0.1]]})

print('result: {0}'.format(result))

alerts = bvc_db.get_camera_alerts(camera_id)

print('alerts: {0}: {1}'.format(camera_id, alerts))
