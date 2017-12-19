import threading
import time
import reco_config
import logging

from MotionDetector import MotionDetector
from PeopleDetector import PeopleDetector, PeopleDetector2
import tensorflow as tf

from trk_analyzer2 import TrackAnalyzer2
from trk_object import TrackObject
from alert_object import AlertObject

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

class AlertTAState(object):
    """
    contains state of alert for 12 sec after alert creation
    """

    def __init__(self, camera_id: int, alert_id: str):
        
        self.camera_id = camera_id
        self.alert_id = alert_id

        self.timestamp = time.time()

        self.count = 0

    pass

class FrameWorker(threading.Thread):
    
    thread_count = 0

    dbg = None

    camera = None
    alert_areas = None

    current_frame = None
    analyzer = None

    post_new_alert = None

    bStop = False

    frame = None        # current frame
    frame_time = None

    frame1 = None       # frame T-1
    frame2 = None       # frame T-2

    alerts_ta = None    # list of AlertTAState. 

    use_cpu = reco_config.use_cpu

    def __init__(self, camera, cap_w, cap_h, post_new_alert):
        
        self.camera = camera
        self.alert_areas = camera['areas']

        self.post_new_alert = post_new_alert

        self.md_min_area = (cap_w * cap_h) / 600
        
        self.lock = threading.Condition()

        self.frames1 = []
        self.frames2 = []
        
        self.frame = None

        self.frame_count = 0
        self.frame_count2 = 0
        self.frame_time = time.time()

        self.alerts_ta = []

        FrameWorker.thread_count += 1
        super().__init__()
        pass

    @classmethod
    def exist_any_worker(cls):
        return cls.thread_count > 0

    def stop(self):
        logging.debug("signal to stop camera [%d] worker", self.camera['id'])
        self.bStop = True

    def _process_ta_frames(self, frame):
        
        now = time.time()

        new_list = []

        for ta in self.alerts_ta:

            d = now - ta.timestamp
            n = int(d)

            #print("1 {0} {1}, time: T{2:.2f}, n: {3}".format(ta.alert_id, ta.count, d, n))

            if n <= reco_config.send_ta_images and n > ta.count:
                self._on_ta_alert(ta.alert_id, "T{0}".format(n), frame)
                ta.count = n

            if n < reco_config.send_ta_images:
                new_list.append(ta)
                
            pass

        self.alerts_ta = new_list

        #for ta in self.alerts_ta:
        #    print("2 {0} T{1}".format(ta.alert_id, ta.count))

        pass

    def process_frame(self, frame):
        """
        add frame to queue
        """
        
        with self.lock:

            now = time.time()

            self.frame = frame
            self.frame_count += 1

            self.frames1.append((frame, now))

            while len(self.frames1) > 0:
                _,t = self.frames1[0]
                if (now-t) > 1.0:
                    self.frames2.append(self.frames1.pop(0))
                else:
                    break

            while len(self.frames2) > 0:
                _,t = self.frames2[0]
                if (now-t) > 2.0:
                    self.frames2.pop(0)
                else:
                    break

            if self.alerts_ta:
                self._process_ta_frames(frame)
                pass                

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

        try:

            config = get_tf_config(self.use_cpu)

            if reco_config.use_cpu:

                logging.info("configure detector for CPU")
                with tf.device('/cpu:0'):
                    self.run_detector1(config)

            else:

                logging.info("configure detector for GPU")

                self.run_detector1(config)

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

    def run_detector1(self, config):
        """
        use PeopleDetector
        """
    
        motion_detector = MotionDetector(self.md_min_area)

#        pdetector =  PeopleDetector(config)
#        with pdetector.as_default():

        with PeopleDetector(config) as pdetector:

            while not self.bStop:
                
                with self.lock:
                    self.lock.wait(0.2)

                    frame = self.frame
                    self.frame = None

                    self.frame1, _ = self.frames1[0] if self.frames1 else (None, None)
                    self.frame2, _ = self.frames2[0] if self.frames2 else (None, None)

                if frame is None:
                    continue

                self.current_frame = frame

                self.recognize(frame, motion_detector, pdetector)       

                self.frame_count2 += 1

                objects = []

                if self.dbg and self.dbg.draw_frame(frame, objects):
                    logging.info("stop signal from debug window [%d]", self.camera['id'])
                    break

                self.current_frame = None
            pass # with
        

    def run_detector2(self, config):
        """
        use PeopleDetector2 ( shared graph )
        """
        
        motion_detector = MotionDetector(self.md_min_area)

        with PeopleDetector2(config) as pdetector:

            while not self.bStop:
                
                with self.lock:
                    self.lock.wait(0.2)

                    frame = self.frame
                    self.frame = None

                    self.frame1, _ = self.frames1[0] if self.frames1 else (None, None)
                    self.frame2, _ = self.frames2[0] if self.frames2 else (None, None)

                if frame is None:
                    continue

                self.current_frame = frame

                self.recognize(frame, motion_detector, pdetector)       

                self.frame_count2 += 1

                objects = []

                if self.dbg and self.dbg.draw_frame(frame, objects):
                    logging.info("stop signal from debug window [%d]", self.camera['id'])
                    break

                self.current_frame = None
            pass # with
        pass        

    def _on_ta_alert(self, alert_id:str, prefix: str, frame):

        camera_id = self.camera['id']

        alert = AlertObject(camera_id, alert_id, None)
        alert.camera_name = self.camera['name']

        logging.debug("new %s alert: %s", prefix, alert_id)
        
        alert.set_image(prefix, frame)

        if self.post_new_alert:
            self.post_new_alert(alert)
        
        pass

    def on_alert(self, alert: AlertObject, is_enter: bool, box: TrackObject):
        
        camera_id = self.camera['id']

        if isinstance(box, TrackObject):
            pos = box.get_pos()
            if self.dbg: self.dbg.add_alert(pos, is_enter)

        alert.camera_id = camera_id
        alert.camera_name = self.camera['name']

        if is_enter:

            logging.debug("new alert: %s", alert)

            if self.post_new_alert:
                
                alert.set_image("T", self.current_frame, box)

                if reco_config.send_tb_images:
                    alert.set_image("T-1", self.frame1)
                    alert.set_image("T-2", self.frame2)

                if reco_config.send_ta_images > 0:
                    with self.lock:
                        self.alerts_ta.append(AlertTAState(camera_id, alert.alert_id))

                self.post_new_alert(alert)

        else:
            pass

    def recognize(self, frame, motion_detector, people_detector):
        
        if reco_config.enable_motion_detector and not motion_detector.isMotion(frame):
            return

        boxes = people_detector.process_frame(frame) if reco_config.enable_people_detector else []
        
        h, w = frame.shape[:2]
            
        if self.tracker:
            self.tracker.objects = boxes_to_track_objects(boxes)
            objects = list(self.tracker.objects)
        else:
            objects = list(boxes_to_track_objects(boxes))

        self.analyzer.process_objects(w, h, objects)        
    

       