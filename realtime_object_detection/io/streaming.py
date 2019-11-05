import sys
import numpy as np
import cv2
import ffmpeg
import subprocess
import logging
from time import sleep
from threading import Thread
from queue import PriorityQueue
from multiprocessing import Queue, Pool, Process, log_to_stderr
from urllib.parse import urljoin

from realtime_object_detection.detection import ObjectDetection
from realtime_object_detection.utils.logger import logger



class Streamer:

    RTMP = False
    FILE = True
    STDOUT = False

    def __init__(self, 
        rtmp_server, 
        stream_in, 
        stream_out, 
        process_frame,
        queue_size=1000, 
        num_workers=1):

        self.rtmp_server = rtmp_server
        self.input_url = f"{rtmp_server}/{stream_in}"
        # self.input_url = "/home/tensorflow/videos/inputs/train-crossing.mkv"
        self.output_url = f"{rtmp_server}/{stream_out}"
        self.output_file = "/home/tensorflow/videos/outputs/video.mp4"

        self.process_frame = process_frame

        self.queue_size = queue_size
        self.num_workers = num_workers

        self.stream_in = InputStream(self.input_url, self.queue_size)
        self.width, self.height = self.stream_in.get_video_size()

        self.outputs = {
            'rtmp': self.create_process_out(f"{self.output_url}") if self.RTMP else None,
            'file': self.create_video_writer(f"{self.output_file}") if self.FILE else None,
            'stdout': sys.stdout if self.STDOUT else None
        }

        self.writers = {
            'rtmp': self.outputs['rtmp'].stdin if self.outputs['rtmp'] else None,
            'file': self.outputs['file'] if self.outputs['file'] else None,
            'stdout': self.outputs['stdout'].buffer if self.outputs['stdout'] else None
        }

        self.output_queue = PriorityQueue(maxsize=self.queue_size)
        self.pool = Pool(self.num_workers)

        self.frame_nr = 0
        self._pool_started = False

    def start(self):

        logger.debug("Start streamer")
        logger.debug(f"{self.input_url} --> {self.output_url}")
        logger.debug(f"Video size: {self.width}x{self.height}")

        self.stream_in.start()
        self.stream_out.start()
        # logger.debug(f'### L123 {self.stream_in.queue.qsize()}')

        while True:

            # logger.debug(f'### L127 {self.output_queue.qsize()}')

            if not self.stream_in.queue.qsize():
                logger.info('No frame to process')
                sleep(1)
                continue

            # if not self._pool_started:
            #     logger.info('Starting to process the frames')
            #     # self.pool.apply_async(self.process_frame_async, self.stream_in.queue)
            #     self._pool_started = True
            #     sleep(1.)
            #     logger.debug(f'### L139 {self.output_queue.qsize()}')
                

            if not self.output_queue.empty():
                self.write_frame()

            if self.output_queue.empty() and self.stream_in.stopped:
                log = f'Frames in: {self.stream_in.frame_nr}   Frames out: {self.frame_nr}'
                logger.info(log)
                break

        self.clean()
        return self

    def write_frame(self):
        frame_nr, bytes_out = self.output_queue.get()
        logger.debug(f"Frame #{frame_nr} processed")
        for name, output in self.outputs.items():
            if hasattr(output, 'write'):
                logger.debug(f'Writing to {name}')                
                output.write(bytes_out)

    def process_frame(self):
        print('Processing frame')
        logger = log_to_stderr(logging.DEBUG)
        frame_nr, frame_in = self.stream_in.queue.get()
        logger.debug(f'Input shape: {frame_in.shape}')
        rgb_out = cv2.cvtColor(frame_in, cv2.COLOR_RGB2BGR)
        frame_out = self.process_frame(rgb_out)
        logger.debug(f'Output shape: {frame_out.shape}')
        bytes_out = frame_out.astype(np.uint8).tobytes()
        return frame_nr, bytes_out

    def process_frame_async(self):
        frame_nr, bytes_out = self.process_frame
        self.output_queue.put((frame_nr, bytes_out))

    def create_process_out(self, url):
        logger.debug('Starting ffmpeg output process')

        input_opts = {
            'format': 'rawvideo', 
            's': f'{self.width}x{self.height}',
            # 'pix_fmt': 'rgb24'
        }
        
        output_opts = {
            'format': 'h264',
            'vcodec': 'libx264',
            # 'preset': 'slower',
            # 'pix_fmt': 'rgb24',
        }
        
        return (
            ffmpeg
            .input('pipe:', **input_opts)
            .output(url, **output_opts) 
            .overwrite_output()
            .run_async(pipe_stdin=True)

        )

    def create_video_writer(self, filename):
        return cv2.VideoWriter(
            filename,
            cv2.VideoWriter_fourcc(*'mp4v'), 
            self.stream_in.getFPS() / self.num_workers,
            self.stream_in.get_video_size()
        )

    def clean(self):
        logger.debug("Cleaning...")
        if self.writers['rtmp']:
            self.writers['rtmp'].close()
            self.outputs['rtmp'].wait()

        if self.outputs['file']:
            self.outputs['file'].release()
        
        self.pool.terminate()
        cv2.destroyAllWindows()

    def get_video_size(self):
        # probe = ffmpeg.probe(self.url)
        # video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        # width = int(video_info['width'])
        # height = int(video_info['height'])
        width, height = 1920, 1080
        return width, height
