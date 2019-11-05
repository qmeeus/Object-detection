import os, os.path as p
from time import sleep
import numpy as np
import ffmpeg
import subprocess
from queue import PriorityQueue
from multiprocessing import Pool, log_to_stderr

from realtime_object_detection.detection import ObjectDetection
from realtime_object_detection.io import InputStream, OutputFile, OutputStream
from realtime_object_detection.utils.logger import logger


def abspath(relpath):
    return p.abspath(p.join(p.dirname(__file__), '..', relpath))    


# def task(queue_in, queue_out):
    

#     while not queue_in.is_empty():

#         frame_nr, frame = queue_in.get()
#         frame_out = detector.detect_objects(frame)
#         queue_out.put((frame_nr, frame_out))
#         queue_in.task_done()



# def process_frame(detector, queue_in):
#     frame_nr, frame = queue_in.get()
#     frame_out = detector.detect_objects(frame)
#     queue_in.task_done()
#     return frame_nr, frame_out


input_stream = InputStream(os.environ['INPUT_STREAM_URL'], 10000)
input_stream.start()

fps = input_stream.getFPS()
output_file = OutputFile(abspath(os.environ['OUTPUT_FILE']), 'XVID', {
    'fps': fps,
    'frameSize': input_stream.video_size
})

output_stream = OutputStream(
    os.environ['OUTPUT_STREAM_URL'],
    input_cfg={"format": "rawvideo", "s": "{}x{}".format(*input_stream.video_size)},
    # filter_cfg={"fps": fps / 2, "round": "up"},
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
    
    logger.info('Start writing video')
    
    n_workers = os.environ.get('N_WORKERS', 5)
    logger.debug("Start pool")

    detector = ObjectDetection()

    # with Pool(n_workers) as pool:

    while not input_stream.is_empty:

        logger = log_to_stderr('DEBUG')
        # logger.debug(f'{input_stream.queue.qsize()} items left in the queue')

        # tasks = [
        #     pool.apply_async(process_frame, (detector, input_stream.queue))
        #     for _ in range(n_workers)
        # ]

        frame_nr, frame = input_stream.read()
        frame_out = detector.detect_objects(frame)

        # for task in tasks:
        #     task.wait()
        #     frame_nr, frame_out = task.get()
        #     _logger.debug(f"Finished frame n°{frame_nr}")

        for output in outputs:
            output.write_frame(frame_out)

except KeyboardInterrupt:

    logger.info('Cleaning outputs')
    for output in outputs:
        output.clean()
    detector.clean()

