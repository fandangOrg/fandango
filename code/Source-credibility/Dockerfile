FROM ubuntu
COPY . /app
WORKDIR /app
RUN apt-get update
#add-apt-repository ppa:deadsnakes/ppa
#RUN apt install -y software-properties-common
#RUN apt-get install python3.6
#RUN apt-get install -y software-properties-common
RUN apt-get install -y curl
RUN apt-get install -y gnupg2
#RUN apt-get update
RUN apt-get install -y python3.6
RUN apt install -y python3-pip
#RUN add-apt-repository ppa:jonathonf/python-3.6
#RUN apt-get -y upgrade
#RUN apt-get update
RUN apt install -y openjdk-8-jdk
RUN apt-get install -y apt-transport-https
#RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt install -y wget
#RUN wget --no-check-certificate -O - https://debian.neo4j.org/neotechnology.gpg.key |  apt-key add -
#RUN echo 'deb https://debian.neo4j.org/repo stable/' |  tee -a /etc/apt/sources.list.d/neo4j.list
RUN apt update
#RUN apt-get install -y neo4j

#RUN apt-get install python3.6
#RUN  cp /app/neo4j_libraries/* /var/lib/neo4j/plugins
RUN pip3 install requests
RUN pip3 install future
RUN pip3 install colorlog
RUN pip3 install -r requirements.txt
RUN apt-get install python3-lxml python3-dev -y
# RUN sed -i -e "\$aStrictHostKeyChecking no" /etc/ssh/ssh_config
# RUN chmod a+x ./tunnel_kafka.sh
# RUN chmod a+x ./tunnel_elastic.sh
#RUN echo 'dbms.security.procedures.unrestricted=apoc.*, algo.*' | tee -a /etc/neo4j/neo4j.conf
#RUN echo 'dbms.security.procedures.whitelist=apoc.*, algo.*'    | tee -a /etc/neo4j/neo4j.conf
#RUN echo 'dbms.allow_format_migration=true'                     | tee -a /etc/neo4j/neo4j.conf
#RUN echo 'dbms.connectors.default_listen_address=0.0.0.0'	| tee -a /etc/neo4j/neo4j.conf
#RUN echo 'dbms.connector.bolt.enabled=true'                     | tee -a /etc/neo4j/neo4j.conf
#RUN echo 'dbms.connector.bolt.listen_address=:7687'             | tee -a /etc/neo4j/neo4j.conf
#RUN echo 'dbms.connector.https.enabled=true'                    | tee -a /etc/neo4j/neo4j.conf
#RUN echo 'dbms.connector.http.listen_address=:7474'             | tee -a /etc/neo4j/neo4j.conf



#RUN echo 'dbms.security.auth_enabled=false'                     | tee -a /etc/neo4j/neo4j.conf


#RUN rm /var/lib/neo4j/data/dbms/auth
#EXPOSE 7474
EXPOSE 5000
#EXPOSE 7687

#CMD ["usr/bin/./neo4j-admin","set-initial-password","pss1"]
#RUN rm -rf /var/lib/neo4j/data/dbms/auth
#RUN service neo4j restart
#RUN ["/usr/bin/cypher-shell -u neo4j -p neo4j && CALL dbms.changePassword('fandango');"]
#RUN service neo4j stop
#CMD service neo4j restart ; python /app/./init_service.py
CMD python3 /app/./init_service.py
