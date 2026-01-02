FROM dtcooper/raspberrypi-os:python

RUN apt-get update && apt-get install -y \
      pipx \
    && \
    pipx install uv
