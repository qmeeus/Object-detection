import numpy as np
import cv2
import ffmpeg
import subprocess
from threading import Thread
from multiprocessing import Queue, Pool
from urllib.parse import urljoin

from realtime_object_detection.detection import ObjectDetection
from realtime_object_detection.utils.logger import logger


class RTMPStream:

    def __init__(self, url):

        self.url = url
        self.stream = cv2.VideoCapture()
        self.stream.open(self.url)
        self.grabbed, self.frame = self.stream.read()

        self._stopped = False

    def start(self):
        Thread(target=self.update).start()
        
    def update(self):
        while not self._stopped:
            self.grabbed, self.frame = self.stream.read()

    def read(self):
        return self.grabbed, self.frame

    def stop(self):
        self._stopped = True

    def getFPS(self):
        # Get the frame rate of the frames
        return int(self.stream.get(cv2.CAP_PROP_FPS))

    def get_video_size(self):
        # probe = ffmpeg.probe(self.url)
        # video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        # width = int(video_info['width'])
        # height = int(video_info['height'])
        width, height = 1920, 1080
        return width, height


class Streamer:

    def __init__(self, 
        rtmp_server, 
        stream_in, 
        stream_out, 
        process_frame,
        queue_size=5, 
        num_workers=2):

        self.rtmp_server = rtmp_server
        self.input_url = f"{rtmp_server}/{stream_in}"
        self.output_url = f"{rtmp_server}/{stream_out}"
        self.output_file = "outputs/video.mp4"

        self.process_frame = process_frame

        self.queue_size = queue_size
        self.num_workers = num_workers

        self.stream = RTMPStream(self.input_url)
        self.width, self.height = self.stream.get_video_size()

        self.input_queue = Queue(maxsize=self.queue_size)
        self.output_queue = Queue(maxsize=self.queue_size)
        self.pool = Pool(self.num_workers, self.worker)

        self._process = None
        self._is_started = False

    def start(self):

        logger.debug("Start streamer")
        logger.debug(f"{self.input_url} --> {self.output_url}")
        logger.debug(f"Video size: {self.width}x{self.height}")

        # process_in = self.create_process_in()
        process_out = self.create_process_out()

        self.stream.start()
        
        count_frame = 0
        while True:
            count_frame += 1
            ret, bytes_in = self.stream.read()
            # in_bytes = process_in.stdout.read(self.width * self.height * 3)
            if not bytes_in:
                logger.info("End of frame")
                break

            self.input_queue.put(bytes_in)
            process_out.stdin.write(self.output_queue.get())
            # output_video.write(output_rgb)

            if not self._is_started:
                self._is_started = True

        logger.debug("Cleaning...")
        process_out.stdin.close()
        # process_in.wait()
        process_out.wait()
        self.pool.terminate()
        cv2.destroyAllWindows()
        return self

    def worker(self):
        while True:
            bytes_in = self.input_queue.get()
            frame_in = np.frombuffer(bytes_in, np.uint8).reshape([self.height, self.width, 3])
            logger.debug(f'Frame length: {len(frame_in)}')
            rgb_out = cv2.cvtColor(frame_in, cv2.COLOR_RGB2BGR)
            frame_out = self.process_frame(rgb_out)
            bytes_out = frame_out.astype(np.uint8).tobytes()
            self.output_queue.put(bytes_out)

    def create_process_in(self):
        logger.debug('Starting ffmpeg input process')
        return (
            ffmpeg
            .input(self.input_url)
            .output('pipe:', format='rawvideo', pix_fmt='rgb24', vframes=8)
            .run_async(pipe_stdout=True)
        )

    def create_process_out(self):
        logger.debug('Starting ffmpeg output process')
        return (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{self.width}x{self.height}')
            .output(self.output_url, pix_fmt='rgb24', s=f'{self.width}x{self.height}')
            .overwrite_output()
            .run_async(pipe_stdin=True)

        )

    def create_process_async(self):

        input_opts = dict()  #dict(format='rawvideo', pix_fmt='rgb24')
        output_opts = dict(format='flv', preset='slower', movflags='faststart', pix_fmt='rgb24')

        return (
            ffmpeg
            .input(self.input_url, **input_opts)
            .output(self.output_url, **output_opts)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

    # def create_video_writer(self):
    #     return cv2.VideoWriter(
    #         self.output_file,
    #         cv2.VideoWriter_fourcc(*'XVID'), 
    #         self.stream.getFPS() / self.num_workers,
    #         self.stream.get_video_size()
    #     )
