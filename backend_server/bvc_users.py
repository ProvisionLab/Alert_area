import bvc_config

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id

users = [
    User(1, 'reco1', 'reco1passwd'),                    # recognizer uses this to auth
    User(2, bvc_config.bvcclient_username, bvc_config.bvcclient_password),   # BvcClient uses this to auth
    User(3, 'user2', 'qwerty2'),
]
