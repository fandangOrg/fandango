
FROM python:3

WORKDIR /usr/src/app

ENV KAFKA_HOST=localhost \
    KAFKA_PORT=9092 \
    KAFKA_TOPIC=topic \
    KAFKA_CONSUMER_GROUP=elastic_group \
    INPUT_JSON_ID_FIELD_PATH=data;identifier \
    ES_HOST=localhost \
    ES_PORT=9220 \
    ES_INDEX_NAME=test-kafka-es \
    ES_DOC_TYPE=doc \
	LOG_TYPE=BOTH \
	CONSOLE_LOG_LEVEL=DEBUG \
	LOG_EXPIRATION_TIME=2

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "kafka_consumer_to_elasticsearch.py" ]
