import threading
import time
import reco_config
import logging

from MotionDetector import MotionDetector
from PeopleDetector import PeopleDetector, PeopleDetector2
import tensorflow as tf

from trk_analyzer2 import TrackAnalyzer2
from trk_object import TrackObject
from alert_object import AlertObject, encode_cvimage, add_box_to_image
from rogapi.alerts import ROG_Alert, ROG_AlertImage

from CameraContext import AlertTAState

if reco_config.show_dbg_window:
    from debug_window import DebugWindow

def get_tf_config(use_cpu: bool):
    
    if use_cpu:
        config = tf.ConfigProto(device_count={'CPU': 1, 'GPU': 0}, allow_soft_placement = False)
    else:
        config = tf.ConfigProto()
            
    #config.gpu_options.per_process_gpu_memory_fraction = 0.1
    config.gpu_options.allow_growth = True
    #config.log_device_placement = True

    return config

def boxes_to_track_objects(boxes):
    objects = dict([(TrackObject(1+i, (b[1] + b[3]) / 2, b[2], b[3] - b[1], b[2] - b[0]), 1+i) for i, b in enumerate(boxes)])
    return objects

class FrameWorker(threading.Thread):
    
    def __init__(self, context):
        
        self.context = context

        self.use_cpu = False

        self.frame = None
        self.lock = threading.Condition()
        
        self.bRunning = True
        super().__init__()
        pass

    def stop(self):
        self.bRunning = False

    def new_frame(self, frame):

        with self.lock:

            self.frame = frame
            self.context.on_new_frame(frame)

            self.lock.notify()

        pass

    def get_fps(self, reset=True):
        
        return self.context.get_fps(reset)

    def set_alert_areas(self, areas):

        with self.lock:
            self.context.set_alert_areas(areas)

        pass

    def run(self):
        
        config = get_tf_config(self.use_cpu)

        self.people_detector = PeopleDetector(config)
        
        with self.people_detector, self.lock:
        
            while self.bRunning:
                
                try:
        
                    if self.frame is None:
                        self.lock.wait(1.0)
                    else:
                        self._process_frame()

                except:
                    logging.exception("exception in FrameWorker.run")

        self.people_detector = None
        pass

    def _process_frame(self):
        
        frame = self.frame
        self.frame = None

        if self.context.preprocess_frame(frame):
            
            self.lock.release()
        
            try:

                objects = self._recognize(frame)

            finally:
                self.lock.acquire()

            self.context.postprocess_frame(frame, objects)

            pass
        
        pass

    def _recognize(self, frame):
        
        boxes = self.people_detector.process_frame2(frame) if reco_config.enable_people_detector else []
            
        objects = list(boxes_to_track_objects(boxes))

        return objects
