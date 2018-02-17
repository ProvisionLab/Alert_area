import bvc_db

from flask import Flask, request, render_template
import flask
from flask_jwt import jwt_required, current_identity
from flask_cors import CORS
import json

import flask.logging

import bvc_config
import bvc_logging, logging

import sys, signal

from bvc_users import BVC_JWT
from reco_dispatcher import RecoDispatcher
from reco_dispatcher2 import RecoDispatcher2

class BVC_Flask(Flask):
    
    def __init__(self):
        
        super().__init__(__name__);
   
        logging.info("BVC server starting")

        self.jwt = BVC_JWT(self)

        self.dispatcher = RecoDispatcher()
        self.dispatcher.on_cameras_update()

        self.dispatcher2 = RecoDispatcher2()

        self.prev_sigint = signal.signal(signal.SIGINT, self.on_signal_int)
        self.prev_sigterm = signal.signal(signal.SIGTERM, self.on_signal_term)

    def on_signal_int(self, signum, taskfrm):

        logging.warning("on_signal_int")

        self.prev_sigint(signum, taskfrm)
        pass
       
    def on_signal_term(self, signum, taskfrm):

        logging.warning("on_signal_term")

        self.dispatcher.stop(False)
        self.dispatcher2.stop(False)

        self.dispatcher.stop()
        self.dispatcher2.stop()

        sys.exit(0)
        #self.prev_sigterm(signum, taskfrm)
        pass

    def on_reco_instance_request(self, reco_id):
        
        i = reco_id.rfind(':')
        if i >= 0:
            instance_id = reco_id[:i]
            process_id = reco_id[i+1:]
        else:
            instance_id = reco_id
            process_id = '0'

        logging.info('on_reco_instance_request, \'%s\', \'%s\'', instance_id, process_id)
        
        pass

app = BVC_Flask()
CORS(app)

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

@app.route('/api/active_cameras', methods=["GET"])
@jwt_required()
def api_cameras_get_enabled():

    logging.debug('get active cameras, %s', current_identity.id)

    if current_identity.id[:5] != 'reco-':
        return error_response(403, "")
        
    reco_id = current_identity.id[5:]

    cameras = app.dispatcher.on_reco_get_cameras(reco_id)

    return flask.jsonify({'cameras': cameras})

@app.route('/api/cameras/<int:camera_id>', methods=["DELETE"])
@jwt_required()
def api_cameras_delete(camera_id):

    logging.info('delete camera: %d', camera_id)

    if not bvc_db.delete_camera(camera_id):
        return error_response(404, "not found")

    app.dispatcher.on_cameras_update()
        
    return flask.jsonify({}), 204


@app.route('/api/user/<int:user_id>/cameras', methods=["GET"])
@jwt_required()
def api_cameras_get_all(user_id:int):

    logging.info('get all cameras, user: %d', user_id)

    cameras = bvc_db.get_cameras(user_id)

    return flask.jsonify({'cameras': cameras})

@app.route('/api/user/<int:user_id>/camera', methods=["POST"])
@jwt_required()
def api_user_new_camera(user_id: int):
    
    logging.info('set all cameras, user: %d', user_id)

    camera = request.get_json()

    logging.debug('request headers: %s', str(request.headers))
    logging.debug('request payload: %s', str(camera))

    if camera is None:
        return error_response(400, "failed")

    if not isinstance(camera,dict):
        return error_response(400, "failed")

    cameras = [camera]
    camera_id = camera.get('camera_id')

    for c in cameras:
        if c.get('enabled'):
            del c['enabled']

    #print("set cameras: ", cameras)

    if not bvc_db.append_cameras(user_id, cameras):
        return error_response(400, "failed")

    app.dispatcher.on_cameras_update()

    return flask.jsonify({}), 201, {'location': '/api/cameras/{}'.format(camera_id)}

@app.route('/api/user/<int:user_id>/cameras', methods=["POST"])
@jwt_required()
def api_user_new_cameras(user_id: int):
    
    logging.info('set all cameras, user: %d', user_id)

    cameras = request.get_json()

    logging.debug('request headers: %s', str(request.headers))
    logging.debug('request payload: %s', str(cameras))

    if cameras is None:
        return error_response(400, "failed")

    if isinstance(cameras,dict):
        cameras = [cameras]

    for c in cameras:
        if c.get('enabled'):
            del c['enabled']

    #print("set cameras: ", cameras)

    if not bvc_db.append_cameras(user_id, cameras):
        return error_response(400, "failed")

    app.dispatcher.on_cameras_update()

    return flask.jsonify({}), 200

@app.route('/api/user/<int:user_id>/cameras', methods=["PUT"])
@jwt_required()
def api_user_put_cameras(user_id: int):

    logging.info('set all cameras, user: %d', user_id)

    cameras = request.get_json()

    logging.debug('request headers: %s', str(request.headers))
    logging.debug('request payload: %s', str(cameras))

    if cameras is None:
        return error_response(400, "failed")

    if isinstance(cameras,dict):
        cameras = [cameras]

    for c in cameras:
        if c.get('enabled'):
            del c['enabled']

    #print("set cameras: ", cameras)

    if not bvc_db.update_cameras(user_id, cameras):
        return error_response(400, "failed")

    app.dispatcher.on_cameras_update()

    return flask.jsonify({}), 204

@app.route('/api/cameras/<int:camera_id>', methods=["GET"])
@app.route('/api/camera/<int:camera_id>', methods=["GET"])
@jwt_required()
def api_camera_get(camera_id: int):

    camera, err = bvc_db.get_camera(camera_id)

    if camera is None:
        logging.error(err)
        return error_response(404, err)#"camera {0} not found".format(camera_id))

    return flask.jsonify({'camera': camera })

