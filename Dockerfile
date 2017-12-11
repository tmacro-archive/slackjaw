FROM tmacro/python:3

ADD requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

ADD . /app
ADD ./s6 /etc

