import requests
import json

use_dev = False

#########################################################

if use_dev:

    rogapi_url='https://rog-api-dev.herokuapp.com'      # dev-server
    rogapi_username = 'bvc-dev@gorog.co'
    rogapi_password = 'password123!!!'

    #bvcapi_url = 'http://localhost:5000'
    bvcapi_url = 'https://dev.gorog.co'  # BVC Dev Server
    bvc_verify_ssl=True

    bvcapi_username = 'rogt-2'
    bvcapi_password = 'qwerty1'

    reco_username = 'reco-1'
    reco_password = '0123456789'

else:
    
    rogapi_url = 'https://rog-api-prod.herokuapp.com'   # prod-server
    rogapi_username = 'bvc-prod@gorog.co'
    rogapi_password = 'q5y2nib,+g!P8zJ+'

    bvcapi_url = 'https://production.gorog.co'  # BVC Prod
    bvc_verify_ssl=True

    bvcapi_username = 'rogt-2'
    bvcapi_password = 'qwerty1'

    reco_username = 'reco-1'
    reco_password = '0123456789'

#########################################################

session = requests.Session()
session.verify = bvc_verify_ssl

#########################################################

def enable_camera(camera_id:int, value:bool):
    
    # auth

    r = session.post('{}/api/auth'.format(bvcapi_url), 
        json={'username': bvcapi_username,'password': bvcapi_password})

    if r.status_code != 200:
        print('auth failed')
        return False

    jwt_token = r.json()['access_token']


    # set enabled

    r = session.put('{0}/api/cameras/{1}/enabled'.format(bvcapi_url, camera_id),
        headers = {'Authorization': 'JWT {0}'.format(jwt_token) },
        json={'enabled':value})

    if r.status_code != 200:
        print('set_enabled failed', r.status_code, r.text)
        return False

    print('succeeded')
    return True    


def get_camera(camera_id:int):
    
    # auth

    r = session.post('{}/api/auth'.format(bvcapi_url), 
        json={'username': bvcapi_username,'password': bvcapi_password})

    if r.status_code != 200:
        print('auth failed')
        return False

    jwt_token = r.json()['access_token']


    # set enabled

    r = session.get('{0}/api/cameras/{1}'.format(bvcapi_url, camera_id),
        headers = {'Authorization': 'JWT {0}'.format(jwt_token) })

    if r.status_code != 200:
        print('get_camera failed', r.status_code, r.text)
        return False

    print('succeeded')
    return r.json()   


if __name__ == '__main__':
    
    print("api url: \'{}\'".format(bvcapi_url))

    enable_camera(8, True)
    #print(get_camera(226))
 
   