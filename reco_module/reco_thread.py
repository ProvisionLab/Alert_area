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

    dbg = None

    connection = None

    thread_count = 0
    bStop = False

    current_frame = None
    analyzer = None

    @classmethod
    def stop_recognition(cls):
        cls.bStop = True

    @classmethod
    def exist_any_recognition(cls):
        return cls.thread_count > 0

    def __init__(self, connection, camera):
        self.connection = connection
        self.camera = camera

        RecoThread.thread_count += 1

        threading.Thread.__init__(self)

    def on_alert(self, alert: AlertObject, is_enter: bool, pos):
        camera_id = self.camera['id']
        if self.dbg: self.dbg.add_alert(pos, is_enter)

        #self.connection.post_reco_alert(camera_id, alert_id)  
        alert.camera_id = camera_id

        alert.set_image(self.current_frame)

        self.connection.post_reco_alert(alert)      

    def update_areas(self, areas):

        #print('############## update_areas #################')

        if self.analyzer:
            self.analyzer.update_areas(areas)

        if self.dbg:
            self.dbg.update_areas(areas)
        pass

    def get_camera_url(self, camera):
        
        camera_url = camera['url']

        username = camera.get('username')
        password = camera.get('password')
        if username is None or password is None:
            return camera_url

        if camera_url[:7] != 'rtsp://':
            return camera_url

        camera_url = 'rtsp://{0}:{1}@{2}'.format(quote(username), quote(password), camera_url[7:])

        return camera_url


    def run(self):

        print('start reco: \'{0}\', {1}'.format(self.camera['name'], self.camera['url']))

        # open stream by url
        camera_url = self.get_camera_url(self.camera)
        camera_id = self.camera['id']

        detector = PeopleDetector()
        tracker = TrackerEmu()

        if reco_config.DEBUG:
            self.dbg = DebugWindow(self.camera, tracker, self.connection)

        try:
            cap = cv2.VideoCapture(camera_url)
            #fourcc = cv2.VideoWriter_fourcc(*'XVID')
            #print(cap.get(7))
            objects = None

            if cap.isOpened():
                
                # setup analyzer
                alert_areas = self.connection.get_camera_alerts(camera_id)
                self.analyzer = TrackAnalyzer2(alert_areas)
                self.analyzer.on_alert = self.on_alert

                motion_detector = MotionDetector(int(cap.get(3) * cap.get(4) / 600))
                frame_id = 0
                config = tf.ConfigProto()
                config.gpu_options.per_process_gpu_memory_fraction = 0.7
                # session = tf.Session(config=config, ...)
                with detector.detection_graph.as_default():
                    with tf.Session(graph=detector.detection_graph, config=config) as sess:
                        # process stream
                        while not RecoThread.bStop and cap.isOpened():

                            res, frame = cap.read()

                            if not res:
                                continue

                            if res and frame_id % 2 == 0 and motion_detector.isMotion(frame):
                                boxes = detector.process_frame(frame, sess)

                                h, w = frame.shape[:2]
                        
                                tracker.objects = boxes_to_track_objects(boxes)
                                objects = list(tracker.objects)
                                self.current_frame = frame
                                self.analyzer.process_objects(w, h, objects)

                            if self.dbg and self.dbg.draw_frame(frame, objects):
                                       break
                            frame_id += 1
                            pass #while

            cap.release()

        except:
            print('exception: {0}'.format(camera_id))
            traceback.print_exc()

        RecoThread.thread_count -= 1

        if self.dbg:
            del self.dbg

        print('end: {0}, threads: {1}'.format(camera_id, RecoThread.thread_count))
        pass
