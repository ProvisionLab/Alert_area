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

def encode_cvimage2(image, prefix):

    if image is None:
        return None

    if reco_config.send_image_to_sftp:
        
        #print(prefix, image)
        
        data = encode_cvimage(image)
        fname = prefix + str(uuid.uuid4()) + '.jpg'
        
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

    cvimage = None
    cvimage1 = None
    cvimage2 = None

    def __init__(self, alert_type: str):
        self.camera_id = None
        self.alert_type = alert_type

        # <ISO Extended Z timestamp>
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        self.timestamp = ts
        self.image = None
        pass


    def encode_image(self):

        self.image = encode_cvimage2(self.cvimage, "T_")

        if self.image:
            self.image1 = encode_cvimage2(self.cvimage1, "T-1_")
            self.image2 = encode_cvimage2(self.cvimage2, "T-2_")
        else:
            self.image1 = None
            self.image2 = None

    def set_image(self, image, box: TrackObject):
        
        if image is not None and isinstance(box, TrackObject):
            image = image.copy()
            cv2.rectangle(image, (int(box.x1),int(box.y1)), (int(box.x2),int(box.y2)), (0,0,255), thickness=2);
            #global image_index
            #image_index += 1
            #cv2.imwrite("image{0:04d}.jpg".format(image_index), image)
        
        self.cvimage = image

    def set_image1(self, image):
        self.cvimage1 = image

    def set_image2(self, image):
        self.cvimage2 = image
        
    def as_dict(self):

        images = []

        if self.image:
            images.append(self.image)

        if self.image1:
            images.append(self.image1)

        if self.image2:
            images.append(self.image2)
        

        payload = { 
            'camera_id': self.camera_id, 
            'alert_type_id': self.alert_type, 
            'timestamp': self.timestamp, 
#            'image' : self.image if self.image else "noimage"
            'images' : images
        }

        return payload
