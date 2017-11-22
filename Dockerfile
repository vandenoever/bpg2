# convenience Dockerfile for running bpg2
#   docker build -t bpg2 .
#   docker run -ti -p 5000:5000 --rm bpg2
#   browse to http://127.0.0.1:5000

FROM debian:stretch

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
  sqlite3 wget python-pip gnupg gcc libpython2.7-dev

# set up bpg2 directory
RUN mkdir /bpg2
WORKDIR /bpg2
# install multichain
RUN wget https://www.multichain.com/download/multichain-1.0.2.tar.gz
RUN tar -xvzf multichain-1.0.2.tar.gz
# WORKDIR /bpg2/multichain-1.0.2
# RUN mv multichaind multichain-cli multichain-util /usr/local/bin

RUN pip install -U pip setuptools wheel
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# patch a bug in Savoir
RUN echo '# -*- coding: utf-8 -*-\nfrom Savoir import *' > /usr/local/lib/python2.7/dist-packages/Savoir/__init__.py
COPY . .

# make port 5000 open
EXPOSE 5000
ENTRYPOINT ["./go.sh"]
ENTRYPOINT ["/bin/bash", "-l"]
