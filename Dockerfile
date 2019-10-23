FROM python:3.6-slim
ARG user
ARG password
#RUN apt-get update
#RUN apt-get install python3.6-dev -y
RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y libicu-dev
ADD requirements.txt /
RUN pip install --upgrade --extra-index-url http://$user:$password@distribution.livetech.site --trusted-host distribution.livetech.site -r /requirements.txt
RUN python3 -m spacy download en_core_web_md
RUN python3 -m spacy download it_core_news_sm
RUN python3 -m spacy download es_core_news_md
RUN python3 -m spacy download nl_core_news_sm
RUN python3 -m nltk.downloader stopwords
######## TREETAGGER
RUN mkdir /treetagger
RUN apt-get update && apt-get install perl -y
WORKDIR /treetagger 
ENV SOURCE http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data
ADD $SOURCE/install-tagger.sh /treetagger
ADD $SOURCE/tree-tagger-linux-3.2.1.tar.gz /treetagger
ADD $SOURCE/tagger-scripts.tar.gz /treetagger
#ADD $SOURCE/french-par-linux-3.2-utf8.bin.gz /treetagger
ADD $SOURCE/italian.par.gz /treetagger
ADD $SOURCE/english.par.gz /treetagger
ADD $SOURCE/spanish.par.gz /treetagger
#ADD $SOURCE/german-par-linux-3.2-utf8.bin.gz /treetagger
#ADD $SOURCE/french-chunker-par.gz /treetagger
ADD $SOURCE/english-chunker.par.gz /treetagger
#ADD $SOURCE/german-chunker-par.gz /treetagger
ADD $SOURCE/spanish-chunker.par.gz /treetagger
RUN chmod u+x /treetagger/install-tagger.sh
WORKDIR /treetagger
RUN tar xvzf /treetagger/tree-tagger-linux-3.2.1.tar.gz
RUN /treetagger/install-tagger.sh
ENV PATH $PATH:/treetagger/bin:/treetagger/cmd

#RUN pip install --upgrade --extra-index-url http://$user:$password@206.189.119.125:8080 --trusted-host 206.189.119.125 -r /requirements.txt
ADD . /fandango-fake-news
ENV PYTHONPATH=$PYTHONPATH:/fandango-fake-news
WORKDIR /fandango-fake-news/fake_news_detection/services/
#CMD python ServicesFandangoAnnotation.py
CMD python ServicesFandango.py

