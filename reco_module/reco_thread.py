"""
"""
import threading
import traceback
import time
import cv2
from tracker_emu import TrackerEmu
from trk_analyzer2 import TrackAnalyzer2
from PeopleDetector import PeopleDetector
from MotionDetector import MotionDetector
from trk_object import TrackObject
from alert_object import AlertObject
from debug_window import DebugWindow
import reco_config
import tensorflow as tf
from urllib.parse import quote
import logging

# camera: { 'id': int, 'name': str, url': str, 'enabled': bool }

def boxes_to_track_objects(boxes):
    objects = dict([(TrackObject(1+i, (b[1] + b[3]) / 2, b[2], b[3] - b[1], b[2] - b[0]), 1+i) for i, b in enumerate(boxes)])
    return objects

class RecoThread(threading.Thread):
    """
    """

    camera = None
    alert_areas = None

    dbg = None

    connection = None

    thread_count = 0
    bStop = False   # True, if thread gone to exit
    bExit = False   # True, if thread exited

    current_frame = None
    analyzer = None

    @classmethod
    def exist_any_recognition(cls):
        return cls.thread_count > 0

    def __init__(self, connection, camera, areas):
        self.connection = connection
        self.camera = camera
        self.alert_areas = areas

        RecoThread.thread_count += 1

        threading.Thread.__init__(self)

    def stop(self):
        logging.debug("signal to stop camera [%d]", self.camera['id'])
        self.bStop = True

    def on_alert(self, alert: AlertObject, is_enter: bool, pos):
        camera_id = self.camera['id']
        if self.dbg: self.dbg.add_alert(pos, is_enter)

        alert.camera_id = camera_id
        alert.camera_name = self.camera['name']

        logging.debug("new alert: %s", alert)

        alert.set_image(self.current_frame)

        self.connection.post_reco_alert(alert)      

    def update_areas(self, areas):

        #print('############## update_areas #################')

        self.alert_areas = areas

        logging.debug("update_areas: [%d] %s", self.camera['id'], areas)

        if areas is None:
            logging.warning("update areas of camera: [%d] \'%s\', None", self.camera['id'], self.camera['name'])
            return

        logging.info("update areas of camera: [%d] \'%s\', %d areas", self.camera['id'], self.camera['name'], len(areas))

        if self.analyzer:
            self.analyzer.update_areas(areas)

        if self.dbg:
            self.dbg.update_areas(areas)

        pass

    def get_camera_url(self, camera):
        
        camera_url = camera['url']
        return camera_url

        username = camera.get('username')
        password = camera.get('password')
        if username is None or password is None:
            return camera_url

        if camera_url[:7] != 'rtsp://':
            return camera_url

        camera_url = 'rtsp://{0}:{1}@{2}'.format(quote(username), quote(password), camera_url[7:])

        return camera_url

    def run_capture(self, detector, tracker):
        """
        capture of camera loop
        @return: True to restart, False to stop
        """

        camera_id = self.camera['id']
        camera_url = self.get_camera_url(self.camera)

        if not self.alert_areas:
            logging.info("camera %s has no alerts, resetting...", self.camera['name'])
            return False

        # open stream by url
        cap = cv2.VideoCapture(camera_url)
        #fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #print(cap.get(7))
        
        objects = None

        if not cap.isOpened():
            logging.error("camera [%d] \'%s\' not opened", camera_id, self.camera['name'])
            return False

        logging.info('start capture of camera: \'%s\', url: \'%s\'', self.camera['name'], camera_url)
        
        bContinue = False
            
        self.analyzer = TrackAnalyzer2(self.alert_areas)
        self.analyzer.on_alert = self.on_alert

        motion_detector = MotionDetector(int(cap.get(3) * cap.get(4) / 600))

        config = tf.ConfigProto()
        config.gpu_options.per_process_gpu_memory_fraction = 0.7

        frame_id = 0

        # session = tf.Session(config=config, ...)
        with detector.detection_graph.as_default(), \
            tf.Session(graph=detector.detection_graph, config=config) as sess:

            # process stream
            while not self.bStop and cap.isOpened():
                
                if not self.alert_areas:
                    bContinue = False
                    break

                res, frame = cap.read()

                if not res:
                    logging.warning("camera [%d], frame not readed, restarting of capture", camera_id)
                    bContinue = True
                    #continue
                    break

                if res and frame_id % 2 == 0 and motion_detector.isMotion(frame):
                    boxes = detector.process_frame(frame, sess)

                    h, w = frame.shape[:2]
            
                    tracker.objects = boxes_to_track_objects(boxes)
                    objects = list(tracker.objects)
                    self.current_frame = frame
                    self.analyzer.process_objects(w, h, objects)

                if self.dbg and self.dbg.draw_frame(frame, objects):
                    logging.info("stop signal from debug window [%d]", camera_id)
                    bContinue = False
                    break

                frame_id += 1
                pass #while

        del self.analyzer
        cap.release()

        return bContinue

    def run(self):

        camera_id = self.camera['id']

        logging.info('reco thread start: camera [%d] \'%s\'', camera_id, self.camera['name'])

        # setup analyzer
        alert_areas = self.connection.get_camera_alerts(camera_id)

        # no capture if no alerts
        if not alert_areas:
            logging.warning("camera \'%s\' has no alerts configured", self.camera['name'])
            self.bExit = True
            return False

        self.alers_areas = alert_areas

        detector = PeopleDetector()
        tracker = TrackerEmu()

        if reco_config.DEBUG and reco_config.show_dbg_window:
            self.dbg = DebugWindow(self.camera, tracker, self.connection)

        try:

            while self.run_capture(detector, tracker):
                logging.info("restart reco: \'%s\'", self.camera['name'])
                pass
                  
        except:
            logging.exception('exception while capture of camera: %d', camera_id)
            #traceback.print_exc()

        RecoThread.thread_count -= 1

        if self.dbg:
            self.dbg.close()
            del self.dbg

        logging.info('reco thread end: camera [%d], threads left: %d', camera_id, RecoThread.thread_count)

        self.bExit = True
        pass
