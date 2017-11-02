import threading
import time
import cv2
from tracker_emu import TrackerEmu
from trk_analyzer import TrackAnalyzer
from trk_object import TrackObject
from debug_window import DebugWindow
import traceback
from reco_client import post_reco_alert, get_camera_alerts

# camera: { 'id' : str, 'url' : str }

thread_count = 0
bStop = False

def stop_recognition():
    global bStop
    bStop = True

def wait_threads():
    while thread_count > 0:
        time.sleep(1)

class RecoThread(threading.Thread):
    """
    """

    access_token = None
    camera = None

    tracker = None

    dbg = None

    def __init__(self, access_token, camera):
        self.access_token = access_token
        self.camera = camera
        threading.Thread.__init__(self)

    def on_alert(self, camera_id: str, alert_id: str, obj: TrackObject):
        print("alert: {0} {1}".format(camera_id,alert_id))
        if self.dbg: self.dbg.add_alert(obj)
        #post_reco_alert(self.access_token, camera_id, alert_id)        

    def run(self):

        print('start reco: {0}'.format(self.camera['url']))

        # open stream by url
        camera_url = self.camera['url']
        camera_id = self.camera['id']

        self.tracker = TrackerEmu()

        self.dbg = DebugWindow(self.access_token, self.camera, self.tracker)

        try:
            cap = cv2.VideoCapture(camera_url)

            if cap.isOpened():

                # setup analyzer
                alerts = get_camera_alerts(self.access_token, camera_id)
                analyzer = TrackAnalyzer(alerts)
                analyzer.on_alert = lambda alert_id, obj: self.on_alert(camera_id, alert_id, obj)

                # process stream
                while not bStop and cap.isOpened():

                    res, frame = cap.read()

                    #if not res:
                    #    break

                    if res:
                        self.tracker.process_frame(frame)

                        h, w = frame.shape[:2]

                        analyzer.process_objects(w, h, list(self.tracker.objects.values()))

                        if self.dbg and self.dbg.draw_frame(frame, self.tracker.objects):
                            break

                    pass #while

            cap.release()
            print('end: {0}'.format(camera_id))

        except:
            print('exception: {0}'.format(camera_id))
            traceback.print_exc()

        global thread_count
        thread_count -= 1

        del self.dbg
        pass

def start_recognition(access_token: str, camera: dict):

    global thread_count
    thread_count += 1

    t = RecoThread(access_token, camera)
    t.start()
