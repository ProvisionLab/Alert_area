import bvc_db

cameras = [
 { 
   'name' : 'camera_01',
   'url' : 'rtsp://184.72.239.149/vod/mp4:BigBuckBunny_115k.mov',
   'alerts' : [ 
		{ 'type' : 'LD', 'duration' : 10, 'points' : [[0.1,0.1],[0.5,0.1],[0.3,0.4]] },
		{ 'type' : 'RA', 'points' : [[0.3,0.2],[0.8,0.2],[0.4,0.6]] },
		{ 'type' : 'VW', 'direction' : 'L', 'points' : [[0.9,0.3],[0.9,0.5]] }
	]
 },
 { 
   'name' : 'camera_02', 
   'url' : 'rtsp://184.72.239.149/vod/mp4:BigBuckBunny_115k.mov'
 },
 { 
   'name' : 'camera_03',
   'url' : 'rtsp://184.72.239.149/vod/mp4:BigBuckBunny_115k.mov'
 },
 { 
   'name' : 'camera_04', 
   'url' : 'rtsp://184.72.239.149/vod/mp4:BigBuckBunny_115k.mov'
 },
]


bvc_db.drop()

for camera in cameras:
  bvc_db.append_camera(camera)

