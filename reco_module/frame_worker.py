import threading
import time
import reco_config
import logging

from MotionDetector import MotionDetector
from PeopleDetector import PeopleDetector
import tensorflow as tf

from trk_analyzer2 import TrackAnalyzer2
from alert_object import AlertObject

if reco_config.show_dbg_window:
    from debug_window import DebugWindow

def boxes_to_track_objects(boxes):
    objects = dict([(TrackObject(1+i, (b[1] + b[3]) / 2, b[2], b[3] - b[1], b[2] - b[0]), 1+i) for i, b in enumerate(boxes)])
    return objects

class FrameWorker(threading.Thread):
    
    thread_count = 0

    dbg = None

    camera = None
    alert_areas = None

    current_frame = None
    analyzer = None

    post_new_alert = None

    bStop = False

    def __init__(self, camera, cap_w, cap_h, post_new_alert):
        
        self.camera = camera
        self.alert_areas = camera['areas']

        self.post_new_alert = post_new_alert

        self.md_min_area = (cap_w * cap_h) / 600
        
        self.frame = None
        self.lock = threading.Condition()

        self.frame_count = 0
        self.frame_count2 = 0
        self.frame_time = time.time()

        FrameWorker.thread_count += 1
        threading.Thread.__init__(self)
        pass

    @classmethod
    def exist_any_worker(cls):
        return cls.thread_count > 0

    def stop(self):
        logging.debug("signal to stop camera [%d] worker", self.camera['id'])
        self.bStop = True

    def process_frame(self, frame):
        """
        add frame to queue
        """
        
        with self.lock:
            self.frame = frame
            self.frame_count += 1
            self.lock.notify()
        pass

    def run(self):
        """
        thread main loop
        """

        camera_id = self.camera['id']
        self.tracker = None

        if reco_config.show_dbg_window:
            self.dbg = DebugWindow(self.camera, self.tracker, self.alert_areas)

        self.analyzer = TrackAnalyzer2(self.alert_areas)
        self.analyzer.on_alert = self.on_alert

        motion_detector = MotionDetector(self.md_min_area)

        detector = PeopleDetector()

        config = tf.ConfigProto()
        config.gpu_options.per_process_gpu_memory_fraction = 0.7

        try:

            with detector.detection_graph.as_default(), \
                tf.Session(graph=detector.detection_graph, config=config) as tf_session:

                while not self.bStop:
                    
                    with self.lock:
                        self.lock.wait(0.1)

                        frame = self.frame
                        self.frame = None

                    if frame is None:
                        continue

                    self.current_frame = frame

                    self.recognize(frame, motion_detector, detector, tf_session)       

                    self.frame_count2 += 1

                    objects = []

                    if self.dbg and self.dbg.draw_frame(frame, objects):
                        logging.info("stop signal from debug window [%d]", camera_id)
                        break

                    self.current_frame = None

                pass # with

        finally:
            FrameWorker.thread_count -= 1            

        if self.dbg:
            self.dbg.close()
            del self.dbg

        pass

    def get_fps(self):
        """
        @return (fps,fps2)  input FPS and output FPS
        """
        
        now = time.time()
        d = now - self.frame_time

        if d < 1.0:
            return 0,0

        fps = self.frame_count / d
        fps2 = self.frame_count2 / d

        self.frame_time = now
        self.frame_count = 0
        self.frame_count2 = 0

        return fps, fps2

    def update_areas(self, areas):
        
        if self.analyzer:
            self.analyzer.update_areas(areas)

        if self.dbg:
            self.dbg.update_areas(areas)
        
        pass

    ##########################################

    def on_alert(self, alert: AlertObject, is_enter: bool, pos):
        camera_id = self.camera['id']
        if self.dbg: self.dbg.add_alert(pos, is_enter)

        alert.camera_id = camera_id
        alert.camera_name = self.camera['name']

        logging.debug("new alert: %s", alert)

        alert.set_image(self.current_frame)

        if self.self.post_new_alert:
            self.post_new_alert(alert)

    def recognize(self, frame, motion_detector, detector, tf_session):
        
        if not motion_detector.isMotion(frame):
            return

        boxes = detector.process_frame(frame, tf_session) if reco_config.enable_detector else []
        
        h, w = frame.shape[:2]
            
        if self.tracker:
            self.tracker.objects = boxes_to_track_objects(boxes)
            objects = list(self.tracker.objects)
        else:
            objects = list(boxes_to_track_objects(boxes))

        self.analyzer.process_objects(w, h, objects)        
    

       