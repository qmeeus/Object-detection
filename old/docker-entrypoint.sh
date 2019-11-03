#!/bin/bash

mkfifo /tmp/stream

python3 -m old.main \
    --output 1 \
    --num-workers 10 -q-size 150 \
    --input-stream rtmp://nginx-rtmp/live/cam \
    --output-stream rtmp://nginx-rtmp/live/out #\
    # --display 1 \
    # | ffmpeg \
    # -crf 30 \
    # -preset veryslow \
    # -acodec aac \
    # -strict experimental \
    # -ac 2 -b:a 96k \
    # -vcodec libx264 -r 25 -b:v 500k -f flv \
    # 'rtmp://10.1.129.22/live/cam2'

