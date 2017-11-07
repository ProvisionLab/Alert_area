"""
"""
import threading
import traceback
import cv2
import reco_config
from tracker_emu import TrackerEmu
from trk_analyzer2 import TrackAnalyzer2
from trk_object import TrackObject
from debug_window import DebugWindow

# camera: { 'id' : str, 'url' : str }

class RecoThread(threading.Thread):
    """
    """

    camera = None

    dbg = None

    connection = None

    thread_count = 0
    bStop = False

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

    def on_alert(self, alert_id: str, is_enter: bool, pos):
        camera_id = self.camera['id']
        if self.dbg: self.dbg.add_alert(pos, is_enter)
        self.connection.post_reco_alert(camera_id, alert_id)        

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
                analyzer = TrackAnalyzer2(alert_areas)
                analyzer.on_alert = self.on_alert

                # process stream
                while not RecoThread.bStop and cap.isOpened():

                    res, frame = cap.read()

                    #if not res:
                    #    break

                    if res:
                        tracker.process_frame(frame)

                        h, w = frame.shape[:2]

                        objects = list(tracker.objects.values())

                        analyzer.process_objects(w, h, objects)

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
