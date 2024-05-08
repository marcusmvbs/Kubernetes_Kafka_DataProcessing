from confluent_kafka import Consumer, KafkaException
import os
import sqlite3
from dotenv import load_dotenv
import logging
import json

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
security_protocol = 'sasl_plaintext'
sasl_plain_username='user1'
sasl_mechanism='SCRAM-SHA-256'

config = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': security_protocol,
    'sasl.mechanism': sasl_mechanism,
    'sasl.username': sasl_plain_username,
    'sasl.password': sasl_plain_password,
    'group.id': 'my_consumer_group',  # Specify a consumer group ID
    'auto.offset.reset': 'earliest'   # Start reading from the beginning of the topic
}

# SQLite database configuration
TEO_DIR = os.path.join(os.path.abspath('.'))
BASE_DIR = os.path.dirname(TEO_DIR)
DATA_DIR = os.path.join(BASE_DIR, 'data')
db_path = os.path.join(DATA_DIR, 'rivalry.db')

def initialize_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create a table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS matches
                    (team1 TEXT, odd1 REAL, team2 TEXT, odd2 REAL, month TEXT, date TEXT, hour TEXT)''')
    conn.commit()
    return conn

def save_to_database(conn, match_data):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO matches (team1, odd1, team2, odd2, month, date, hour)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (match_data['team1'], match_data['odd1'], match_data['team2'],
                    match_data['odd2'], match_data['month'], match_data['date'], match_data['hour']))
    conn.commit()

def initialize_kafka_consumer():
    try:
        consumer = Consumer(config)
        consumer.subscribe([topic])
        return consumer
    except Exception as e:
        logger.error(f"Error initializing Kafka consumer: {e}")
        return None

def consume_and_save_messages(consumer, conn):
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
                message_value = json.loads(msg.value().decode('utf-8'))
                save_to_database(conn, message_value)
                logger.info("Saved message to database: %s", message_value)
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user.")
    finally:
        consumer.close()

if __name__ == "__main__":
    conn = initialize_database()
    consumer = initialize_kafka_consumer()
    if consumer and conn:
        consume_and_save_messages(consumer, conn)
    else:
        logger.error("Exiting due to failure to initialize Kafka consumer or database connection.")
