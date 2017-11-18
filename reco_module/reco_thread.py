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

# camera: { 'id' : str, 'url' : str }


def inc(id):
    id += 1
    return id

def boxes_to_track_objects(boxes):
    id = 0
    objects = dict([(TrackObject(id, (b[1] + b[3]) / 2, b[2], b[3] - b[1], b[2] - b[0]), inc(id)) for b in boxes])
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
        self.bStop = True

    def on_alert(self, alert: AlertObject, is_enter: bool, pos):
        camera_id = self.camera['id']
        if self.dbg: self.dbg.add_alert(pos, is_enter)

        alert.camera_id = camera_id
        alert.camera_name = self.camera['name']

        alert.set_image(self.current_frame)

        self.connection.post_reco_alert(alert)      

    def update_areas(self, areas):

        #print('############## update_areas #################')

        self.alert_areas = areas

        print("update_areas: {0} {1}".format(self.camera["id"], areas))

        if areas is None:
            return

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

    # return: True to continue, False to stop
    def run_capture(self, detector, tracker):

        camera_id = self.camera['id']
        camera_url = self.get_camera_url(self.camera)

        if not self.alert_areas:
            print("camera {0} has no alerts, resetting...".format(self.camera['name']))
            return False

        # open stream by url
        cap = cv2.VideoCapture(camera_url)
        #fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #print(cap.get(7))
        
        objects = None

        if not cap.isOpened():
            print("camera {0} not opened".format(self.camera['name']))
            return False

        print('start capture: \'{0}\' {1}'.format(self.camera['name'], self.camera['url']))
        
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
                    bContinue = False
                    break

                frame_id += 1
                pass #while

        del self.analyzer
        cap.release()

        return bContinue

    def run(self):

        camera_id = self.camera['id']

        print('start reco: \'{0}\''.format(self.camera['name']))

        # setup analyzer
        alert_areas = self.connection.get_camera_alerts(camera_id)

        # no capture if no alerts
        if not alert_areas:
            print("camera {0} has no alerts configured".format(self.camera['name']))
            self.bExit = True
            return False

        self.alers_areas = alert_areas

        detector = PeopleDetector()
        tracker = TrackerEmu()

        if reco_config.DEBUG:
            self.dbg = DebugWindow(self.camera, tracker, self.connection)

        try:

            while self.run_capture(detector, tracker):
                print("restart reco: \'{0}\'".format(self.camera['name']))
                pass
                  
        except:
            print('exception: {0}'.format(self.camera['id']))
            traceback.print_exc()

        RecoThread.thread_count -= 1

        if self.dbg:
            self.dbg.close()
            del self.dbg

        print('end: {0}, threads: {1}'.format(self.camera['id'], RecoThread.thread_count))

        self.bExit = True
        pass
