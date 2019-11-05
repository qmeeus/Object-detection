ARG TAG

FROM tensorflow/tensorflow:$TAG

ENV DEBIAN_FRONTEND=noninteractive

ENV PY_VERSION=3.6.1
ENV PY_V=3.6

WORKDIR /tmp

RUN add-apt-repository ppa:jonathonf/python-3.6 && apt update && apt install -y python3 \
    python3-dev \
    python-pil \
    python-lxml \
    python-tk \
    build-essential \
    cmake \ 
    git \ 
    libgtk2.0-dev \ 
    pkg-config \ 
    libavcodec-dev \ 
    libavformat-dev \ 
    libswscale-dev \ 
    libtbb2 \
    libtbb-dev \ 
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    x11-apps \
    wget \
    ffmpeg \
    unzip \
    && rm -rf /var/lib/apt/lists/* 

RUN git clone -q https://github.com/tensorflow/models /usr/local/lib/python$PYV/dist-packages/tensorflow/models
RUN wget -q -P /usr/local/src/ https://github.com/google/protobuf/releases/download/v$PY_VERSION/protobuf-python-$PY_VERSION.tar.gz

RUN cd /usr/local/src/ \
 && tar xf protobuf-python-$PY_VERSION.tar.gz \
 && rm protobuf-python-$PY_VERSION.tar.gz \
 && cd /usr/local/src/protobuf-$PY_VERSION/ \
 && ./configure \
 && make \
 && make install \
 && ldconfig \
 && rm -rf /usr/local/src/protobuf-$PY_VERSION/

RUN apt-get autoremove -y && apt-get autoclean -y

ENV PYTHONPATH "$PYTHONPATH:/usr/local/lib/python$PYV/dist-packages/tensorflow/models/research:/usr/local/lib/python$PYV/dist-packages/tensorflow/models/research/slim"
RUN cd /usr/local/lib/python$PYV/dist-packages/tensorflow/models/research \
    && protoc object_detection/protos/*.proto --python_out=.

RUN pip install ffmpeg-python

