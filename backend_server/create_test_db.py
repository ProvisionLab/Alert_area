import bvc_db

cameras = [
    { 
      'id' : 1,
      'name' : 'Beach',
      'url' : 'rtsp://98.112.92.120:554',
    },
    { 
      'id' : 2,
      'name' : 'Ice Rink', 
      'url' : 'rtsp://12.110.253.194:554'
    },
    { 
      'id' : 3,
      'name' : 'Warehouse',
      'url' : 'rtsp://140.237.176.132:554'
    },
    { 
      'id' : 3,
      'name' : 'Office',
      'url' : 'rtsp://221.205.18.188:554'
    },
    { 
      'id' : 5,
      'name' : 'Restaurant',
      'url' : 'rtsp://5.43.115.237:554'
    },
    { 
      'id' : 6,
      'name' : 'Kiev',
      'url' : 'rtsp://91.233.111.24:554'
    },
]

bvc_db.drop()

for camera in cameras:
  bvc_db.append_camera(camera)
