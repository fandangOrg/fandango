from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime
import json


topic = "input_raw"


# producer = KafkaProducer(bootstrap_servers=['10.0.0.4:9092'],
#                          value_serializer=lambda x:
#                          json.dumps(x).encode('utf-8'))
#
# data = {'number': 5}
# producer.send(topic, value=data)


# start = datetime.now()
# for i in range(200):
#     if (datetime.now() - start).total_seconds() > 5:
#         break
#
# print "yeah"

consumer = KafkaConsumer(topic,
                         bootstrap_servers=['10.0.0.4:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id='certh_ner_group',
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

"analyzed_ner_topic"
counter = 0
for message in consumer:
    counter += 1
    print counter


