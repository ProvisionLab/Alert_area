import datetime
import uuid
import cv2
import base64
import rog_sftp
import reco_config


def encode_cvimage(image):
    
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, encimg = cv2.imencode('.jpg', image, encode_param)

    if result:
        return encimg
    else:
        return None

class AlertObject(object):
    
    camera_id = None
    camera_name = None

    cvimage = None

    def __init__(self, alert_type: str):
        self.camera_id = None
        self.alert_type = alert_type

        # <ISO Extended Z timestamp>
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        self.timestamp = ts
        self.image = None
        pass

    def encode_image(self):

        image = self.cvimage

        if image is None:
            self.image = 'nofile'
            return

        if reco_config.send_image_to_sftp:
            
            data = encode_cvimage(image)
            fname = str(uuid.uuid4()) + '.jpg'
            
            if rog_sftp.sftp_upload(reco_config.sftp_path + fname, data):
                self.image = fname

        else:

            image = cv2.resize(image, (320,200), interpolation=cv2.INTER_AREA)
            data = encode_cvimage(image)

            if data is not None:
                self.image = str(base64.b64encode(data))
            else:
                self.image = None
            pass
       
    def set_image(self, image):
        
        self.cvimage = image
        


    def as_dict(self):

        payload = { 
            'camera_id': self.camera_id, 
            'alert_type_id': self.alert_type, 
            'timestamp': self.timestamp, 
        }

        if self.image:
            payload['image'] = self.image

        return payload

