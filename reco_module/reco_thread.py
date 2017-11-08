"""
"""
import threading
import traceback
import time
import cv2
from tracker_emu import TrackerEmu
from trk_analyzer2 import TrackAnalyzer2
from trk_object import TrackObject
from alert_object import AlertObject
from debug_window import DebugWindow
import reco_config

# camera: { 'id' : str, 'url' : str }

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

        if self.current_frame is not None:
            alert.set_image(self.current_frame)

        if reco_config.send_alerts_to_upstream:
            self.connection.usapi.post_alert(alert)        
        else:
            self.connection.post_reco_alert(alert)      

    def update_areas(self, areas):

        #print('############## update_areas #################')

        if self.analyzer:
            self.analyzer.update_areas(areas)

        if self.dbg:
            self.dbg.update_areas(areas)
        pass

    def run(self):

        print('start reco: \'{0}\', {1}'.format(self.camera['name'], self.camera['url']))

        # open stream by url
        camera_url = self.camera['url']
        camera_id = self.camera['id']

        tracker = TrackerEmu()

        if reco_config.DEBUG:
            self.dbg = DebugWindow(self.camera, tracker, self.connection)

        try:
            cap = cv2.VideoCapture(camera_url)

            if cap.isOpened():
                
                # setup analyzer
                alert_areas = self.connection.get_camera_alerts(camera_id)
                self.analyzer = TrackAnalyzer2(alert_areas)
                self.analyzer.on_alert = self.on_alert

                # process stream
                while not RecoThread.bStop and cap.isOpened():

                    res, frame = cap.read()

                    #if not res:
                    #    break

                    if res:
                        tracker.process_frame(frame)

                        h, w = frame.shape[:2]

                        objects = list(tracker.objects.values())

                        self.current_frame = frame
                        self.analyzer.process_objects(w, h, objects)

                        if self.dbg and self.dbg.draw_frame(frame, objects):
                            break

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
