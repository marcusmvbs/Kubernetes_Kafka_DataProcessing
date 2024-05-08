# cron &

# python /app/elt_script.py
kubectl get secret kafka-user-passwords --namespace kafka -o jsonpath='{.data.client-passwords}' | base64 -d | cut -d , -f 1 | sed 's/$/";/' > kafka/app/.creds.txt
cat kafka/app/.creds.txt >> kafka/client.properties # Current test

# Airflow Steps

# Create postgres database "airflow_DB" (for airflow metadata content)
# Initcontainer to start airflow, make sure db is running
# Environment sql connection with airflow_DB
# Command "airflow db init && airflow users create ..."

# pip install apache-airflow-providers-docker
# docker compose - extra_hosts: - "host.docker.internal:host-gateway"
