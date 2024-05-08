FROM ubuntu:22.04

LABEL maintainer="Marcus Vinicius Barros da Silva <marcus.mvbs@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    --no-install-recommends gnupg curl wget ca-certificates \
    apt-utils apt-transport-https dos2unix net-tools jq \
    python3 python3-pip python3-apt ansible \
    vim postgresql-client sqlite3 cron \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /py_config /ansible /kind /charts
COPY requirements.txt /py_config/

RUN pip3 install --upgrade pip && \
    pip3 install -r /py_config/requirements.txt && \
    ansible-galaxy collection install community.general community.kubernetes

RUN curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh

COPY airflow/ /airflow/
COPY ansible/ /ansible/
COPY charts/ /charts/
COPY kafka/ /kafka/
COPY kind/ /kind/
COPY start.sh /py_config/

# minutes / hour(AM/PM) / day / month / week day
# RUN echo "0 * * * * sh ./start.sh" | crontab -

CMD ["tail", "-f", "/dev/null"]
# CMD ["sh", "-c", "python /airflow/elt/elt_script.py && tail -f /dev/null"]