import bvc_db

cameras = bvc_db.get_cameras()

for camera in cameras:
    camera['name'] = "{0} [{1}]".format(camera['name'], camera['id'])
    bvc_db.append_camera_alert(camera['id'], {
                               'type': 'VW', 'direction': 'B', 'points': [[0.0, 0.5], [1.0, 0.5]]
                               })
