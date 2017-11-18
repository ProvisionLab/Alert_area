import bvc_db


cameras = bvc_db.get_cameras()

for c in cameras:

    print (c)

    alerts, err = bvc_db.get_camera_alerts(c['id'])

    if alerts is None:
        print("   alerts: None, ", err)
        continue

    if not alerts:
        print("   alerts: ", alerts)
        continue

    for a in alerts:
        print ("   ", a)