@app.route('/api/cameras/<int:camera_id>/enabled', methods=["GET", "PUT"])
@app.route('/api/camera/<int:camera_id>/enabled', methods=["GET", "PUT"])
@jwt_required()
def api_camera_enabled(camera_id: int):

    if request.method == 'GET':
    
        value, err = bvc_db.get_camera_property(camera_id, 'enabled', True)
    
        if value is None:
            logging.error(err)
            return error_response(404, err)

        return flask.jsonify({'value' : value, 'enabled' : value })

    if request.method == 'PUT':

        value = request.get_json().get('value')

        if value is None:
            value = request.get_json().get('value')

        if not isinstance(value,bool):
            return error_response(400, "invalid argument")

        res, err = bvc_db.set_camera_property(camera_id, 'enabled', value)

        if res is None:
            logging.error(err)
            return error_response(404, err)

        logging.info("camera [%d] enabled = %s", camera_id, value)

        app.dispatcher.on_cameras_update()

        return flask.jsonify({}), 204

@app.route('/api/camera/<int:camera_id>/connectedOnce', methods=["GET"])
@jwt_required()
def api_camera_connectedOnce(camera_id: int):

    if request.method == 'GET':
    
        value, err = bvc_db.get_camera_property(camera_id, 'connectedOnce', False)

        if value is None:
            logging.error(err)
            return error_response(404, err)

        return flask.jsonify({'value' : value })

@app.route('/api/cameras/<int:camera_id>/alerts', methods=["GET", "POST", "DELETE"])
@jwt_required()
def api_camera_alerts(camera_id:str):

    if request.method == 'GET':
        
        alerts, err = bvc_db.get_camera_alerts(camera_id)

        if alerts is None:
            logging.error(err)
            return error_response(404, err)

        return flask.jsonify({ 'alerts' : alerts })

    if request.method == 'POST':
        
        alert_id, err = bvc_db.append_camera_alert(camera_id, request.get_json())

        if alert_id is None:
            logging.error(err)
            return error_response(404, err)

        app.dispatcher.on_cameras_update()

        return flask.jsonify({ 'alert' : { 'id' : alert_id } }), 201, {'location': '/api/cameras/{0}/alerts/{1}'.format(camera_id,alert_id)}

    if request.method == 'DELETE':
        
        res, err = bvc_db.delete_camera_alerts(camera_id)

        if res is None:
            logging.error(err)
            return error_response(404, err)

        app.dispatcher.on_cameras_update()

        return flask.jsonify(res), 204
    
@app.route('/api/cameras/<int:camera_id>/alerts/<string:alert_id>', methods=["DELETE", "PUT", "GET"])
@jwt_required()
def api_camera_alert_(camera_id:str, alert_id:str):

    if request.method == 'GET':

        alert, err = bvc_db.get_camera_alert(camera_id, alert_id)

        if alert is None:
            logging.error(err)
            return error_response(404, err)

        return flask.jsonify({'alert' : alert })

    if request.method == 'PUT':
        
        try:

            res, err = bvc_db.update_camera_alert(camera_id, alert_id, request.get_json())

            if res is None:
                logging.error(err)
                return error_response(404, err)

            return flask.jsonify({}), 204

        except Exception as e:
            logging.exception("exce")
            return "exception", 500

    if request.method == 'DELETE':

        res, err = bvc_db.delete_camera_alert(camera_id, alert_id)

        if res is None:
            logging.error(err)
            return error_response(404, err)

        app.dispatcher.on_cameras_update()

        return flask.jsonify({}), 204

@app.route('/api/alerts', methods=["POST"])
@jwt_required()
def api_alerts():

    data = request.get_json()

    camera_id = data.get('camera_id', None)
    if camera_id is None:
        return error_response(400, "invalid arguments")

    alert_type = data.get('alert_type_id')
    if alert_type is None:
        return error_response(400, "invalid arguments")

    logging.info("new alert: camera [%d], type: %s", camera_id, alert_type)

    return flask.jsonify({}), 201

@app.route('/api/rs', methods=["POST"])
@app.route('/api/reco_status', methods=["POST"])
@jwt_required()
def api_reco_status():

    if current_identity.id[:5] != 'reco-':
        return error_response(403, "")
        
    data = request.get_json()

    reco_id = current_identity.id[5:]
    logging.debug("ps: %s %s", reco_id, str(data))

    if reco_id is None:
        return error_response(400, "invalid arguments")

    fps = data.get('fps', 0.0)
    cameras = data.get('cameras', [])

    app.dispatcher.set_reco_status(reco_id, fps, cameras)
    app.dispatcher2.set_reco_status(reco_id, fps, cameras)

    return flask.jsonify({}), 204

@app.route('/status', methods=["GET"])
def get_status():
    
    try:

        return render_template(
            'status.html',
            title='Status',
            status=app.dispatcher.get_status(),
            status2=app.dispatcher2.get_status()
        )

    except Exception as e:
        logging.exception("[EX] /status: ")
        raise

@app.route('/subs', methods=["GET"])
def get_subs():
    
    try:

        return render_template(
            'subs.html',
            title='Subscribes',
            subs=bvc_db.get_subscribes()
        )

    except Exception as e:
        logging.exception("[EX] /subs: ")
        raise

@app.route('/', methods=["GET"])
def get_home():
    
    return "<html>OK<html>", 200

if __name__ == '__main__':
    #app.run(host="127.0.0.1", port=5000)
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)
    #context = ('cert/cert.pem', 'cert/key.pem')
    #app.run(host="0.0.0.0", port=443, threaded=True, ssl_context=context, debug=True)