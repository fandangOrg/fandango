#!/bin/bash
# Topic creation example script
KAFKA_PATH=/data/kafka/bin
KAFKA_ZOOKEEPER=fandangoedge01:2181
${KAFKA_PATH}/kafka-topics.sh --create --zookeeper ${KAFKA_ZOOKEEPER} --replication-factor 1 --partitions 1 --topic test
