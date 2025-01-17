import bvc_db

cameras = [

    {'id':1, 'name':'Airport', 'url':'rtsp://admin:admin@70.182.223.82:554'},
    {'id':2, 'name':'Airport', 'url':'rtsp://admin:admin@216.195.110.44:554'},
    {'id':3, 'name':'Airport', 'url':'rtsp://admin:admin@71.40.113.5:554'},
    {'id':4, 'name':'Auto Garage', 'url':'rtsp://admin:admin@192.206.48.79:554'},
    {'id':5, 'name':'Auto Garage', 'url':'rtsp://admin:admin@70.184.97.36:554'},
    {'id':6, 'name':'Baseball Field', 'url':'rtsp://admin:admin@47.48.201.129:554'},
    {'id':7, 'name':'Beach', 'url':'rtsp://admin:admin@173.165.212.17:554'},
    {'id':8, 'name':'Beach', 'url':'rtsp://admin:admin@98.112.92.120:554'},
    {'id':9, 'name':'Beach', 'url':'rtsp://admin:admin@97.87.252.219:554'},
    {'id':10, 'name':'Beach', 'url':'rtsp://admin:admin@98.112.92.120:8554'},
    {'id':11, 'name':'Beach', 'url':'rtsp://admin:admin@173.163.208.170:554'},
    {'id':12, 'name':'Beach', 'url':'rtsp://admin:admin@173.54.193.242:10554'},
    {'id':13, 'name':'Beach', 'url':'rtsp://admin:admin@65.153.32.6:554'},
    {'id':14, 'name':'Beach', 'url':'rtsp://admin:admin@50.249.92.49:554'},
    {'id':15, 'name':'Beach', 'url':'rtsp://admin:admin@69.85.214.84:10554'},
    {'id':16, 'name':'Construction', 'url':'rtsp://admin:admin@64.191.131.250:554'},
    {'id':17, 'name':'Construction', 'url':'rtsp://admin:admin@207.62.193.3:8554'},
    {'id':18, 'name':'Construction', 'url':'rtsp://admin:admin@207.62.193.8:8554'},
    {'id':19, 'name':'Construction', 'url':'rtsp://admin:admin@207.62.193.4:554'},
    {'id':20, 'name':'Construction', 'url':'rtsp://admin:admin@50.249.90.107:554'},
    {'id':21, 'name':'Construction', 'url':'rtsp://admin:admin@70.233.119.2:554'},
    {'id':22, 'name':'Construction', 'url':'rtsp://admin:admin@166.161.60.172:554'},
    {'id':23, 'name':'Construction', 'url':'rtsp://admin:admin@207.62.193.121:554'},
    {'id':24, 'name':'Construction', 'url':'rtsp://admin:admin@207.62.193.121:8554'},
    {'id':25, 'name':'Construction', 'url':'rtsp://admin:admin@207.62.193.121:554'},
    {'id':26, 'name':'Dog Play', 'url':'rtsp://admin:admin@50.76.197.33:554'},
    {'id':27, 'name':'Dog Play', 'url':'rtsp://admin:admin@98.101.13.90:554'},
    {'id':28, 'name':'Residence', 'url':'rtsp://admin:admin12345@98.189.214.180:52156/Streaming/Channels/402'},
    {'id':29, 'name':'Residence', 'url':'rtsp://admin:admin12345@98.189.214.180:52156/Streaming/Channels/502'},
    {'id':30, 'name':'Residence', 'url':'rtsp://admin:admin12345@98.189.214.180:52156/Streaming/Channels/202'},
    {'id':31, 'name':'Residence', 'url':'rtsp://admin:admin12345@98.189.214.180:52156/Streaming/Channels/102'},
    {'id':32, 'name':'Residence', 'url':'rtsp://admin:admin12345@98.189.214.180:52156/Streaming/Channels/302'},
    {'id':33, 'name':'Residence', 'url':'rtsp://admin:admin12345@98.189.214.180:52156/Streaming/Channels/602'},
    {'id':34, 'name':'Residence', 'url':'rtsp://admin:admin12345@98.189.214.180:52156/Streaming/Channels/702'},
    {'id':35, 'name':'Hospital', 'url':'rtsp://admin:admin@24.176.25.20:554'},
    {'id':36, 'name':'MFR', 'url':'rtsp://admin:admin@96.82.107.45:554'},
    {'id':37, 'name':'MFR', 'url':'rtsp://admin:admin@24.234.190.148:554'},
    {'id':38, 'name':'Residence', 'url':'rtsp://admin:NY5!C2o>ra@107.184.79.88:8154/live/0/h264.sdp'},
    {'id':39, 'name':'Residence', 'url':'rtsp://admin:admin@76.175.137.190:554'},
    {'id':40, 'name':'Residence', 'url':'rtsp://admin:admin@67.174.65.202:554'},
    {'id':41, 'name':'Office', 'url':'rtsp://admin:admin@160.36.130.76:554'},
    {'id':42, 'name':'Office', 'url':'rtsp://admin:admin@174.66.76.39:554'},
    {'id':43, 'name':'Office', 'url':'rtsp://admin:admin@70.62.250.132:554'},
    {'id':44, 'name':'Office', 'url':'rtsp://admin:admin@96.67.33.233:554'},
    {'id':45, 'name':'Office', 'url':'rtsp://admin:admin@50.241.254.153:554'},
    {'id':46, 'name':'Office', 'url':'rtsp://admin:admin@50.102.249.166:554'},
    {'id':47, 'name':'Office', 'url':'rtsp://admin:admin@184.16.238.222:554'},
    {'id':48, 'name':'Office', 'url':'rtsp://admin:admin@50.104.129.238:554'},
    {'id':49, 'name':'Office', 'url':'rtsp://admin:admin@50.102.133.122:554'},
    {'id':50, 'name':'Office', 'url':'rtsp://admin:admin@50.127.79.74:554'},
    {'id':51, 'name':'Office', 'url':'rtsp://admin:admin@174.66.76.41:554'},
    {'id':52, 'name':'Office', 'url':'rtsp://admin:admin@50.121.116.74:554'},
    {'id':53, 'name':'Office', 'url':'rtsp://admin:admin@174.66.76.40:554'},
    {'id':54, 'name':'Office', 'url':'rtsp://admin:admin@50.121.119.66:554'},
    {'id':55, 'name':'Office', 'url':'rtsp://admin:admin@50.102.133.146:554'},
    {'id':56, 'name':'Retail', 'url':'rtsp://admin:admin@173.15.243.254:554'},
    {'id':57, 'name':'Retail', 'url':'rtsp://admin:admin@68.62.191.7:554'},
    {'id':58, 'name':'School', 'url':'rtsp://admin:admin@24.171.185.186:554'},
    {'id':59, 'name':'School', 'url':'rtsp://admin:admin@152.2.228.20:554'},
    {'id':60, 'name':'School', 'url':'rtsp://admin:admin@152.2.228.23:554'},
    {'id':61, 'name':'School', 'url':'rtsp://admin:admin@184.183.3.200:10554'},
    {'id':62, 'name':'School', 'url':'rtsp://admin:admin@152.1.182.21:554'},
    {'id':63, 'name':'School', 'url':'rtsp://admin:admin@209.18.49.78:554'},
    {'id':64, 'name':'Storage Lot', 'url':'rtsp://admin:admin@69.8.37.14:554'},
    {'id':65, 'name':'Tennis Courts', 'url':'rtsp://admin:admin@173.14.73.67:554'},
    {'id':66, 'name':'Utilities', 'url':'rtsp://admin:admin@208.184.123.222:554'},
    {'id':67, 'name':'Utilities', 'url':'rtsp://admin:admin@71.9.159.78:554'},
    {'id':68, 'name':'Utilities', 'url':'rtsp://admin:admin@65.79.195.228:554'},
    {'id':69, 'name':'Warehouse', 'url':'rtsp://admin:admin@23.252.159.40:554'},
    {'id':70, 'name':'Warehouse', 'url':'rtsp://admin:admin@50.27.176.30:554'},
    {'id':71, 'name':'Warehouse', 'url':'rtsp://admin:admin@64.126.161.165:554'},
]

bvc_db.drop()

for camera in cameras:
    camera['name'] = "{0} [{1}]".format(camera['name'], camera['id'])
    camera['enabled'] = False
    bvc_db.append_camera(camera)
    bvc_db.append_camera_alert(camera['id'], {'type': 'VW', 'direction': 'B', 'points': [[0.0, 0.5], [1.0, 0.5]]})
