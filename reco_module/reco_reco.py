import threading
import time
import cv2
from tracker_emu import TrackerEmu
from debug_window import DebugWindow
import traceback

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

    def run(self):

        print('start reco: {0}'.format(self.camera['url']))

        self.dbg = DebugWindow(self.access_token, self.camera)

        # open stream by url
        camera_url = self.camera['url']
        camera_id = self.camera['id']

        self.tracker = TrackerEmu(self.access_token, self.camera)

        try:
            cap = cv2.VideoCapture(camera_url)
      
            if cap.isOpened():

#                dbg = DebugWindow()
#                cv2.namedWindow('video', cv2.WINDOW_NORMAL)

                while not bStop and cap.isOpened():

                    res, frame = cap.read()

                    #if not res:
                    #    break

                    if res:
                        self.tracker.process_frame(frame)

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
