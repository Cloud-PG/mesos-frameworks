FROM python:2.7

WORKDIR /usr/src/app

RUN apt-get install -y gcc
RUN pip install --no-cache-dir pymesos 

COPY scheduler.py .
COPY process.py /usr/local/lib/python2.7/site-packages/pymesos/process.py
