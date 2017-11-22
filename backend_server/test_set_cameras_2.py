import bvc_db

cameras = [
    {
        "id": 476, "name": "Island House", 
        "url": "rtsp://admin:admin@173.163.208.170:554"
    }, 
    {
        "id": 477, "name": "Pathway", 
        "url": "rtsp://admin:admin@65.153.32.6:554"
    }, 
    {
        "id": 478, "name": "Road", 
        "url": "rtsp://admin:admin@50.249.92.49:554"
    },
    {
        "id": 479, "name": "Tarmac", 
        "url": "rtsp://admin:admin@70.182.223.82:554"
    }, 
    {
        "id": 480, "name": "Terminal", 
        "url": "rtsp://admin:admin@216.195.110.44:554"
    }, 
    {
        "id": 481, "name": "Birds Eye", 
        "url": "rtsp://admin:admin@64.191.131.250:554"
    }, 
    {
        "id": 483, "name": "Bldg 1 - West", 
        "url": "rtsp://admin:admin@207.62.193.8:8554"
    },
    {
        "id": 484, "name": "Bldg 2 - Ground", 
        "url": "rtsp://admin:admin@207.62.193.4:554"
    }, 
    {
        "id": 485, "name": "Gravel Storage", 
        "url": "rtsp://admin:admin@50.249.90.107:554"
    }, 
    {
        "id": 486, "name": "Round-About", 
        "url": "rtsp://admin:admin@70.233.119.2:554"
    }, 
    {
        "id": 487, "name": "Dog Play", 
        "url": "rtsp://admin:admin@50.76.197.33:554"
    }, 
    {
        "id": 489, "name": "Backyard", 
        "url": "rtsp://admin:0ilChange@107.184.56.7:5542/11"
    }, 
    {
        "id": 506, "name": "Sea Gem Cottage Driveway", 
        "url": "rtsp://root:neil1000@seagem.homeftp.net:554/axis-media/media.amp?stream=2"
    },
    {
        "id": 491, "name": "Dining Room", 
        "url": "rtsp://admin:0ilChange@107.184.56.7:5541/11"
    },
    {
        "id": 475, "name": "Boardwalk", 
        "url": "rtsp://admin:admin@97.87.252.219:554"
    },
    {
        "id": 474, "name": "Bench", 
        "url": "rtsp://admin:admin@98.112.92.120:554"
    },
    {
        "id": 488, "name": "Kennel", 
        "url": "rtsp://admin:admin@98.101.13.90:554"
    },
    {
        "id": 482, "name": "Bldg 1 - Overhead", 
        "url": "rtsp://admin:admin@207.62.193.3:8554"
    },
    {
        "id": 493, "name": "Prospect - North", 
        "url": "rtsp://admin:0ilChange@107.184.56.7:5544"
    },
    {
        "id": 490, "name": "Basement Door",
        "url": "rtsp://admin:0ilChange@107.184.56.7:5547"
    }
]

bvc_db.drop()

for camera in cameras:
    bvc_db.append_camera(camera)
