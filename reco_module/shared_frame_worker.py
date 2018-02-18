import threading
from CameraContext import CameraContext

class PeopleDetectorWorker(threading.Thread):

    def __init__(self):
        
        self.frames = dict()
        self.lock = threading.Condition()
        
        self.bRunning = True
        super().__init__()
        pass

    def stop(self):
        self.bRunning = False

    def new_frame(self, camera_id, frame):
        
        with self.lock:

            self.frames[camera_id] = frame

            self.lock.notify()

        pass

    def run(self):
        
        with self.lock:
        
            while self.bRunning:
        
                if self.frames:
                    frames = self.frames
                    self.frames = dict()
                    self.lock.release()
                    try:
                        self._process_frames(frames)
                    finally:
                        self.lock.acquire()
                else:
                    self.lock.wait(1.0)

        pass

    def _process_frames(self, frames:dict):
        
        pass

class SharedFrameDetector(object):
    
    detector_worker = PeopleDetectorWorker()

    def __init__(self, camera_id):
        pass

    def new_frame(self, frame):
        pass


