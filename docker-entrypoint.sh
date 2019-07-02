#!/bin/bash
#src:

mkfifo /tmp/stream

python3 main.py \
    --display 1 --output 0 \
    --num-workers 2 -q-size 150 \
    --input-device rtmp://10.1.129.22/live/RamonStream \
    # | ffmpeg \
    # -crf 30 \
    # -preset veryslow \
    # -acodec aac \
    # -strict experimental \
    # -ac 2 -b:a 96k \
    # -vcodec libx264 -r 25 -b:v 500k -f flv \
    # 'rtmp://10.1.129.22/live/cam2'

