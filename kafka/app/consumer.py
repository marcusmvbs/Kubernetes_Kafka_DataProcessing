from confluent_kafka import Consumer, KafkaException
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

def read_password_from_file(sasl_password_path):
    with open(sasl_password_path, 'r') as file:
        password = file.read().strip()
        password = password[:-2]
    return password

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka configuration
topic = os.getenv('KAFKA_TOPIC')
bootstrap_servers = os.getenv('KAFKA_BROKERS')

sasl_password_path = "/tmp/.creds.txt"
sasl_plain_password = read_password_from_file(sasl_password_path)
security_protocol   = 'sasl_plaintext'
sasl_plain_username ='user1'
sasl_mechanism      = 'SCRAM-SHA-256'

config = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': security_protocol,
    'sasl.mechanism': sasl_mechanism,
    'sasl.username': sasl_plain_username,
    'sasl.password': sasl_plain_password,
    'group.id': 'my_consumer_group',  # Specify a consumer group ID
    'auto.offset.reset': 'earliest'   # Start reading from the beginning of the topic
}

def initialize_kafka_consumer():
    try:
        consumer = Consumer(config)
        consumer.subscribe([topic])
        return consumer
    except Exception as e:
        logger.error(f"Error initializing Kafka consumer: {e}")
        return None

def consume_messages(consumer):
    if consumer is None:
        logger.error("Kafka consumer is not initialized. Exiting.")
        return
    
    try:
        while True:
            msg = consumer.poll(1.0)  # Poll for new messages
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    # End of partition, the consumer has reached the end of the topic
                    logger.warning('%% %s [%d] reached end at offset %d\n' %
                                   (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                logger.info(f"Received message: {msg.value().decode('utf-8')}")
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user.")
    finally:
        consumer.close()

if __name__ == "__main__":
    consumer = initialize_kafka_consumer()
    if consumer:
        consume_messages(consumer)
    else:
        logger.error("Exiting due to failure to initialize Kafka consumer.")
