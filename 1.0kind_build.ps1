$imageName     = "linux_k8s"
$containerName = "ubuntu_kind"
$network_type  = "--network=host"
$socket_volume = "/var/run/docker.sock:/var/run/docker.sock"
$playbook_exec = "ansible-playbook -i ansible/inventory.ini ansible/playbook.yaml"

# Docker Variables
$DockerBuildCmd  = "docker build -t $imageName ."
$DockerRunCmd    = "docker run -d $network_type -v $socket_volume --name $containerName $imageName"
$AnsiblePlaybook = "docker exec -it $containerName sh -c '$playbook_exec'"

## RUN commands ##
# Build Docker container
Invoke-Expression -Command $DockerBuildCmd
# Run Docker container
Invoke-Expression -Command $DockerRunCmd

# Execute Ansible tasks
Invoke-Expression -Command $AnsiblePlaybook

# Get pods
# $kubectl_pods = "kubectl get pods -A"
# $Get_Pods     = "docker exec -it $containerName sh -c '$kubectl_pods'"
# Invoke-Expression -Command $Get_Pods

Write-Output ""
Write-Output "Ubuntu-Kind ready!`n"



. .\2.1airflow_build.ps1
# . .\2.2kafka_build.ps1