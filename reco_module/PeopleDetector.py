import os
import cv2
import time
import threading
#import argparse
#import multiprocessing
import numpy as np
import tensorflow as tf
import cv2
#from matplotlib import pyplot as plt
import logging

STANDARD_ALERTS = [
    'VIRTUAL WALL',
    'RESTRICTED AREA',
    'LOITERING'
]

class PeopleDetector:
    
    detection_graph = None

    session = None
    
    def __init__(self, config):
        
        self.config = config
        self.detection_graph = self.create_grapth()

    def create_grapth(self):
        
        CWD_PATH = os.getcwd()
        MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
        PATH_TO_CKPT = os.path.join(CWD_PATH, 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')
        # Load a frozen TF model
        
        detection_graph = tf.Graph()

        with detection_graph.as_default():
            #self.sess = tf.Session(graph=self.detection_graph)
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

            # Each box represents a part of the image where a particular object was detected.
            self.boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            self.scores = detection_graph.get_tensor_by_name('detection_scores:0')
            self.classes = detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')        

        return detection_graph

    def process_frame(self, frame):
        
        frame_scaled = cv2.resize(frame, (640, 480))
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(frame_scaled, axis=0)

        # Actual detection.
        (boxes, scores, classes, num_detections) = self.session.run(
           [self.boxes, self.scores, self.classes, self.num_detections],
           feed_dict={self.image_tensor: image_np_expanded})

        min_score_thresh = 0.2

        people_boxes = [[b[0] * frame.shape[0], b[1] * frame.shape[1], b[2] * frame.shape[0], b[3] * frame.shape[1]]
           for b, s, c in zip(boxes[0], scores[0], classes[0]) if s > min_score_thresh and c == 1.0]

        return people_boxes

    def as_default(self):
        
        gcx = self.detection_graph.as_default()
        self.session = tf.Session(graph=self.detection_graph, config=self.config)
        return gcx


class PeopleDetectorGraph(tf.Graph):
    
    ref_count = 0
    
    def __init__(self):
        
        super().__init__()
        
        CWD_PATH = os.getcwd()
        MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
        PATH_TO_CKPT = os.path.join(CWD_PATH, 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')
        
        with self.as_default():
            #sess = tf.Session(graph=self.detection_graph)

            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.image_tensor = self.get_tensor_by_name('image_tensor:0')

            # Each box represents a part of the image where a particular object was detected.
            self.boxes = self.get_tensor_by_name('detection_boxes:0')

            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            self.scores = self.get_tensor_by_name('detection_scores:0')
            self.classes = self.get_tensor_by_name('detection_classes:0')
            self.num_detections = self.get_tensor_by_name('num_detections:0')
            pass

    def process_frame(self, frame, tf_session):
        
        frame_scaled = cv2.resize(frame, (640, 480))

        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(frame_scaled, axis=0)

        # Actual detection.
        (boxes, scores, classes, num_detections) = tf_session.run(
           [self.boxes, self.scores, self.classes, self.num_detections],
           feed_dict={self.image_tensor: image_np_expanded})

        min_score_thresh = 0.2

        people_boxes = [[b[0] * frame.shape[0], b[1] * frame.shape[1], b[2] * frame.shape[0], b[3] * frame.shape[1]]
           for b, s, c in zip(boxes[0], scores[0], classes[0]) if s > min_score_thresh and c == 1.0]

        return people_boxes        

class PeopleDetector2(object):
    """
    save as PeopleDetector
    but use one instance of tf.Graph
    """
    
    lock = threading.Lock()
    detection_graph = None
    ref_count = 0

    def __init__(self, config):
        self.config = config
        pass

    @classmethod
    def aquire_graph(cls):

        #graph = PeopleDetectorGraph()
        #return graph

        with PeopleDetector2.lock:
            if cls.detection_graph is None:
                logging.info("create PeopleDetectorGraph instance")
                cls.detection_graph = PeopleDetectorGraph()

            cls.detection_graph.ref_count += 1
            return cls.detection_graph

    @classmethod
    def release_graph(cls, graph):

        #del graph
        #return;        

        with PeopleDetector2.lock:
            cls.detection_graph.ref_count -= 1
            if cls.detection_graph.ref_count == 0:
                logging.info("delete PeopleDetectorGraph instance")
                del cls.detection_graph

    def as_default(self):
        self.graph = PeopleDetector2.aquire_graph(); 
        gcx = self.graph.as_default()
        self.session = tf.Session(graph=self.graph, config=self.config)
        return gcx

    def __enter__(self):
        self.graph = PeopleDetector2.aquire_graph(); 
        self.grath_context = self.graph.as_default()
        self.session = tf.Session(graph=self.graph, config=self.config)
        return self

    def __exit__(self, type, value, traceback):

        self.session.close()
        self.session = None

        self.grath_context.close()
        self.grath_context = None

        PeopleDetector2.release_graph(self.graph)
        self.graph = None
        pass

    def process_frame(self, frame):
        
        frame_scaled = cv2.resize(frame, (640, 480))

        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(frame_scaled, axis=0)

        # Actual detection.
        (boxes, scores, classes, num_detections) = self.session.run(
           [self.graph.boxes, self.graph.scores, self.graph.classes, self.graph.num_detections],
           feed_dict={self.graph.image_tensor: image_np_expanded})

        min_score_thresh = 0.2

        people_boxes = [[b[0] * frame.shape[0], b[1] * frame.shape[1], b[2] * frame.shape[0], b[3] * frame.shape[1]]
           for b, s, c in zip(boxes[0], scores[0], classes[0]) if s > min_score_thresh and c == 1.0]

        return people_boxes        
