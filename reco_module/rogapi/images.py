import base64

class ROG_Image(object):
    
    def __init__(self, image):

        self.data = str(base64.b64encode(image), "utf-8")

    def get_data(self):

        return self.data
