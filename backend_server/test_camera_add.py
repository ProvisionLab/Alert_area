import bvc_db

bvc_db.append_camera(
{ 
  'id' : 6,
  'name' : 'Kiev 2',
  'url' : 'rtsp://91.233.111.24:554'
})

cameras = bvc_db.get_cameras()

for c in cameras:
    print("camera: {0} {1}".format(c['id'], c['name']))
