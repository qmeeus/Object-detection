#!/bin/bash

#xhost +local:docker
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -

docker run -m 4GB -it --rm \
    -e DISPLAY=$DISPLAY -e XAUTHORITY=$XAUTH \
    -v $XSOCK:$XSOCK -v $XAUTH:$XAUTH -v $PWD:/home/patrick/app \
    realtime-object-detection:latest

#xhost -local:docker
