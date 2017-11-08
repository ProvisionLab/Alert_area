import datetime
import cv2
import base64

class AlertObject(object):
    
    camera_id = None

    def __init__(self, alert_type: str):
        self.camera_id = None
        self.alert_type = alert_type

        # <ISO Extended Z timestamp>
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        self.timestamp = ts
        self.image = None
        pass
       

    def set_image(self, image):
        
        img = cv2.resize(image, (320,200), interpolation=cv2.INTER_AREA)
        
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, encimg = cv2.imencode('.jpg', img, encode_param)

        if result:
            self.image = str(base64.b64encode(encimg))
        else:
            self.image = None
        pass


    def as_dict(self):

        payload = { 
            'camera_id': self.camera_id, 
            'alert_type_id': self.alert_type, 
            'timestamp': self.timestamp, 
        }

        if self.image:
            payload['image'] = self.image

        return payload

