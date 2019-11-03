#!/bin/bash

ffmpeg -i $1 \
    -crf 30 \
    -preset veryslow \
    -acodec aac \
    -strict experimental \
    -ac 2 -b:a 96k \
    -vcodec libx264 -r 25 -b:v 500k -f flv \
    'rtmp://10.1.129.22/live/cam2'

# cvlc  -vvv outputs/output.avi \
#     --sout '#transcode{vcodec=h264,scale=Auto,width=1280,height=720,acodec=aac,ab=128,channels=2}:std{access=rtmp,mux=ffmpeg{mux=flv},dst=rtmp://10.1.129.22/live/cam2}'
