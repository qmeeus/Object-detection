import os
from time import time, sleep

from realtime_object_detection.io import InputStream
from realtime_object_detection.utils.logger import logger

FPS = 10

input_stream = InputStream(os.environ['INPUT_STREAM_URL'], 1000, FPS)
input_stream.start()

start = time()
frames = 0
while True:
    t = time() - start
    frames = input_stream.size
    logger.warn(f"Elasped: {t:.4f}  frames: {frames}  fps: {frames / t:.2f}")
    sleep(1)

    if t > 10:
        break
