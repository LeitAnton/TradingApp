import json
import os

from kafka import KafkaProducer
from kafka.errors import KafkaConnectionError


def send_message_to_kafka(topic, message):
    kafka_url = os.environ.get('KAFKA_URL')

    producer = KafkaProducer(
        bootstrap_servers=kafka_url,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    try:
        producer.send(topic, message)
    except KafkaConnectionError as e:
        print(f'Kafka Connection Error: {e}')
    finally:
        producer.close()
