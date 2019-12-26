FROM python:3

COPY . /app
WORKDIR /app
RUN apt-get update
RUN apt-get -y upgrade
RUN apt install -y openssh-server
RUN apt install -y openssh-client
#RUN apt-get -y install sshpass
RUN pip install requests
RUN pip install future
RUN pip install colorlog
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download xx
RUN python -m spacy download it_core_news_sm
RUN python -m spacy download de_core_news_sm
RUN python -m spacy download es_core_news_sm
RUN python -m spacy download nl_core_news_sm
RUN apt-get install python3-lxml -y
# RUN sed -i -e "\$aStrictHostKeyChecking no" /etc/ssh/ssh_config
# RUN chmod a+x ./tunnel_kafka.sh
# RUN chmod a+x ./tunnel_elastic.sh

EXPOSE 5001
EXPOSE 9092
EXPOSE 9220	

#ENTRYPOINT ./docker-entrypoint.sh

CMD [ "python", "./init_services.py" ]