#!/bin/bash -e


cd models
wget http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz
tar -xvf *.tar.gz
rm *.tar.gz
