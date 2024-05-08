from confluent_kafka import Consumer, Producer, KafkaError
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
bootstrap_servers = os.getenv('KAFKA_BROKERS')

sasl_password_path = "/tmp/.creds.txt"
sasl_plain_password = read_password_from_file(sasl_password_path)
security_protocol = 'sasl_plaintext'
sasl_plain_username = 'user1'
sasl_mechanism = 'SCRAM-SHA-256'

consumer_config = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': security_protocol,
    'sasl.mechanism': sasl_mechanism,
    'sasl.username': sasl_plain_username,
    'sasl.password': sasl_plain_password,
    'group.id': 'rivalryodds_consumer_group',  # Specify a consumer group ID
    'auto.offset.reset': 'earliest'   # Start reading from the beginning of the topic
}

producer_config = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': security_protocol,
    'sasl.mechanism': sasl_mechanism,
    'sasl.username': sasl_plain_username,
    'sasl.password': sasl_plain_password,
}

def initialize_kafka_consumer():
    try:
        consumer = Consumer(consumer_config)
        return consumer
    except Exception as e:
        logger.error(f"Error initializing Kafka consumer: {e}")
        return None

def process_message_content(message_content):
    # Implement your logic to process the message content and filter information here
    # For example, split the message and filter out specific information
    parts = message_content.split(',')
    team1_info = f"Team1: {parts[0]}, Odd1: {parts[1]}"
    team2_info = f"Team2: {parts[2]}, Odd2: {parts[3]}"
    filtered_content = f"{team1_info}, {team2_info}"
    return filtered_content

def consume_messages_and_produce_filtered_topic(consumer):
    if consumer is None:
        logger.error("Kafka consumer is not initialized. Exiting.")
        return
    
    producer = Producer(producer_config)
    filtered_topic = "filteredrivalryodds"

    try:
        consumer.subscribe(["rivalryodds"])
        while True:
            msg = consumer.poll(1.0)  # Poll for new messages
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition, the consumer has reached the end of the topic
                    logger.warning('%% %s [%d] reached end at offset %d\n' %
                                   (msg.topic(), msg.partition(), msg.offset()))
                else:
                    raise KafkaError(msg.error())
            else:
                # Process message content and filter information
                message_content = msg.value().decode('utf-8')
                filtered_content = process_message_content(message_content)
                
                # Produce filtered message to another topic
                producer.produce(filtered_topic, value=filtered_content.encode('utf-8'))
                logger.info(f"Produced filtered message to topic {filtered_topic}")
                
                # Flush producer to ensure messages are delivered
                producer.flush()
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user.")
    finally:
        consumer.close()

if __name__ == "__main__":
    consumer = initialize_kafka_consumer()
    if consumer:
        consume_messages_and_produce_filtered_topic(consumer)
    else:
        logger.error("Exiting due to failure to initialize Kafka consumer.")
