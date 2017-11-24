"""
test GPU speed
"""
import time
import threading
import signal
import tensorflow as tf
import cv2
from PeopleDetector import PeopleDetector
from tensorflow.python.client import device_lib

use_gpu = True

def show_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    for i in local_device_protos:
        print("{0}, memory_limit: {1}".format(i.name, i.memory_limit))

if use_gpu:
    config = tf.ConfigProto()
    #config = tf.ConfigProto(device_count={'CPU': 1, 'GPU': 1}, allow_soft_placement = True)
else:
    config = tf.ConfigProto(device_count={'CPU': 1, 'GPU': 0}, allow_soft_placement = True)

config.gpu_options.allow_growth = True
#config.log_device_placement = True

bStop = False

def detect(index, max_count, fps_list: dict):
    
    frame = cv2.imread("test_image01.jpg")

    if frame is None:
        print("image test_image01.jpg not loaded")
        return

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
                #print("[{0}] FPS {1:.2f}".format(index, fps))
                fps_list[index] = fps

def run(index, max_count, fps_list: dict):
    
    if use_gpu:
        #with tf.device('/device:CPU:0'):
            detect(index, max_count, fps_list)    
    else:
        with tf.device('/CPU:0'):
            detect(index, max_count, fps_list)    

def stop_execution(signum, taskfrm):
    global bStop
    bStop = True
    print("Ctrl-C was pressed")


def run_detects(count):
    
    threads = []
    fps_list = {}

    for i in range(count):
        threads.append(threading.Thread(target=run, args=(i, 1000, fps_list)))

    print("press Ctrl-C to stop")

    for t in threads:
        t.start()

    print()

    while not bStop:

        time.sleep(2.0)
        
        s = ""
        total_fps = 0.0
        for k,fps in fps_list.items():
            s += ", [{0}] FPS {1:.1f}".format(k, fps)
            total_fps += fps

        print("\rTotal FPS {0:.2f}".format(total_fps), s, end=".    ")

    print()

    for t in threads:
        t.join()

    print("Total FPS {0:.2f}".format(total_fps))

if __name__ == "__main__":

    signal.signal(signal.SIGINT, stop_execution)    

    show_available_gpus()

    run_detects(4)
