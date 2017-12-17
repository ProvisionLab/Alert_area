"""
test GPU speed
"""
import time
import threading
import signal
import tensorflow as tf
import cv2
from PeopleDetector import PeopleDetector, PeopleDetector2
from tensorflow.python.client import device_lib

use_cpu = False

if use_cpu:
    config = tf.ConfigProto(device_count={'GPU': 0}, allow_soft_placement = False)
else:
    config = tf.ConfigProto(allow_soft_placement = True)
    #config = tf.ConfigProto(device_count={'CPU': 1, 'GPU': 1}, allow_soft_placement = True)

#config.intra_op_parallelism_threads = 10
#config.inter_op_parallelism_threads = 10
#config.use_per_session_threads = False
config.gpu_options.per_process_gpu_memory_fraction = 0.1
config.gpu_options.allow_growth = True

config.log_device_placement = False

bStop = False

def detect(index, max_count, fps_list: dict):
    
    frame = cv2.imread("test_image01.jpg")

    if frame is None:
        print("image test_image01.jpg not loaded")
        return


    fps = 0

    pdetector =  PeopleDetector(config)
    with pdetector.detection_graph.as_default(), \
        tf.Session(graph=pdetector.detection_graph, config=config):


#    with PeopleDetector2(config) as pdetector:

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
                fps_list[index] = fps

def run(index, max_count, fps_list: dict):
    
    if use_cpu:
        with tf.device('/cpu:0'):
            detect(index, max_count, fps_list)    
    else:
        #with tf.device('/gpu:0'):
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

    total_fps = 0.0

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

def show_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    for i in local_device_protos:
        print("{0}, memory_limit: {1}".format(i.name, i.memory_limit))

if __name__ == "__main__":

    signal.signal(signal.SIGINT, stop_execution)    

    show_available_gpus()

    run_detects(4)
