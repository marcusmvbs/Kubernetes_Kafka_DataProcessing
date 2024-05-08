### Kubernetes Dashboard NodePort Service ###
$containerName  = "ubuntu_kind"
$kubectl_secret = "kubectl apply -f /kind/dashboard/sa-secret.yaml"
$create_sa      = "kubectl apply -f /kind/dashboard/serviceaccount.yaml"
$nodeport_svc   = "kubectl apply -f /kind/dashboard/nodeport-svc.yaml"
$kubectl_svc    = "kubectl get svc -n kubernetes-dashboard"
$sa_token       = "kubectl create token dashboard-sa -n kubernetes-dashboard"

$Secret_Token  = "docker exec -it $containerName sh -c '$kubectl_secret'"
$Create_SvcAcc = "docker exec -it $containerName sh -c '$create_sa'"
$Apply_Svc     = "docker exec -it $containerName sh -c '$nodeport_svc'"
$Get_Svc       = "docker exec -it $containerName sh -c '$kubectl_svc'"
$Create_Token  = "docker exec -it $containerName sh -c '$sa_token'"

Invoke-Expression -Command $Secret_Token
Start-Sleep -Seconds 2
Invoke-Expression -Command $Create_SvcAcc
Start-Sleep -Seconds 2
Invoke-Expression -Command $Apply_Svc
Start-Sleep -Seconds 2
Invoke-Expression -Command $Get_Svc
Start-Sleep -Seconds 2
Write-Output "`nDashboard Bearer Token (dashboard-sa):`n"
Invoke-Expression -Command $Create_Token

Write-Output "`nDashboard Nodeport service enabled: https://localhost:30500`n"
Write-Output "Copy bearer token to access kubernetes dashboard on browser."