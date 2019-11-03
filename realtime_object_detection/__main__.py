import os

from realtime_object_detection.detection import ObjectDetection
from realtime_object_detection.streaming import Streamer


detector = ObjectDetection()

stream = Streamer(
    rtmp_server=os.environ['RTMP_SERVER'],
    stream_in=os.environ['STREAM_IN'],
    stream_out=os.environ['STREAM_OUT'],
    process_frame=detector.detect_objects,
    queue_size=1024,
    num_workers=5
)

stream.start()
detector.clean()
