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
        self.rog_alert_id = None

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
        self.alert_areas = [] if camera is None else camera.get('areas',[])

        self.post_new_alert = post_new_alert

        self.md_min_area = (cap_w * cap_h) / 600
        
        self.lock = threading.Condition()

        self.frames1 = []
        self.frames2 = []
        
        self.frame = None

        self.frame_count1 = 0
        self.frame_count2 = 0
        self.frame_time = time.time()

        self.alerts_ta = []

        self.use_motion_detector = reco_config.enable_motion_detector

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
                
                self._on_ta_alert(ta, ta.alert_id, "T{0}".format(n), frame)
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
            self.frame_count1 += 1

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

    def get_fps(self, reset=True):
        """
        @return (fps,fps2)  input FPS and output FPS
        """
        with self.lock:
        
            now = time.time()
            d = now - self.frame_time

            if d < 1.0:
                return 0,0

            fps1 = self.frame_count1 / d
            fps2 = self.frame_count2 / d

            if reset:

                self.frame_time = now
                self.frame_count1 = 0
                self.frame_count2 = 0

            return fps1, fps2

    def update_areas(self, areas):
        
        with self.lock:
        
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

        logging.info('use motion detector: %s', self.use_motion_detector)
    
        motion_detector = MotionDetector(self.md_min_area) if self.use_motion_detector else None

#        pdetector =  PeopleDetector(config)
#        with pdetector.as_default():

        t1 = time.time()

        with PeopleDetector(config) as pdetector, self.lock:

            while not self.bStop:
                
                #logging.info('reco loop')

                frame = self.frame
                self.frame = None
                
                if frame is None:
                    self.lock.wait(0.1)
                    continue

                self.frame1, _ = self.frames1[0] if self.frames1 else (None, None)
                self.frame2, _ = self.frames2[0] if self.frames2 else (None, None)

#                print("fps2: ", self.frame_count1, self.frame_count2)

                self.current_frame = frame

                self.lock.release()

                h, w = frame.shape[:2]

                try:

                    #logging.info("reco begin: %.2f s", time.time()-t1)
                    #t1 = time.time()

                    if motion_detector is not None and not motion_detector.isMotion(frame):
                        continue

                    objects = self.recognize(frame, motion_detector, pdetector)       

                    #logging.info("reco end: %.2f s", time.time()-t1)
                    #t1 = time.time()

                finally:

                    self.lock.acquire()

                self.frame_count2 += 1

                if len(objects) > 0:

                    self.analyzer.process_objects(w, h, objects)        
                    objects = None

                self.current_frame = None

            pass # with
        

    def run_detector2(self, config):
        """
        use PeopleDetector2 ( shared graph )
        """
        
        motion_detector = MotionDetector(self.md_min_area) if self.use_motion_detector else None

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

                objects = []

                if self.dbg and self.dbg.draw_frame(frame, objects):
                    logging.info("stop signal from debug window [%d]", self.camera['id'])
                    break

                self.current_frame = None
            pass # with
        pass        

    def _on_ta_alert(self, alert_ta, alert_id: str, prefix: str, frame):

        if self.post_new_alert:
            alert_image = ROG_AlertImage(None, encode_cvimage(frame))
            alert_image.obj = alert_ta
            self.post_new_alert(alert_image)
        
        pass

    def on_alert(self, alert: AlertObject, is_enter: bool, box: TrackObject):
        
        camera_id = self.camera['id']

        if isinstance(box, TrackObject):
            pos = box.get_pos()
            if self.dbg: self.dbg.add_alert(pos, is_enter)

        if is_enter:

            logging.info("new alert: [%d] %s", alert.camera_id, alert.alert_type)

            if self.post_new_alert:
                
                rog_alert = ROG_Alert(camera_id, alert.alert_type_id)
                
                rog_alert.set_image("image_3", encode_cvimage(add_box_to_image(self.current_frame, box)))

                if reco_config.send_tb_images:
                    rog_alert.set_image("image_1", encode_cvimage(self.frame2))
                    rog_alert.set_image("image_2", encode_cvimage(self.frame1))

                if reco_config.send_ta_images > 0:
                    with self.lock:
                        alert_ta = AlertTAState(camera_id, alert.alert_id)
                        rog_alert.obj = alert_ta
                        self.alerts_ta.append(alert_ta)

                self.post_new_alert(rog_alert)

        else:
            pass

    def recognize(self, frame, motion_detector, people_detector):
        
        boxes = people_detector.process_frame(frame) if reco_config.enable_people_detector else []
        
        h, w = frame.shape[:2]
            
        if self.tracker:
            self.tracker.objects = boxes_to_track_objects(boxes)
            objects = list(self.tracker.objects)
        else:
            objects = list(boxes_to_track_objects(boxes))

        return objects
