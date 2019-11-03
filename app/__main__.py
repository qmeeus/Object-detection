import os
from app.streaming import Streamer


stream = Streamer(
    rtmp_server=os.environ['RTMP_SERVER'],
    stream_in=os.environ['STREAM_IN'],
    stream_out=os.environ['STREAM_OUT'],
    queue_size=20,
    num_workers=5
)

stream.start()
del stream
