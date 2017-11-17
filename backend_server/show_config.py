import bvc_db


cameras = bvc_db.get_cameras()

for c in cameras:
    print (c)
    alerts, err = bvc_db.get_camera_alerts(c['id'])
    for a in alerts:
        print ("   ", a)

