import datetime
import uuid
import cv2
import base64
import rog_sftp
import reco_config
from trk_object import TrackObject
import logging

image_index = 0


alert_type_names = {
    "RA": "Entering Restricted Area",
    "LD": "Loitering Detected",
    "VW": "Entry Detected"
}

alert_type_ids = None

def set_alert_type_ids(data):
    
    global alert_type_ids

    if data is None:
        alert_type_ids = {
            "RA" : 11,
            "VW" : 5,
            "LD" : 49,
        }
        return

    alert_type_ids = {}
    for i in data:
        for k in ['RA', 'LD', 'VW']:
            if i['name'] == alert_type_names[k]:
                alert_type_ids[k] = i['id']
        

    logging.info('set_alert_type_ids: %s', str(alert_type_ids))
    pass

def get_alert_type_id(alert_type):

    if alert_type_ids:
        return alert_type_ids.get(alert_type, 0)
    else:
        return 0
            

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

        #image = cv2.resize(image, (320,200), interpolation=cv2.INTER_AREA)
        data = encode_cvimage(image)

        if data is not None:
            return str(base64.b64encode(data))
        else:
            return None
        pass
    pass


def add_box_to_image(image, box):
    
    if isinstance(box, TrackObject):

        image = image.copy()

        cv2.rectangle(image, (int(box.x1),int(box.y1)), (int(box.x2),int(box.y2)), (0,0,255), thickness=2);
        #global image_index
        #image_index += 1
        #cv2.imwrite("image_{0}_{1:04d}.jpg".format(prefix, image_index), image)

        return image

    else:
       
        return image
        
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
        self.alert_type_id = get_alert_type_id(self.alert_type)

        self.alert_ta = None
        self.rog_alert_id = None

        # <ISO Extended Z timestamp>
        ts = datetime.datetime.utcnow().isoformat()+'Z'

        self.timestamp = ts
        self.images = []

        self.cvimages = []
        pass

    def encode_images(self):
        
        self.images = []
        
        for prefix, image in self.cvimages:
            data = convert_image(image, prefix, self.alert_id)
            if data:
                if prefix=='T-2':
                    self.images.append(("image_1", data))
                elif prefix=='T-1':
                    self.images.append(("image_2", data))
                elif prefix=='T':
                    self.images.append(("image_3", data))
                else:
                    self.images.append(("image", data))

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
                'alert_type_id': self.alert_type_id,
                'timestamp': self.timestamp, 
            }

        else:
            
            payload = { 
                'alert_id': self.alert_id, 
            }

        if reco_config.send_tb_images or reco_config.send_ta_images > 0:
            
            for n, d in self.images:
                payload[n] = d

        elif len(self.images) == 1:
            payload[self.images[0][0]] = self.images[0][1]

        return payload

    def as_debug(self):

        d = self.as_dict()

        for k,v in d.items():
            if k[:5] == 'image' and v is not None:
                if isinstance(v,str):
                    d[k] = v[:32]
                
        return d
