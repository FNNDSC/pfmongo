#
# Dockerfile for persair.
#
# Build with
#
#   docker build -t <name> .
#
# For example if building a local version, you could do:
#
#   docker build --build-arg UID=$UID -t local/persair .
#
# In the case of a proxy (located at say 10.41.13.4:3128), do:
#
#    export PROXY="http://10.41.13.4:3128"
#    docker build --build-arg http_proxy=$PROXY --build-arg UID=$UID -t local/persair .
#
# To run an interactive shell inside this container, do:
#
#   docker run -ti --entrypoint /bin/bash local/persair
#
# To pass an env var HOST_IP to the container, do:
#
#   docker run -ti -e HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}') --entrypoint /bin/bash local/persair
#
FROM docker.io/python:3.11.0-slim-bullseye

LABEL DEVELOPMENT="                                                         \
    docker run --rm -it                                                     \
    -v $PWD/persair:/persair:ro  local/persair                              \
"

WORKDIR /pfmongo

ENV DEBIAN_FRONTEND=noninteractive

COPY . $WORKDIR

# COPY requirements.txt $WORKDIR/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install tzlocal
RUN pip install ipython
# COPY . $WORKDIR
# COPY setup.py $WORKDIR/setup.py
RUN pip install -U ./

RUN apt update                              && \
    apt-get install -y apt-transport-https  && \
    apt -y install vim telnet netcat procps

CMD [ "pfmongo", "--man" ]
