
FROM python:3.6-slim
ARG user
ARG password
ADD requirements.txt /
RUN pip install --upgrade --extra-index-url http://$user:$password@206.189.119.125:8080 --trusted-host 206.189.119.125 -r /requirements.txt
ADD . /fake-news-detection
ENV PYTHONPATH=$PYTHONPATH:/fake-news-detection
WORKDIR /fake-news-detection/services/
CMD python Services.py
