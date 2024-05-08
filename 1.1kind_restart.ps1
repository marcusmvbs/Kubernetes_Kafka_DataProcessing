# Common Variable
$containerName = "ubuntu_kind"

# Clean up variables
$KindDelCmd      = "docker exec -it $containerName sh -c 'kind delete cluster'"
$DockerStopCmd   = "docker stop $containerName"
$DockerRemoveCmd = "docker rm $containerName"

## RUN commands ##
# Clean up
Invoke-Expression -Command $KindDelCmd
Invoke-Expression -Command $DockerStopCmd
Invoke-Expression -Command $DockerRemoveCmd

## Rebuild ##
# Dot Sourcing - Execution continues in the file below
. .\1.0kind_build.ps1