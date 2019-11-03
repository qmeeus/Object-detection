import numpy as np
import cv2
import ffmpeg
from threading import Thread
from multiprocessing import Queue, Pool
from urllib.parse import urljoin

from app.detection import worker
from app.utils.logger import logger


class RTMPStream:

    def __init__(self, url):

        self.stream = cv2.VideoCapture()
        self.stream.open(url)
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


class Streamer:

    def __init__(self, rtmp_server, stream_in, stream_out, queue_size=5, num_workers=2):

        self.rtmp_server = rtmp_server
        self.input_url = f"{rtmp_server}/{stream_in}"
        self.output_url = f"{rtmp_server}/{stream_out}"

        self.queue_size = queue_size
        self.num_workers = num_workers

        self.input_queue = Queue(maxsize=self.queue_size)
        self.output_queue = Queue(maxsize=self.queue_size)
        self.pool = Pool(self.num_workers, worker, (self.input_queue, self.output_queue))

        self.stream = RTMPStream(self.input_url)

        self._process = None

        self._is_started = False

    def start(self):

        logger.debug("Start process")
        logger.debug(f"{self.input_url} -> {self.output_url}")

        self._process = (
            ffmpeg
            .input(self.input_url)
            .output(self.output_url, format='flv')
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

        count_frame = 0
        while True:
            ret, frame = self.stream.read()
            count_frame += 1
            if ret:
                self.input_queue.put(frame)
                output_rgb = cv2.cvtColor(self.output_queue.get(), cv2.COLOR_RGB2BGR)

                self._process.stdin.write(output_rgb.astype(np.uint8).tobytes())

            else:
                logger.info("Enf of frame")
                break

            if not self._is_started:
                self._is_started = True

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        return self

    def __del__(self):

        logger.debug("Cleaning...")

        self._process.stdin.close()
        self._process.wait()

        self.pool.terminate()
        cv2.destroyAllWindows()
   
