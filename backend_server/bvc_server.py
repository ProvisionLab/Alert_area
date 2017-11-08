from flask import Flask, request
import flask
#from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required, current_identity
import json
import bvc_db
from datetime import timedelta
import bvc_config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_AUTH_URL_RULE'] = '/api/auth'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=360*24*3600)   # 2do: change in future

#####################################################
## JWT implementation

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id

users = [
    User(1, 'reco1', 'reco1passwd'),
    User(2, 'user1', 'qwerty1'),
    User(3, 'user2', 'qwerty2'),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

def authenticate(username, password):
  user = username_table.get(username, None)
  if user and user.password.encode('utf-8') == password.encode('utf-8'):
    return user
  return None

def identity(payload):
  user_id = payload['identity']
  return userid_table.get(user_id, None)

jwt = JWT(app, authenticate, identity)

#####################################################
## Flask api implementation

def error_response(status:int, message:str):

  return flask.Response(
           status=status,
           mimetype="application/json",
           response=json.dumps({'error':{ 'status' : status, 'message' : message}})
           )

@app.errorhandler(404)
def page_not_found(e):
  return error_response(404, "resource not found")

@app.errorhandler(500)
def internal_error(e):
  return error_response(500, "server error")

@app.route('/api/cameras/all/', methods=["GET"])
@jwt_required()
def api_cameras_all_get():
  cameras = bvc_db.get_cameras()
  return flask.jsonify({'cameras':cameras})

@app.route('/api/cameras/<int:camera_id>/', methods=["GET"])
@jwt_required()
def api_camera_get(camera_id:str):

  camera, err = bvc_db.get_camera(camera_id)

  if camera is not None:
    return flask.jsonify({'camera' : camera })
  else:
    return error_response(404, err)#"camera {0} not found".format(camera_id))

@app.route('/api/cameras/<int:camera_id>/alerts/', methods=["GET", "POST"])
@jwt_required()
def api_camera_alerts(camera_id:str):

  if request.method == 'GET':

    alerts, err = bvc_db.get_camera_alerts(camera_id)

    if alerts is None:
      return error_response(404, err)

    return flask.jsonify({ 'alerts' : alerts })

  if request.method == 'POST':

    alert_id, err = bvc_db.append_camera_alert(camera_id, request.get_json())

    if alert_id is None:
      return error_response(404, err)

    return flask.jsonify({ 'alert' : { 'id' : alert_id } })

@app.route('/api/cameras/<int:camera_id>/alerts/<string:alert_id>/', methods=["DELETE", "PUT", "GET"])
@jwt_required()
def api_camera_alert_(camera_id:str, alert_id:str):

  if request.method == 'GET':

    alert, err = bvc_db.get_camera_alert(camera_id, alert_id)

    if alert is None:
      return error_response(404, err)

    return flask.jsonify({'alert' : alert })

  if request.method == 'PUT':

    res, err = bvc_db.update_camera_alert(camera_id, alert_id, request.get_json())

    if res is None:
      return error_response(404, err)

    return flask.jsonify(res)

  if request.method == 'DELETE':

    res, err = bvc_db.delete_camera_alert(camera_id, alert_id)

    if res is None:
      return error_response(404, err)

    return flask.jsonify(res)

@app.route('/api/alerts/', methods=["POST"])
@jwt_required()
def api_alerts():

  data = request.get_json()

  camera_id = data.get('camera_id')
  alert_id = data.get('alert_id')

  if camera_id is None:
    return error_response(400, "invalid arguments")

  if alert_id is None:
    return error_response(400, "invalid arguments")

  print("alert: {0} / {1}".format(camera_id, alert_id))

  return flask.jsonify({})

if __name__ == '__main__':
  app.run(host=bvc_config.api_host, port=bvc_config.api_port)
