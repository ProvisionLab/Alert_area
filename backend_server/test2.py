import bvc_db



cameras = bvc_db.get_cameras()

print(cameras)

camera_id = cameras[2]['id']

alerts = bvc_db.get_camera_alerts(camera_id)

print('alerts: {0}: {1}'.format(camera_id, alerts))
