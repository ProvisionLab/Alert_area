import threading
import signal
import time
import cv2


#camera_url = "rtsp://admin:admin@24.171.185.186:554" # School [58]
camera_url = "rtsp://admin:admin@173.165.212.17:554" # Beach [7], FPS 30
#camera_url = "rtsp://admin:admin@76.175.137.190:554" # Residence [40], FPS 15
#camera_url = "rtsp://admin:admin@98.101.13.90:554" # Dog Play [27], FPS 4


bStop = False


frame_count = 0
frame_count2 = 0
frame_id = 0

def process_frame(frame):
    
    return
    
    cv2.imshow("dbg", frame)
    if cv2.waitKey(20) == 27: # E
        global bStop
        bStop = True


class FrameWorker(threading.Thread):
    
  
    def __init__(self):
        
        self.frame = None
        self.new_frame = threading.Condition()

        threading.Thread.__init__(self)
        pass

    def process_frame(self, frame):
        
        with self.new_frame:
            self.frame = frame
            self.new_frame.notify()
        pass

    def run(self):
        
        self.dbg_win = cv2.namedWindow("dbg", cv2.WINDOW_AUTOSIZE)

        while not bStop:
            
            with self.new_frame:
                self.new_frame.wait(0.1)

                frame = self.frame
                self.frame = None

            if frame is None:
                continue

            self.show_frame(frame)          

        cv2.destrowWindow("dbg")
        pass

    ##########################################

    def show_frame(self, frame):
        
        cv2.imshow("dbg", frame)

        if cv2.waitKey(500) == 27: # ESC
            global bStop
            bStop = True
     
        global frame_count2
        frame_count2 += 1
    

def get_frame1(cap):
    
    global frame_count, frame_count2, frame_id

    res, frame2 = cap.read()

    frame_id2 = int(cap.get(1))

    fn = frame_id2 - frame_id 
    frame_id = frame_id2

    if fn > 2:
        print("{0} frames dropped".format(fn))


    if res:
        frame_count += 1
        return frame2
    else:
        print("cap.read return False")
        return None


def get_frame2(cap):
    
    global frame_count, frame_count2
    
    frame = None

    while not bStop:
        
        res = cap.grab()

        if not res:
            break

    while not bStop:
    
        res, frame2 = cap.receive()

        if res:
            frame = frame2 
            frame_count += 1
            return frame
            
        if not res:
            break

    return frame

def capture(camera_url, worker):

    cap = cv2.VideoCapture(camera_url)    

    if not cap.isOpened():
        print("camera nbot opened")
        return

    global frame_count, frame_count2

    frame_count = 0
    frame_count2 = 0
    frame_time = time.time()

    while not bStop:

        frame = get_frame1(cap)

        frame_id = int(cap.get(1))
        
        if frame is not None:
            worker.process_frame(frame)

        now = time.time()
        delta = now - frame_time
        if delta > 5.0:
            fps = frame_count / delta
            fps2 = frame_count2 / delta
            frame_count = 0
            frame_count2 = 0
            frame_time = now
            print("Frame {0}, FPS {1:.1f}/{2:.1f}".format(frame_id, fps, fps2))

        pass

    cap.release()

def stop_execution():
    bStop = True

if __name__ == '__main__':

    signal.signal(signal.SIGINT, stop_execution)

    worker = FrameWorker()
    worker.start()

    capture(camera_url, worker)

    worker.join()
