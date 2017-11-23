import bvc_db

cameras = [
    {"id":537,"name":"H1","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"id":538,"name":"H2","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"id":539,"name":"H3","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"id":540,"name":"H4","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"id":541,"name":"H5","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"id":542,"name":"H6","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":543,"name":"H7","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":544,"name":"H8","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":545,"name":"H9","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":546,"name":"H10","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":547,"name":"H11","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":548,"name":"H12","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":549,"name":"H13","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":550,"name":"H14","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":551,"name":"H15","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":552,"name":"H16","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":553,"name":"H17","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":554,"name":"H18","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":556,"name":"H20","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":555,"name":"H19","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":561,"name":"H25","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":557,"name":"H21","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":558,"name":"H22","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":559,"name":"H23","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":560,"name":"H24","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":563,"name":"H27","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":564,"name":"H28","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":562,"name":"H26","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":565,"name":"H29","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":566,"name":"H30","url":"rtsp://admin:admin@98.112.92.120:554"},
    {"enabled":False,"id":567,"name":"H31","url":"rtsp://admin:admin@98.112.92.120:554"},
]

bvc_db.drop()

for camera in cameras:
    camera['name'] = "{0} [{1}]".format(camera['name'], camera['id'])
    bvc_db.append_camera(camera)
    bvc_db.append_camera_alert(camera['id'], {
                               'type': 'VW', 'direction': 'B', 'points': [[0.0, 0.5], [1.0, 0.5]]
                               })
