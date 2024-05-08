FROM python:3.8-slim
# FROM docker.io/bitnami/kafka:3.7.0-debian-12-r2

RUN apt-get update && apt-get install -y python3-pip \
    vim postgresql-client sqlite3 cron && \
    apt-get clean

COPY . /tmp/

RUN pip3 install --upgrade pip && \
    pip3 install -r /tmp/requirements.txt

# RUN echo "0 3 * * * python /tmp/filtered_topic.py" | crontab -

CMD ["tail", "-f", "/dev/null"]