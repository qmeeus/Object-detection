FROM tensorflow/tensorflow:nightly-devel-py3

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
#    libjasper-dev \
#    libdc1394-22-dev \
    x11-apps \
    wget \
    vim \
    ffmpeg \
    unzip \
    && rm -rf /var/lib/apt/lists/* 

COPY requirements.txt ./
RUN  pip install -U pip && pip install -r requirements.txt

# Install tensorflow models object detection
RUN PY_VERSION=$(python --version | cut -d" " -f2)
RUN PYV=$(echo $PY_VERSION | cut -d"." -f1,2)
RUN echo $(python --version | cut -d" " -f2) $PY_VERSION $PYV
RUN git clone -q https://github.com/tensorflow/models /usr/local/lib/python$PYV/dist-packages/tensorflow/models
RUN wget -q -P /usr/local/src/ https://github.com/google/protobuf/releases/download/v$PY_VERSION/protobuf-python-$PY_VERSION.tar.gz

# Download & build protobuf-python
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

# Set TF object detection available
ENV PYTHONPATH "$PYTHONPATH:/usr/local/lib/python$PYV/dist-packages/tensorflow/models/research:/usr/local/lib/python$PYV/dist-packages/tensorflow/models/research/slim"
RUN cd /usr/local/lib/python$PYV/dist-packages/tensorflow/models/research \
    && protoc object_detection/protos/*.proto --python_out=.


ARG user_id
RUN useradd --uid $user_id --group video --shell /bin/bash --create-home patrick
USER patrick

# Setting up working directory 
RUN mkdir /home/patrick/app
WORKDIR /home/patrick/app

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY --chown=patrick:users docker-entrypoint.sh .
RUN chmod 755 ./docker-entrypoint.sh
CMD bash ./docker-entrypoint.sh

