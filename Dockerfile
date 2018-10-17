
FROM python:3.6-slim
ARG user
ARG password
ADD requirements.txt /
RUN pip install --upgrade --extra-index-url http://$user:$password@94.23.7.153:8085 --trusted-host 94.23.7.153 -r /requirements.txt
ADD . /fake-news-detection
ENV PYTHONPATH=$PYTHONPATH:/fake-news-detection
WORKDIR /fake-news-detection/
CMD bash
