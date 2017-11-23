"""
test GPU speed
"""
import time
import threading
import signal
import tensorflow as tf
import cv2
from PeopleDetector import PeopleDetector


config = tf.ConfigProto()
#config = tf.ConfigProto(device_count={'CPU': 1, 'GPU': 0}, allow_soft_placement = True)

bStop = False
total_fps = 0

def run(index, max_count = 100):
    
    frame = cv2.imread("test_image01.jpg")

    pdetector =  PeopleDetector(config)

    fps = 0

    with pdetector.as_default():

        frame_count = 0
        frame_time = time.time()

        while not bStop and frame_count < max_count:
            
            pdetector.process_frame(frame)
            frame_count += 1

            now = time.time()
            d = now - frame_time
            if d > 2.0:
                fps = frame_count / d
                frame_count = 0
                frame_time = now
                print("[{0}] FPS {1:.2f}".format(index, fps))

    global total_fps
    total_fps += fps

def stop_execution(signum, taskfrm):
    global bStop
    bStop = True
    print("Ctrl-C was pressed")

if __name__ == "__main__":
    
    threads = []

    threads.append(threading.Thread(target=run, args=(1, 1000,)))
    threads.append(threading.Thread(target=run, args=(2, 1000,)))

    signal.signal(signal.SIGINT, stop_execution)    

    total_fps = 0

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("Total FPS {0:.2f}".format(total_fps))
