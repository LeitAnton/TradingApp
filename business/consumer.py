import logging
import os

from kafka import KafkaConsumer
from kafka.errors import KafkaConnectionError

from business.utils import update_currency_in_database


def constant_consumer():
    topic = 'topic_websocket_data'
    kafka_url = os.environ.get('KAFKA_URL')

    consumer = KafkaConsumer(
        bootstrap_servers=kafka_url,
    )
    consumer.subscribe([topic])

    try:
        while True:
            for message in consumer:
                update_currency_in_database(message.value)
    except KafkaConnectionError as error:
        logging.error(msg=f"Error connecting to Kafka: {error}")

    finally:
        consumer.close()
    constant_consumer()
