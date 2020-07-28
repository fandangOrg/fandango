
<h2> KAFKA ELASTICSEARCH CONNECTOR </h2>

<h3> Introduction </h3>
<p> In this folder we provide a Kafka-ES connector written Python, in order to read messages from a Kafka Topic and then insert them in a ELASTICSEARCH index. <br>
This application will be run in a k8s Pod, thanks to the creation of a docker image that is pushed into the Docker Hub Project Repository. <br>
The variables needed by the application will be passed as Environmental variables in the pod initialization phase. </p>


<h3> Docker Image Build and Push Instructions </h3>

1) enter in folder with the Dockerfile <br>
<br>
2) Build docker image: <br>
   1 -  docker build -t fandangorg/fandango_kafka_elastic:X.X.X . <br>
   2 -  docker push fandangorg/fandango_kafka_elastic:X.X.X
   
   

<h3> Application variables configuration </h3>

In the folder /k8s there is a configuration file used to create and run the application pod. In this file it is possible to specify some input paramters to the app
(as ENV variables). <br>
In this sub-section all the possible configuration of the application will be described: <br>
KAFKA_HOST : hostname or IP of the Kafka Endpoint <br>
KAFKA_PORT : port where the Kafka Endpoint is listening for incoming requests <br>
KAFKA_TOPIC : Kafka topic to subscribe in <br>
KAFKA_CONSUMER_GROUP : name of the Consumer Group to join (new one or already existing) <br>
INPUT_JSON_ID_FIELD_PATH : path of subfields to retrieve the identifier (to use during the ES upsert) in the data schema. The subfields must be separated with a ; and WITHOUT ANY SPACE (e.g.: data;identifier) <br>
ES_HOST : hostname or IP of the Elasticsearch Endpoint <br>
ES_PORT : port where the Elasticsearch Endpoint is listening for incoming requests <br>
ES_INDEX_NAME : ES index to use <br>
ES_DOC_TYPE : type of the document <br>
LOG_TYPE : type of log to apply, values accepted: CONSOLE, FILES, BOTH or NONE <br>
CONSOLE_LOG_LEVEL : level of console log visualization, will be considered only if LOG_TYPE is set to CONSOLE or BOTH <br>
LOG_EXPIRATION_TIME : time in hours, if the folder log will not be modified for this time, it will be cleaned (check done only during the app starting phase)



<h3> K8s Pod Run </h3>

With the following line it is possible to create and run a deployment with one replica of the application: <br>
kubectl apply -f fandango-kafka-elastic-deployment.yaml



<h3> Reference links used to study/develop the solution </h3>

https://github.com/darenr/python-kafka-elasticsearch/blob/master/elasticsearch_consumer.py <br>
https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/ <br>
<br>
https://www.confluent.io/blog/the-simplest-useful-kafka-connect-data-pipeline-in-the-world-or-thereabouts-part-2/ <br>
<br>
https://sookocheff.com/post/kafka/kafka-in-a-nutshell/ <br>
https://towardsdatascience.com/kafka-python-explained-in-10-lines-of-code-800e3e07dad1 <br>
<br>
loggin library links: <br>
http://zetcode.com/python/logging/ <br>
https://docs.python.org/3/howto/logging.html <br>
https://docs.python.org/3/library/logging.handlers.html <br>
https://docs.python.org/3/library/logging.html <br>

