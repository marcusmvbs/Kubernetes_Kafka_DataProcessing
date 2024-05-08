import requests
from bs4 import BeautifulSoup
from confluent_kafka import Producer
import json
import os
import subprocess
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

security_protocol = 'sasl_plaintext'
sasl_plain_username='user1'
sasl_mechanism='SCRAM-SHA-256'

config = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': security_protocol,
    'sasl.mechanism': sasl_mechanism,
    'sasl.username': sasl_plain_username,
    'sasl.password': sasl_plain_password
}

def initialize_kafka_producer():
    try:
        producer = Producer(config)
        return producer
    except Exception as e:
        logger.error(f"Error initializing Kafka producer: {e}")
        return None

def delivery_report(err, msg):
    """ Delivery report callback """
    if err is not None:
        logger.error('Message delivery failed: %s', err)
    else:
        logger.info('Message delivered to %s [%d]', msg.topic(), msg.partition())

def scrape_match_details():
    url = 'https://www.rivalry.com/on/esports/csgo-betting'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    match_elements = soup.find_all('div', class_='betline m-auto betline-wide mb-0')

    matches_data = []

    for match in match_elements:
        team1_element = match.find('div', class_='outcome-name')
        odd1_element = match.find('div', class_='outcome-odds')
        hour_element = match.find('div', class_='text-navy dark:text-[#CFCFD1] leading-3 text-[11px]').text.strip()
        day = hour_element.split()
        month = f"{day[0]}"
        date = f"{day[1][:-4]}"
        hour = f"{day[1][-4:]} {day[2]}"

        if team1_element and odd1_element:
            team1 = team1_element.text.strip()
            odd1 = odd1_element.text.strip()

            team2_element = team1_element.find_next('div', class_='outcome-name')
            odd2_element = odd1_element.find_next('div', class_='outcome-odds')

            if team2_element and odd2_element:
                team2 = team2_element.text.strip()
                odd2 = odd2_element.text.strip() 

                matches_data.append({'team1': team1, 'odd1': odd1, 'team2': team2, 'odd2': odd2, 'month': month, 'date': date, 'hour': hour})
    return matches_data

def send_to_kafka(metrics_data, producer):
    if producer is None:
        logger.error("Kafka producer is not initialized. Exiting.")
        return
    
    for match_data in metrics_data:
        try:
            message_value = json.dumps(match_data)
            producer.produce(topic, value=message_value.encode('utf-8'), callback=delivery_report)
            logger.info(f"Sent message: {message_value}") 
        except Exception as e:
            logger.error(f"Error occurred while sending message to Kafka: {e}")

    producer.flush()
    producer.poll(1)

if __name__ == "__main__":
    producer = initialize_kafka_producer()
    if producer:
        metrics_data = scrape_match_details()
        send_to_kafka(metrics_data, producer)
    else:
        logger.error("Exiting due to failure to initialize Kafka producer.")
