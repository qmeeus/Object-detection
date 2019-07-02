#!/bin/bash

python3 main.py \
    --display 1 --output 1 \
    --num-workers 20 -q-size 150 \
    --input-device rtmp://10.1.129.22/live/RamonStream

