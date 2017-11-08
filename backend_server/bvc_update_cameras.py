import requests
import bvc_db
import bvc_config


def is_request_succeeded(r):
    return r.status_code == 200 or r.status_code == 201

def do_auth(username, password):
    r = requests.post('{0}/api/v2/sessions'.format(bvc_config.usapi_url),
                        json={'session': {'email': username, 'password': password}})

    if not is_request_succeeded(r):
        print('auth failed: ', r.status_code)
        return None

    auth = r.json()
    print('user: ', auth['user']['email'])
    return auth['jwt']

def get_cameras(jwt_token):
    
    r = requests.get('{0}/api/v2/me/cameras'.format(bvc_config.usapi_url),
                        headers={'Authorization': '{0}'.format(jwt_token)})

    if not is_request_succeeded(r):
        print('auth failed: ', r.status_code)
        return None
    
    return r.json()['data']
    
def update_cameras():
    jwt_token = do_auth(bvc_config.usapi_username, bvc_config.usapi_password)

    if jwt_token is None:
        print('cameras updating failed')
        return

    cameras = get_cameras(jwt_token)

    if cameras is None:
        print('cameras updating failed')
        return
        
    bvc_db.update_cameras([{'id': c['id'], 'name': c['name'], 'url': c['rtspUrl']} for c in cameras]) 
  

if __name__ == '__main__':

    bvc_db.delete_empty_cameras()

    #for c in bvc_db.get_cameras():
    #    print(c)

    update_cameras();    

    #for c in bvc_db.get_cameras():
    #    print(c)

    pass
