ARG TAG=devel

FROM docker.io/qmeeus/object-detection:$TAG

COPY requirements.txt ./
RUN  python -m pip install --upgrade pip && \
    pip install -r requirements.txt

ARG user=tensorflow
ARG user_id=1000
RUN useradd --uid $user_id --group video --shell /bin/bash --create-home $user
USER $user

WORKDIR /home/$user

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV QT_X11_NO_MITSHM=1

COPY --chown=$user:users ./models ./models
COPY --chown=$user:users ./realtime_object_detection ./realtime_object_detection
COPY --chown=$user:users ./old ./old

# CMD python -m realtime_object_detection
# CMD python -m realtime_object_detection.deepdream
CMD bash old/docker-entrypoint.sh