import bvc_db


cameras = bvc_db.get_cameras()

for c in cameras:
    print (c)

    alerts, err = bvc_db.get_camera_alerts(c['id'])
    if err or alerts is None:
        print("   alerts: None")
        continue

    for a in alerts:
        print ("   ", a)

