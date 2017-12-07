import bvc_db

user_id = 22

cameras = bvc_db.get_cameras(user_id)

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

