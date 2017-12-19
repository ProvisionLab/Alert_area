import bvc_db

user_id = 22

cameras = bvc_db.get_cameras(user_id)


# import bvc_db
# from bvc_db import db
# users = [u for u in db.users.find({})]
# db.users.update_one({'uid': uid}, { '$set': { 'cameras' : u_cameras }})
# u_cameras = [648, 647, 649, 645, 646, 650, 652, 651]
#

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

