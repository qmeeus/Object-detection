import ffmpeg
import cv2


class OutputStream:

    def __init__(self, dest, input_cfg, output_cfg):
        self.dest = dest

        self.process = (
            ffmpeg
            .input('pipe:', **input_cfg)
            # .filter('fps', **filter_cfg)
            .output(dest, **output_cfg)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

    def write_frame(self, frame):
        self.process.stdin.write(frame)

    def clean(self):
        self.process.stdin.close()
        self.process.wait()


class OutputFile:
    
    def __init__(self, filename, codec, cfg):
        self.filename = filename

        self.video_writer = cv2.VideoWriter(
            filename,
            cv2.VideoWriter_fourcc(*codec),
            **cfg
        )

    def write_frame(self, frame):
        self.video_writer.write(frame)

    def clean(self):
        self.video_writer.release()
