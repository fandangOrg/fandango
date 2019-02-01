
FROM python:3.6-slim
ARG user
ARG password
#RUN apt-get update
#RUN apt-get install python3.6-dev -y
ADD requirements.txt /
RUN python3 -m spacy download en_core_web_md
RUN python3 -m spacy download it_core_news_sm
RUN python3 -m spacy download es_core_news_md
RUN python3 -m spacy download nl_core_news_sm
RUN python3 -m nltk.downloader stopwords
RUN pip install --upgrade --extra-index-url http://$user:$password@206.189.119.125:8080 --trusted-host 206.189.119.125 -r /requirements.txt
ADD . /fandango-fake-news
ENV PYTHONPATH=$PYTHONPATH:/fandango-fake-news
WORKDIR /fandango-fake-news/fake_news_detection/services/
CMD python Services.py
