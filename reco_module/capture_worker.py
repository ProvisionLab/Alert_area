"""
"""
import threading
import traceback
import time
import cv2
from frame_worker import FrameWorker
import reco_config
from urllib.parse import quote
import logging

"""
camera: { 
    'id': int, 
    'name': str, 
    'url': str, 
    'enabled': bool     optional, default True
    'areas' : [...]     alert areas
    'users' : [...]     users subscribed
    }
"""

class CaptureWorker(threading.Thread):
    """
    """

    connection = None
    camera = None
    alert_areas = None

    thread_count = 0
    bStop = False   # True, if thread gone to exit
    bExit = False   # True, if thread exited

    worker = None

    use_cpu = reco_config.use_cpu

    @classmethod
    def exist_any_recognition(cls):
        return cls.thread_count > 0

    def __init__(self, connection, camera):

        self.connection = connection

        if connection is not None:
            self.post_reco_alert = self.connection.post_reco_alert
        else:
            self.post_reco_alert = self._dummy_post_reco_alert

        assert(isinstance(camera,dict))

        self.camera = camera

        self.camera_id = camera.get('id')
        self.camera_name = camera.get('name')
        self.alert_areas = camera.get('areas',[])

        self.camera_url = self.get_camera_url(camera)

        self.restart_on_fail = False
        self.use_motion_detector = reco_config.enable_motion_detector

        CaptureWorker.thread_count += 1

        super().__init__()

    def stop(self):
        logging.debug("signal to stop capture camera [%d]", self.camera['id'])
        self.bStop = True

    def get_fps(self):
        
        if self.worker:
            return self.worker.get_fps()
        else:
            return 0,0

    def update_areas(self, areas):

        #print('############## update_areas #################')

        self.alert_areas = areas

        logging.debug("update_areas: [%d] %s", self.camera['id'], areas)

        if areas is None:
            logging.warning("update areas of camera: [%d] \'%s\', None", self.camera['id'], self.camera['name'])
            return

        #logging.debug("update areas of camera: [%d] \'%s\', %d areas", self.camera['id'], self.camera['name'], len(areas))

        if self.worker:
            self.worker.update_areas(areas)

        pass

    def get_camera_url(self, camera):

        return camera.get('url')

        username = camera.get('username')
        password = camera.get('password')
        if username is None or password is None:
            return self.camera_url

        if self.camera_url[:7] != 'rtsp://':
            return self.camera_url

        camera_url = 'rtsp://{0}:{1}@{2}'.format(quote(username), quote(password), self.camera_url[7:])

        return camera_url

    def run_capture(self, cap):
        
        while not self.bStop:
    
            res, frame = cap.read()
            if not res:
                logging.info('camera: [%d] \'%s\', EOF', self.camera_id, self.camera_name)
                break

            self.worker.process_frame(frame)
            pass

        logging.debug('capture loop end of camera [%d] \'%s\'', self.camera_id, self.camera_name)

    def run(self):
        
        if self.camera is not None:
            camera_id = self.camera.get('id')
            camera_name = self.camera.get('name')
        else:
            camera_id = 0
            camera_name = ''
            

        #if not self.alert_areas:
        #    logging.info("camera %s has no alerts, resetting...", camera_name)
        #    CaptureWorker.thread_count -= 1
        #    self.bExit = True
        #    return

        # open stream by url

        while True:

            cap = cv2.VideoCapture(self.camera_url)

            if cap.isOpened():
        
                cap_fps = int(cap.get(cv2.CAP_PROP_FPS))
                cap_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                cap_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                logging.info('begin capture of camera: \'%s\', url: \'%s\', fps: %d, [%d x %d]', 
                    self.camera_name, self.camera_url, cap_fps, cap_w, cap_h)
        
                self.worker = FrameWorker(self.camera, cap_w, cap_h, self.post_reco_alert)
                self.worker.use_cpu = self.use_cpu
                self.worker.use_motion_detector = self.use_motion_detector

                self.worker.start()

                self.run_capture(cap)
        
                self.worker.stop()
                self.worker.join()
                self.worker = None

                cap.release()

            else:
    
                logging.error("camera [%d] \'%s\' not opened", self.camera_id, self.camera_name)
                break;

            if self.bStop or not self.restart_on_fail:
                break

        CaptureWorker.thread_count -= 1

        logging.info('end capture of camera [%d] \'%s\', workers left: %d', self.camera_id, self.camera_name, CaptureWorker.thread_count)

        self.bExit = True
        pass

    def _dummy_post_reco_alert(self, alert):
        pass