#!/bin/bash -e

tag=devel-gpu-py3
repo=docker.io
user=qmeeus

docker build -t $repo/$user/object-detection:$tag --build-arg TAG=$tag .
docker login -u $user $repo 
docker push $repo/$user/object-detection
