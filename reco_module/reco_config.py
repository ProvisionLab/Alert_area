

reco_name   = 'reco.dev.two'
reco_key    = '0123456789'


DEBUG = False
show_dbg_window = False

# if False, detection is turned off
enable_motion_detector = False
enable_people_detector = True

use_cpu = False

# list of camera names
# to capture all cameras use empty list
filter_cameras = [
#    'Beach',
#    'Ice Rink',
#    'Warehouse',
#    'Office',
#    'Restaurant',
#    'Kiev',
#    'Kiev 2',
#    'Reolink',
#    'Round-About',
#    'Road',
#    'Kennel',
#    'Prospect-North',
#    'Birds Eye',
#    'Dog Play',
#    'Island House',
#    'Bench',
#   'H1',
#   'H2',
#   'H3',
]

#bvcapi_url = 'http://127.0.0.1:5000'
#bvcapi_url = 'http://52.32.99.45:5000'  # BVC Prod
bvcapi_url = 'http://54.69.73.20:5000'  # BVC Dev

bvcapi_key = '0123456789'

update_interval = 60  # seconds
max_alert_queue_size = 50

send_alerts_to_rog = True
send_image_to_sftp = False

send_tb_images = True   # bool: include T-1 and T-2 images into alert
send_ta_images = 4      # int:  count of posts of alerts with T1-T12 images.

# upstream settings

#rogapi_url = 'https://morning-lake-10802.herokuapp.com'
#rogapi_username = 'nabus@test.com'
#rogapi_password = 'password123'

rogapi_url = 'https://rog-api-dev.herokuapp.com'
rogapi_username = 'bvc-dev@gorog.co'
rogapi_password = 'password123!!!'


sftp_host = '54.67.96.88'
sftp_path = 'ftp/bvc/'
sftp_username = 'rog-sftp'
sftp_password = '.4Bk}+3B3'

#sftp_host = '192.168.88.247'
#sftp_username = 'nabus'
#sftp_password = 'nabus28110*'

