import cv2
import ffmpeg
from time import sleep
from threading import Thread
from queue import PriorityQueue
# from multiprocessing import Queue

from realtime_object_detection.utils.logger import logger


class InputStream:

    def __init__(self, src, max_queue_size, fps=None):

        self.src = src
        self.fps = fps
        self.stream = cv2.VideoCapture()
        self.stream.set(cv2.CAP_PROP_FPS, 10)
        self.stream.open(self.src)
        self.queue = PriorityQueue(maxsize=max_queue_size)
        # self.queue = Queue(maxsize=max_queue_size)

        self.video_size = 0, 0

        self.frame_nr = 0
        self.is_streaming = False

    def start(self):

        while True:

            size_probed = self.get_video_size()
            if size_probed == (0, 0):
                logger.info('No input stream...')
                logger.debug('Stream is {}open'.format('not ' if self.stream.isOpened() else ''))
                sleep(1.)
            else:

                logger.debug('Probed size: {}x{}'.format(*size_probed))
                self.video_size = size_probed
                self.start_capture()
                assert self.is_streaming
                break

        thread = Thread(target=self.update)
        thread.start()

        return self

    def update(self):

        while True:

            if self.queue.full():
                logger.debug('The queue is full')
                sleep(1.)
                continue

            elif not self.is_streaming:
                sleep(2.)
                continue

            else:
                ret, frame = self.stream.read()

                if ret:
                    self.frame_nr += 1
                    self.queue.put((self.frame_nr, frame))
                    if self.fps:
                        sleep(1 / self.fps)

                else:
                    self.stop_capture()

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
    def size(self):
        return self.queue.qsize()

    @property
    def is_empty(self):
        return self.size == 0

    # @property
    # def is_streaming(self):
    #     return self.stream.isOpened()

