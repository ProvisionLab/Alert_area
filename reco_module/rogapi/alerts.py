import datetime
import uuid
from rogapi.images import ROG_Image

class ROG_Alert(object):

    def __init__(self, camera_id, alert_type_id):

        self.camera_id = camera_id
        self.alert_type_id = alert_type_id

        self.alert_id = str(uuid.uuid4())

        # <ISO Extended Z timestamp>
        ts = datetime.datetime.utcnow().isoformat()+'Z'
        self.timestamp = ts        

        self.images = []

        self.obj = None # obj to set rog_alert_id value

    def get_data(self):
        
        data = {
            'camera_id': self.camera_id,
            'alert_type_id': self.alert_type_id,
            'timestamp': self.timestamp,
            #'alert_id': self.alert_id,             
        }

        for n, d in self.images:
            data[n] = d.get_data()

        return data

    def set_image(self, name, image):
        
        self.images.append((name, ROG_Image(image)))

class ROG_AlertImage(object):

    def __init__(self, alert_id, image):

        self.alert_id = alert_id
        self.image = ROG_Image(image)

        self.obj = None # obj to get rog_alert_id value

    def get_data(self):
        
        return {
            'alert_id': self.alert_id,
            'image': self.image.get_data()
        }
