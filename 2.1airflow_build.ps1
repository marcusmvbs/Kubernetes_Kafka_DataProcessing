# $kafkaApp_imageName = "21121953/kafka-app"
$containerName      = "ubuntu_kind"

$cm_dag = "kubectl create configmap dag-script -n airflow --from-file=airflow/dags/helloworld_dag.py"
$cm_elt = "kubectl create configmap elt-script -n airflow --from-file=airflow/elt/elt_script.py"

$delete_worker     = "kubectl delete sts airflow-worker -n airflow"
$worker_recreation = "kubectl apply -f /airflow/worker-sts.yaml"
$worker_service    = "kubectl apply -f /airflow/service.yaml"
$apply_dag         = "kubectl exec -it airflow-worker-0 -n airflow -- python dags/helloworld_dag.py"

$Configmap_DAG   = "docker exec -it $containerName sh -c '$cm_dag'"
$Configmap_ELT   = "docker exec -it $containerName sh -c '$cm_elt'"
$Airflow_Delete  = "docker exec -it $containerName sh -c '$delete_worker'"
$Airflow_Create  = "docker exec -it $containerName sh -c '$worker_recreation'"
$Airflow_Service = "docker exec -it $containerName sh -c '$worker_service'"
$Dag_Creation    = "docker exec -it $containerName sh -c '$apply_dag'"

#1 kubectl create configmap dag-script -n airflow --from-file=airflow/dags/helloworld_dag.py
#2 kubectl create configmap elt-script -n airflow --from-file=airflow/elt/elt_script.py
## kubectl exec -it pod -n airflow -- airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin
## kubectl get sts airflow-worker -n airflow -o yaml
#3 kubectl delete sts airflow-worker -n airflow
#4 kubectl apply -f /airflow/worker-sts.yaml
#5 kubectl apply -f /airflow/service.yaml
#6 kubectl exec -it airflow-worker-0 -n airflow -- bash -c 'python dags/helloworld_dag.py'

## Implement worker-0 (cronjob) - Statefulset

Invoke-Expression -Command $Configmap_DAG
Start-Sleep -Seconds 2
Invoke-Expression -Command $Configmap_ELT
Start-Sleep -Seconds 2
Invoke-Expression -Command $Airflow_Delete
Start-Sleep -Seconds 2
Invoke-Expression -Command $Airflow_Create
Start-Sleep -Seconds 2
Invoke-Expression -Command $Airflow_Service
Start-Sleep -Seconds 40
Invoke-Expression -Command $Dag_Creation