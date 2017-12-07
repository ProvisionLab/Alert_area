import datetime
import uuid
import cv2
import base64
import rog_sftp
import reco_config
from trk_object import TrackObject

image_index = 0

def encode_cvimage(image):
    
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, encimg = cv2.imencode('.jpg', image, encode_param)

    if result:
        return encimg
    else:
        return None

def convert_image(image, prefix: str, id: str):

    if image is None:
        return None

    if reco_config.send_image_to_sftp:
        
        #print(prefix, image)

        data = encode_cvimage(image)
        fname = prefix + '_'+ id + '.jpg'
        
        if rog_sftp.sftp_upload(reco_config.sftp_path + fname, data):
            return fname
        else:
            return None

    else:

        image = cv2.resize(image, (320,200), interpolation=cv2.INTER_AREA)
        data = encode_cvimage(image)

        if data is not None:
            return str(base64.b64encode(data))
        else:
            return None
        pass
    pass

class AlertObject(object):
    
    camera_id = None
    camera_name = None

    cvimages = None     # list of (prefix, image)

    def __init__(self, camera_id: int, alert_id: str, alert_type: str):
        """
        @alert_id   unique alert id, if None then generated
        """
        self.camera_id = camera_id
        self.alert_id = alert_id if alert_id else str(uuid.uuid4())
        self.alert_type = alert_type

        # <ISO Extended Z timestamp>
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        self.timestamp = ts
        self.images = []

        self.cvimages = []
        pass

    def encode_images(self):
        
        self.images = []
        
        for prefix, image in self.cvimages:
            name = convert_image(image, prefix, self.alert_id)
            if name:
                self.images.append(name)

    def set_image(self, prefix: str, image, box = None):
        
        if image is not None:
            
            if isinstance(box, TrackObject):
                image = image.copy()
                cv2.rectangle(image, (int(box.x1),int(box.y1)), (int(box.x2),int(box.y2)), (0,0,255), thickness=2);
                #global image_index
                #image_index += 1
                #cv2.imwrite("image_{0}_{1:04d}.jpg".format(prefix, image_index), image)
                
            self.cvimages.append((prefix, image))            

        pass

    def as_dict(self):
        
        if self.alert_type:

            payload = { 
                'camera_id': self.camera_id, 
                'alert_id': self.alert_id, 
                'alert_type_id': self.alert_type, 
                'timestamp': self.timestamp, 
            }

        else:
            
            payload = { 
                'alert_id': self.alert_id, 
            }

        if reco_config.send_tb_images or reco_config.send_ta_images > 0:
            payload['images'] = self.images
        elif len(self.images) == 1:
            payload['image'] = self.images[0]
        else:
            payload['image'] = 'noimage'

        return payload
