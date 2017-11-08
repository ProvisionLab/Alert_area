import os
import cv2
import time
import argparse
import multiprocessing
import numpy as np
import tensorflow as tf
import cv2
from matplotlib import pyplot as plt


STANDARD_ALERTS = [
    'VIRTUAL WALL',
    'RESTRICTED AREA',
    'LOITERING'
]


class PeopleDetector:
    
    def __init__(self):
        CWD_PATH = os.getcwd()
        MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
        PATH_TO_CKPT = os.path.join(CWD_PATH, 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')
        # Load a frozen TF model
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            self.sess = tf.Session(graph=self.detection_graph)
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')

            # Each box represents a part of the image where a particular object was detected.
            self.boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')

            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            self.scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            self.classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def process_frame(self, frame, sess):
        #with self.detection_graph.as_default():
            #self.sess = tf.Session(graph=self.detection_graph)
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        
        frame_scaled = cv2.resize(frame, (480, 270))
        image_np_expanded = np.expand_dims(frame_scaled, axis=0)

            # Actual detection.
        (boxes, scores, classes, num_detections) = sess.run(
           [self.boxes, self.scores, self.classes, self.num_detections],
           feed_dict={self.image_tensor: image_np_expanded})

        min_score_thresh = 0.2

        people_boxes = [[b[0] * frame.shape[0], b[1] * frame.shape[1], b[2] * frame.shape[0], b[3] * frame.shape[1]]
           for b, s, c in zip(boxes[0], scores[0], classes[0]) if s > min_score_thresh and c == 1.0]

        return people_boxes

