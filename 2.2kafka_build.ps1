$docker_pswd           = "dckr_pat_NP2GI2K-hw7f70fKg5GufXyU9P8"
$docker_user           = "21121953"
$kafkaBroker_imageName = "21121953/kafka-broker"
$kafkaApp_imageName    = "21121953/kafka-app"
$containerName         = "ubuntu_kind"
$kafka_brokers         = "kubectl apply -f kafka/kafka.yaml"
$kafka_app             = "kubectl apply -f kafka/app/app.yaml"

# kubectl describe sts kafka-controller -n kafka
$kafka_client  = "kubectl run kafka-client --image=bitnami/kafka:3.7.0-debian-12-r2 -n kafka --command -- sleep infinity"
$client_config = "kubectl cp /kafka/client.properties kafka-client:/tmp/client.properties --namespace kafka"

$kafka_credentials = "./py_config/start.sh"

# Broker - from a broker client pod (SASL)
$create_topic_pod1 = "kubectl exec -it kafka-client -n kafka -- bash /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka-controller-0.kafka-controller-headless.kafka.svc.cluster.local:9092 --command-config /tmp/client.properties --create --topic rivalryodds --replication-factor 3 --partitions 3"
$create_topic_pod2 = "kubectl exec -it kafka-client -n kafka -- bash /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka-controller-0.kafka-controller-headless.kafka.svc.cluster.local:9092 --command-config /tmp/client.properties --create --topic hltvmatches --replication-factor 3 --partitions 3"

$list_topic1 = "kubectl exec -it kafka-client -n kafka -- bash /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka-controller-0.kafka-controller-headless.kafka.svc.cluster.local:9092 --command-config /tmp/client.properties --list"
$list_topic2 = "kubectl exec -it kafka-client -n kafka -- bash /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka-controller-1.kafka-controller-headless.kafka.svc.cluster.local:9092 --command-config /tmp/client.properties --list"
$list_topic3 = "kubectl exec -it kafka-client -n kafka -- bash /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka-controller-2.kafka-controller-headless.kafka.svc.cluster.local:9092 --command-config /tmp/client.properties --list"

# Kafka Client + Kafka Application
$exec_producer = "kubectl exec -it kafka-app -n kafka -- python tmp/producer.py"
$filteredtopic = "kubectl exec -it kafka-app -n kafka -- python tmp/filtered_topic.py"
$exec_consumer = "kubectl exec -it kafka-app -n kafka -- python tmp/consumer.py"

$Kafka_Creds = "docker exec -it $containerName sh -c '$kafka_credentials'"

$DindBroker_build = "docker build -t $kafkaApp_imageName ./kafka/app/"
$DindApp_build    = "docker build -t $kafkaBroker_imageName ./kafka/"
$Docker_Login     = "docker login -u $docker_user -p $docker_pswd"

$KafkaClient  = "docker exec -it $containerName sh -c '$kafka_client'"
$ClientConfig = "docker exec -it $containerName sh -c '$client_config'"

$KafkaApp_Build = "docker exec -it $containerName sh -c '$DindBroker_build'"
$DockerApp_Push = "docker push $kafkaApp_imageName"
$KafkaApp       = "docker exec -it $containerName sh -c '$kafka_app'"

# $KafkaBroker_Build = "docker exec -it $containerName sh -c '$DindApp_build'"
# $DockerBroker_Push = "docker push $kafkaBroker_imageName"
# $KafkaBroker_Apply = "docker exec -it $containerName sh -c '$kafka_brokers'"

$Create_Topic1 = "docker exec -it $containerName sh -c '$create_topic_pod1'"
$Create_Topic2 = "docker exec -it $containerName sh -c '$create_topic_pod2'"

$List_Topic1 = "docker exec -it $containerName sh -c '$list_topic1'"
$List_Topic2 = "docker exec -it $containerName sh -c '$list_topic2'"
$List_Topic3 = "docker exec -it $containerName sh -c '$list_topic3'"

$Producer       = "docker exec -it $containerName sh -c '$exec_producer'"
$Filtered_Topic = "docker exec -it $containerName sh -c '$filteredtopic'"
$Consumer       = "docker exec -it $containerName sh -c '$exec_consumer'"

# Invoke-Expression -Command $Docker_Login
Invoke-Expression -Command $Kafka_Creds
Start-Sleep -Seconds 2
Invoke-Expression -Command $KafkaApp_Build
Invoke-Expression -Command $DockerApp_Push

# Invoke-Expression -Command $KafkaBroker_Build
# Invoke-Expression -Command $DockerBroker_Push
# Invoke-Expression -Command $KafkaBroker_Apply

Invoke-Expression -Command $KafkaClient 
Invoke-Expression -Command $KafkaApp

Start-Sleep -Seconds 100
Invoke-Expression -Command $ClientConfig

Invoke-Expression -Command $Create_Topic1
Invoke-Expression -Command $Create_Topic2

Write-Output "Topic list on pod kafka-controller-0"
Invoke-Expression -Command $List_Topic1
Write-Output "Topic list on pod kafka-controller-1"
Invoke-Expression -Command $List_Topic2
Write-Output "Topic list on pod kafka-controller-2"
Invoke-Expression -Command $List_Topic3

Write-Output "Producer"
Invoke-Expression -Command $Producer 
Start-Sleep -Seconds 10

Write-Output "Filtered_Topic"
Invoke-Expression -Command $Filtered_Topic
Start-Sleep -Seconds 3

Write-Output "Consumer"
Invoke-Expression -Command $Consumer
# ---
# docker exec -it ubuntu_kind bash
# kubectl exec -it kafka-0 -n kafka -- bash

# kubectl get pods,svc,pvc,sts -n kafka-kraft
# kubectl scale statefulset kafka --replicas=3 --namespace=kafka-kraft
# kubectl run kafka-client --restart='Never' --image docker.io/apache/kafka:3.7.0 --port=9092 --namespace kafka --command -- sleep infinity
# kubectl cp --namespace kafka /kafka/client.properties kafka-client:/tmp/client.properties
# kubectl cp --namespace kafka /kafka/producer.py kafka-client:/tmp/producer.py

## Cluster ID ##
# kubectl exec -it kafka-client -n kafka -- bash /opt/bitnami/kafka/bin/kafka-cluster.sh cluster-id --bootstrap-server kafka-controller-0.kafka-controller-headless.kafka.svc.cluster.local:9092

## Logs Directory ##
# ./opt/kafka/bin/kafka-log-dirs.sh --describe --bootstrap-server localhost:9092
