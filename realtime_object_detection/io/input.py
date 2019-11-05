import cv2
import ffmpeg
from time import sleep
from threading import Thread
from queue import PriorityQueue
# from multiprocessing import Queue

from realtime_object_detection.utils.logger import logger


class InputStream:

    def __init__(self, src, max_queue_size):

        self.src = src
        self.stream = cv2.VideoCapture()
        self.stream.open(self.src)
        self.queue = PriorityQueue(maxsize=max_queue_size)
        # self.queue = Queue(maxsize=max_queue_size)

        self.video_size = 0, 0

        self.is_streaming = False
        self.frame_nr = 0

    def start(self):

        while True:
            size_probed = self.get_video_size()
            if size_probed == (0, 0):
                logger.info('No input stream...')
                sleep(1.)
            else:
                logger.debug('Probed size: {}x{}'.format(*size_probed))
                self.video_size = size_probed
                self.start_capture()
                break

        thread = Thread(target=self.update)
        thread.start()

        return self

    def update(self):
        while self.is_streaming:
            if self.queue.full():
                logger.debug('The queue is full')
                sleep(1.)
                continue

            ret, frame = self.stream.read()

            if not ret:
                self.stop_capture()

            self.frame_nr += 1
            self.queue.put((self.frame_nr, frame))
            
    def read(self):
        return self.queue.get()
        
    def start_capture(self):
        logger.info('Input stream started')
        self.is_streaming = True

    def stop_capture(self):
        logger.info('Stream finished')
        self.is_streaming = False

    def getFPS(self):
        # Get the frame rate of the frames
        return int(self.stream.get(cv2.CAP_PROP_FPS))

    def get_video_size(self):
        logger.debug(f'Probing {self.src}')
        probe = ffmpeg.probe(self.src)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        # width, height = 1920, 1080
        return width, height

    @property
    def is_empty(self):
        return self.queue.qsize() == 0