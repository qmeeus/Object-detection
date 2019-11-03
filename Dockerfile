ARG IMAGE=gpu

FROM object-detection:$IMAGE

COPY requirements.txt ./
RUN  python -m pip install --upgrade pip && \
    pip install -r requirements.txt

ARG user=tensorflow
ARG user_id=1000
RUN useradd --uid $user_id --group video --shell /bin/bash --create-home $user
USER $user

# Setting up working directory 
WORKDIR /home/$user

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV QT_X11_NO_MITSHM=1

COPY --chown=$user:users ./app ./app
COPY --chown=$user:users ./models ./models

COPY --chown=$user:users docker-entrypoint.sh .
RUN chmod 755 ./docker-entrypoint.sh
CMD ./docker-entrypoint.sh