import flask

class EBvcException(Exception):
    
    status_code = 400    

    def to_response(self):
        
        response = flask.jsonify({'error':{ 'status' : self.status_code, 'message' : str(*self.args)}})
        response.status_code = self.status_code
        return response

class EInvalidArgs(EBvcException):
    
    def __init__(self, message:str = 'invalid arguments'):
        super().__init__(message)
        self.status_code = 400
        self.message = message

class ENotFound(EBvcException):
    
    def __init__(self, message: str):
        super().__init__(message)
        self.status_code = 404
        self.message = message

class ECameraNotFound(EBvcException):

    def __init__(self, camera_id):
        super().__init__('camera [%d] not found' % camera_id)
        self.status_code = 404
