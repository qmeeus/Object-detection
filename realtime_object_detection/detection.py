import os
import cv2
import numpy as np
import tensorflow as tf

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util



class ObjectDetection:

    PATH_TO_CKPT = 'models/mscoco/frozen_inference_graph.pb'
    PATH_TO_LABELS = 'models/mscoco/mscoco_label_map.pbtxt'
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


    def T(self, layer_name):
        '''Helper for getting layer output tensor'''
        return self._graph.get_tensor_by_name(f'{layer_name}:0')

    def detect_objects(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(frame_rgb, axis=0)
        image_tensor = self.T('image_tensor')

        # Each box represents a part of the image where a particular object was detected.
        boxes = self.T('detection_boxes')

        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        scores = self.T('detection_scores')
        classes = self.T('detection_classes')
        num_detections = self.T('num_detections')

        # Actual detection.
        (boxes, scores, classes, num_detections) = self._session.run(
            [boxes, scores, classes, num_detections],
            feed_dict={image_tensor: image_np_expanded})

        # Visualization of the results of a detection.
        processed_image = vis_util.visualize_boxes_and_labels_on_image_array(
            frame_rgb,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=4)

        logger.debug(f'input shape: {frame_rgb.shape}, output_shape: {processed_image.shape}')

        return processed_image

    def clean(self):
        self._session.close()
