#!/bin/bash
#src: rtmp://10.1.129.22/live/RamonStream
python3 main.py \
    --display 1 --output 1 \
    --num-workers 20 -q-size 150 \
    --input-device test.mp4

