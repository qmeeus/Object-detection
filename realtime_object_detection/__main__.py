import os, os.path as p
import sys
from time import sleep, time
import numpy as np
import ffmpeg
import subprocess
from queue import PriorityQueue
from multiprocessing import Pool, log_to_stderr

from realtime_object_detection.detection import ObjectDetection
from realtime_object_detection.io import InputStream, OutputFile, OutputStream
from realtime_object_detection.utils.logger import logger


BATCH_SIZE = 1
FPS = 30


def abspath(relpath):
    return p.abspath(p.join(p.dirname(__file__), '..', relpath))    


logger.info('       REALTIME OBJECT DETECTION       ')
input_stream = InputStream(os.environ['INPUT_STREAM_URL'], 1000, FPS)
input_stream.start()

# fps = input_stream.getFPS()
output_file = OutputFile(abspath(os.environ['OUTPUT_FILE']), 'XVID', {
    'fps': FPS, 'frameSize': input_stream.video_size
})

output_stream = OutputStream(
    os.environ['OUTPUT_STREAM_URL'],
    input_cfg={"format": "rawvideo", "s": "{}x{}".format(*input_stream.video_size)},
    filter_cfg={"fps": FPS, "round": "up"},
    output_cfg={
        "format": "flv", "pix_fmt": "yuv420p", 'preset': 'slower', 
        "movflags": "faststart", "qscale:v": 3
    }
)

outputs = [
    output_file, 
    output_stream
]

try:
    
    logger.info('       +++  Processing starts  +++')
    detector = ObjectDetection()
    
    while not input_stream.is_empty:

        batch_size = min(BATCH_SIZE, input_stream.size)
        frame_ids, frames = map(list, zip(*((input_stream.read() for _ in range(batch_size)))))
        # logger.debug(f'Batch size: {batch_size}    Remaining: {input_stream.size}')

        assert type(frame_ids) is list
        assert type(frames) is list

        frames_out = detector.detect_objects(frames)

        for frame_out in frames_out:
            for output in outputs:
                output.write_frame(frame_out)

except KeyboardInterrupt:

    logger.info('Cleaning outputs')
    for output in outputs:
        output.clean()
    detector.clean()

