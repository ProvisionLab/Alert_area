import time
import logging
from MotionDetector import MotionDetector
from rogapi.alerts import ROG_Alert, ROG_AlertImage
from alert_object import AlertObject, encode_cvimage, add_box_to_image
from trk_analyzer2 import TrackAnalyzer2
from trk_object import TrackObject
import reco_config

import debug_window

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


class CameraContext(object):
    
    def __init__(self, 
        camera_id,
        cap_w, cap_h, 
        use_motion_detector = True, 
        post_alert_callback = None):

        self.camera_id = camera_id
        self.alert_areas = list() # 2do:
        
        self.post_alert = post_alert_callback
        
        md_min_area = (cap_w * cap_h) / 600
        self.motion_detector = MotionDetector(md_min_area) if use_motion_detector else None

        self.frame0 = None
        self.frame_time = time.time()

        self.frame_count1 = 0
        self.frame_count2 = 0

        self.frames1 = list()
        self.frames2 = list()

        self.frame1 = None   # frame T-1
        self.frame2 = None   # frame T-2
        
        self.alerts_ta = list()     # list of AlertTAState. 

        self.tracker = None

        self.analyzer = TrackAnalyzer2(self.alert_areas)
        self.analyzer.on_alert = self._on_alert

        pass

    def on_new_frame(self, frame):
        
        now = time.time()

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

        pass

    def preprocess_frame(self, frame):
        """
        @return True, to continue detection
        """

        self.frame0 = frame

        self.frame1, _ = self.frames1[0] if self.frames1 else (None, None)
        self.frame2, _ = self.frames2[0] if self.frames2 else (None, None)

        return not self.motion_detector or self.motion_detector.isMotion(frame)

    def postprocess_frame(self, frame, objects):
        
        if self.tracker:
            self.tracker.objects = objects
            objects = list(self.tracker.objects)
        else:
            objects = list(objects)

        h, w = frame.shape[:2]

        self.analyzer.process_objects(w, h, objects)
    
        self.frame_count2 += 1
        
        pass

    def get_fps(self, reset=True):
        """
        @return (fps,fps2)  input FPS and output FPS
        """
        
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

    def set_alert_areas(self, areas):
    
        if self.analyzer:
            self.analyzer.update_areas(areas)        

    def _process_ta_frames(self, frame):

        now = time.time()

        new_list = list()

        for ta in self.alerts_ta:

            d = now - ta.timestamp
            n = int(d)

            #print("1 {0} {1}, time: T{2:.2f}, n: {3}".format(ta.alert_id, ta.count, d, n))

            if n <= reco_config.send_ta_images and n > ta.count:
                
                self._post_ta_image(ta, ta.alert_id, "T{0}".format(n), frame)
                ta.count = n

            if n < reco_config.send_ta_images:
                new_list.append(ta)
                
            pass

        self.alerts_ta = new_list

        #for ta in self.alerts_ta:
        #    print("2 {0} T{1}".format(ta.alert_id, ta.count))

        pass

    def _post_ta_image(self, alert_ta, alert_id: str, prefix: str, frame):
    
        if self.post_alert:
            alert_image = ROG_AlertImage(None, encode_cvimage(frame))
            alert_image.obj = alert_ta
            self.post_alert(alert_image)
        
        pass

    def _on_alert(self, alert: AlertObject, is_enter: bool, box: TrackObject):
        """
        callback from Analizer
        """
        
        if is_enter:

            logging.debug("new alert: %s", alert)

            if self.post_alert:
                
                rog_alert = ROG_Alert(self.camera_id, alert.alert_type_id)
                
                image0 = add_box_to_image(self.frame0, box)

                if reco_config.DEBUG:
                    debug_window.debug_image_output(image0)

                rog_alert.set_image("image_3", encode_cvimage(add_box_to_image(self.frame0, box)))

                if reco_config.send_tb_images:
                    rog_alert.set_image("image_1", encode_cvimage(self.frame2))
                    rog_alert.set_image("image_2", encode_cvimage(self.frame1))

                if reco_config.send_ta_images > 0:
                    alert_ta = AlertTAState(self.camera_id, alert.alert_id)
                    rog_alert.obj = alert_ta
                    self.alerts_ta.append(alert_ta)

                self.post_alert(rog_alert)

        else:
            pass