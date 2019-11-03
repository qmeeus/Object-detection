#!/bin/bash -e

tag=devel-gpu-py3
repo=docker.io
user=qmeeus

docker build -t $repo/$user/object-detection:$tag --build-arg TAG=$tag .
docker $repo login -u $user
docker push $repo/$user/object-detection
