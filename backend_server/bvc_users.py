from flask_jwt import JWT
import bvc_config
from datetime import timedelta

class User(object):
    
    def __init__(self, id):
        """
        @instance_type maybe 'reco', 'rogt', 'rogs'
        """
        self.id = id
        self.instance_type = id[:4]
        self.instance_name = id[5:]

    def __str__(self):
        return "User(id='%s')" % self.id

def authenticate(username, password):
    
    #print('authenticate {}:{}'.format(username, password))
    
    prefix = username[:5]

    if prefix == 'reco-':
        if bvc_config.reco_key.encode('utf-8') == password.encode('utf-8'):
            return User(username)

    elif prefix == 'rogt-':
        if bvc_config.rogt_key.encode('utf-8') == password.encode('utf-8'):
            return User(username)

    elif username == bvc_config.rogserver_username:
        if bvc_config.rogserver_password.encode('utf-8') == password.encode('utf-8'):
            return User('rogs-1')

    elif username == bvc_config.bvcclient_username:
        if bvc_config.bvcclient_password.encode('utf-8') == password.encode('utf-8'):
            return User('rogt-0')

    else:
        return None

def identity(payload):

    #print('identity {}'.format(payload['identity']))

    user_id = payload['identity']
    return User(user_id)

class BVC_JWT(JWT):
    
    def __init__(self, app):
        
        app.config['SECRET_KEY'] = 'bvc-secret'
        app.config['JWT_AUTH_URL_RULE'] = '/api/auth'
        app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=8760*3600)   # 2do: change in future
        
        super().__init__(app, authenticate, identity)

#jwt = JWT(app, bvc_users.authenticate, bvc_users.identity)
