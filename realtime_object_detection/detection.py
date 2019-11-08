import os
import cv2
import numpy as np
import tensorflow as tf
import time

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

from realtime_object_detection.utils.logger import logger

class ObjectDetection:

    # PATH_TO_CKPT = 'models/mscoco/frozen_inference_graph.pb'
    PATH_TO_LABELS = 'models/mscoco_label_map.pbtxt'
    PATH_TO_CKPT = 'models/ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph.pb'
    NUM_CLASSES = 90


    def __init__(self):

        # Loading label map
        self.label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(
            self.label_map, max_num_classes=self.NUM_CLASSES, use_display_name=True
        )

        self.category_index = label_map_util.create_category_index(self.categories)

        self._graph = tf.Graph()
        self._session = tf.InteractiveSession(graph=self._graph)

        with tf.gfile.GFile(self.PATH_TO_CKPT, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            
        tf.import_graph_def(graph_def, name='')

        self._number_of_batches = 0
        self._number_of_predictions = 0
        self._prediction_time = 0


    def T(self, layer_name):
        '''Helper for getting layer output tensor'''
        return self._graph.get_tensor_by_name(f'{layer_name}:0')

    def detect_objects(self, frames):
        # frames_rgb = list(map(self.to_rgb, frames))

        if len(frames) == 1:
            image_array = np.expand_dims(frames[0], axis=0)
        else:
            image_array = np.array(frames)

        # Each box represents a part of the image where a particular object was detected.
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        image_tensor = self.T('image_tensor')
        boxes = self.T('detection_boxes')
        scores = self.T('detection_scores')
        classes = self.T('detection_classes')
        num_detections = self.T('num_detections')

        # logger.info(f'    Detection starts, size: {image_array.shape}')

        # Actual detection.
        start = time.time()
        try:
            return_values = self._session.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_array}
            )
        
            t = time.time() - start
            bs = len(image_array)
            self._prediction_time += t
            self._number_of_predictions += bs
            self._number_of_batches += 1
            # logger.debug(f"Batch n°{self._number_of_batches}: size={bs}")
            # logger.debug(f'total time={t:.2f}, time={t / bs:.2f}, fps={self.average_time:.2f}')
            # logger.debug("Batch sizes: {[len(array) for array in return_values]}")
            return list(map(self.add_boxes, frames, *return_values))

        except Exception as err:
            print(image_array)
            raise err

    def add_boxes(self, frame, boxes, scores, classes, num_detections):

        # Visualization of the results of a detection.
        processed_image = vis_util.visualize_boxes_and_labels_on_image_array(
            frame,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=4
        )

        # logger.debug(f'input shape: {frame.shape}, output_shape: {processed_image.shape}')

        return processed_image

    def clean(self):
        self._session.close()

    @staticmethod
    def to_rgb(frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    @property
    def average_time(self):
        return self._number_of_predictions / self._prediction_time

    @property
    def average_batch_time(self):
        return self._number_of_batches / self._prediction_time
