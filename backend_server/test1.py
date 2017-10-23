import bvc_db



cameras = bvc_db.get_cameras()

print(cameras)

camera_id = cameras[0]['id']

camera = bvc_db.get_camera(camera_id)

print('camera with id {0}: {1}'.format(camera_id, camera))


camera = bvc_db.get_camera("111111111111111111111111")

print('camera with id {0}: {1}'.format(camera_id, camera))

alerts = bvc_db.get_camera_alerts(camera_id)

print('alerts: {0}: {1}'.format(camera_id, alerts))
