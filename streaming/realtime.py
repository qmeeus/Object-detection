import numpy as np
import multiprocessing
from multiprocessing import Queue, Pool
import cv2, os
import subprocess
import ffmpeg

from utils.app_utils import *
from utils.detection import *


def sh(*args):
    with subprocess.Popen(args, stdout=subprocess.PIPE) as proc:
        out = proc.stdout.read()
        return out.decode('utf-8')

def realtime(args):
    """
    Read and apply object detection to input real time stream (webcam)
    """

    is_started = 0

    filename = 'outputs/{}.avi'.format(args["output_name"])
    if os.path.exists(filename):
        os.remove(filename)

    args = args.copy()

    # If display is off while no number of frames limit has been define: set diplay to on
    if((not args["display"]) & (args["num_frames"] < 0)):
        print("\nSet display to on\n")
        args["display"] = 1

    # Set the multiprocessing logger to debug if required
    if args["logger_debug"]:
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(multiprocessing.SUBDEBUG)

    # Multiprocessing: Init input and output Queue and pool of workers
    input_q = Queue(maxsize=args["queue_size"])
    output_q = Queue(maxsize=args["queue_size"])
    pool = Pool(args["num_workers"], worker, (input_q, output_q))

    # created a threaded video stream and start the FPS counter
    vs = WebcamVideoStream(src=args["input_device"]).start()
    fps = FPS().start()

    # Define the output codec and create VideoWriter object
    if args["output"]:
        out = cv2.VideoWriter(filename,
                              cv2.VideoWriter_fourcc(*'XVID'), 
                              vs.getFPS() / args["num_workers"], 
                              (vs.getWidth(), vs.getHeight()))


    # Start reading and treating the video stream
    if args["display"] > 0:
        print()
        print("=====================================================================")
        print("Starting video acquisition. Press 'q' (on the video windows) to stop.")
        print("=====================================================================")
        print()

    process = (
        ffmpeg
        .input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(vs.getWidth(), vs.getHeight()))
        .output('rtmp://10.1.129.22/live/cam2', format='flv', preset='slower', movflags='faststart', pix_fmt='rgb24')
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )

    countFrame = 0
    while True:
        # Capture frame-by-frame
        ret, frame = vs.read()
        countFrame = countFrame + 1
        if ret:
            input_q.put(frame)
            output_rgb = cv2.cvtColor(output_q.get(), cv2.COLOR_RGB2BGR)

            process.stdin.write(
                output_rgb
                .astype(np.uint8)
                .tobytes()
            )

            # write the frame
            if args["output"]:
                out.write(output_rgb)

            # Display the resulting frame
            if args["display"]:
                ## full screen
                if args["full_screen"]:
                    cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
                    cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow("frame", output_rgb)

                fps.update()
            elif countFrame >= args["num_frames"]:
                print('End of frame')
                break

        else:
            print('End of stream')
            break

        if not is_started:
            is_started = 1
            # subprocess.Popen(['bash', 'stream.sh', '-'], stdout=subprocess.PIPE)
            # sh('bash', 'stream.sh', filename)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    process.stdin.close()
    process.wait()

    # When everything done, release the capture
    fps.stop()
    pool.terminate()
    vs.stop()
    if args["output"]:
        out.release()
    cv2.destroyAllWindows()

