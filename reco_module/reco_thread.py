"""
"""
import threading
import traceback
import cv2
import reco_config
from tracker_emu import TrackerEmu
from trk_analyzer import TrackAnalyzer
from trk_object import TrackObject
from debug_window import DebugWindow

# camera: { 'id' : str, 'url' : str }

class RecoThread(threading.Thread):
    """
    """

    camera = None

    tracker = None

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

    def on_alert(self, camera_id: str, alert_id: str, obj: TrackObject):
        if self.dbg: self.dbg.add_alert(obj)
        self.connection.post_reco_alert(camera_id, alert_id)        

    def run(self):

        print('start reco: \'{0}\', {1}'.format(self.camera['name'], self.camera['url']))

        # open stream by url
        camera_url = self.camera['url']
        camera_id = self.camera['id']

        self.tracker = TrackerEmu()

        if reco_config.DEBUG:
            self.dbg = DebugWindow(self.camera, self.tracker, self.connection)

        try:
            cap = cv2.VideoCapture(camera_url)

            if cap.isOpened():

                # setup analyzer
                alert_areas = self.connection.get_camera_alerts(camera_id)
                analyzer = TrackAnalyzer(alert_areas)
                analyzer.on_alert = lambda alert_id, obj: self.on_alert(camera_id, alert_id, obj)

                # process stream
                while not RecoThread.bStop and cap.isOpened():

                    res, frame = cap.read()

                    #if not res:
                    #    break

                    if res:
                        self.tracker.process_frame(frame)

                        h, w = frame.shape[:2]

                        #objects = list(self.tracker.objects.values())
                        objects = self.tracker.objects.values()

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
