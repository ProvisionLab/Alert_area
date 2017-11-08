

DEBUG = True

# list of camera names
# to capture all cameras use empty list
cameras = [
#    'Beach',
    'Ice Rink',
#    'Warehouse',
#    'Office',
#    'Restaurant',
#    'Kiev'
]

api_url = 'http://localhost:5000/'

update_areas_interval = 60  # seconds

send_alerts_to_rog = True
send_image_to_sftp = True

# upstream settings

usapi_url = 'https://morning-lake-10802.herokuapp.com'
usapi_username = 'nabus@test.com'
usapi_password = 'password123'

sftp_host = '54.67.96.88'
sftp_path = 'ftp/bvc/'
sftp_username = 'rog-sftp'
sftp_password = '.4Bk}+3B3'

#sftp_host = '192.168.88.247'
#sftp_username = 'nabus'
#sftp_password = 'nabus28110*'
