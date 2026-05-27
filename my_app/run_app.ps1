# Complete Automation Infrastructure Deployment Script (Kind + FastAPI + ArgoCD)
$ErrorActionPreference = "Stop"

Write-Host "=== 1. Restarting local Kubernetes cluster ===" -ForegroundColor Cyan
if (kind get clusters | Select-String -Pattern "kubeflow") {
    Write-Host "Found old cluster. Deleting..." -ForegroundColor Yellow
    kind delete cluster --name kubeflow
}
Write-Host "Creating new cluster 'kubeflow'..." -ForegroundColor Green
kind create cluster --name kubeflow --config kind-config.yaml

Write-Host "`n=== 2. Loading local Docker image into cluster ===" -ForegroundColor Cyan
Write-Host "Loading image my_app-web:latest..." -ForegroundColor Green
kind load docker-image my_app-web:latest --name kubeflow

Write-Host "`n=== 3. Deploying application (FastAPI + PostgreSQL) ===" -ForegroundColor Cyan
Write-Host "Creating namespace 'kubeflow'..." -ForegroundColor Green
kubectl create namespace kubeflow

Write-Host "Applying manifests from k8s directory..." -ForegroundColor Green
cd k8s
kubectl apply -f db.yaml
kubectl apply -f web.yaml
cd ..

Write-Host "`n=== 4. Deploying GitOps (ArgoCD) ===" -ForegroundColor Cyan
Write-Host "Creating namespace 'argocd'..." -ForegroundColor Green
kubectl create namespace argocd

Write-Host "Installing ArgoCD components..." -ForegroundColor Green
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

Write-Host "Waiting for ArgoCD deployments to be fully ready (dynamic wait)..." -ForegroundColor Yellow
# Розумне очікування: скрипт чекатиме, поки сервер ArgoCD реально не підніметься
kubectl wait --namespace argocd --for=condition=available deployment/argocd-server --timeout=300s

Write-Host "Applying ArgoCD Application manifest..." -ForegroundColor Green
kubectl apply -f k8s/argocd-app.yaml -n argocd

Write-Host "`n=== 5. Compiling ML Pipeline ===" -ForegroundColor Cyan
if (Test-Path "lr3/pipeline.py") {
    cd lr3
    Write-Host "Running pipeline compiler..." -ForegroundColor Green
    python pipeline.py
    cd ..
} else {
    Write-Host "pipeline.py not found, skipping compilation." -ForegroundColor Yellow
}

Write-Host "`n=== 6. Fetching access data ===" -ForegroundColor Cyan
Write-Host "Waiting 15 seconds for application pods stabilization..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "Checking pod status in kubeflow namespace:" -ForegroundColor Green
kubectl get pods -n kubeflow

# Даємо 5 секунд гарантії для генерації секрету після готовності деплойменту
Start-Sleep -Seconds 5
$RawBase64Password = kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}"
$ArgoPassword = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($RawBase64Password))

Write-Host "`n==========================================================" -ForegroundColor Magenta
Write-Host " INFRASTRUCTURE IS READY TO USE! " -ForegroundColor Magenta
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host "ArgoCD Login: admin" -ForegroundColor Green
Write-Host "ArgoCD Password: $ArgoPassword" -ForegroundColor Green
Write-Host "`nTo access services, run these commands in separate windows:" -ForegroundColor Yellow
Write-Host "API:  kubectl port-forward -n kubeflow svc/fastapi-svc 8000:8000" -ForegroundColor Gray
Write-Host "Argo: kubectl port-forward svc/argocd-server -n argocd 8080:443" -ForegroundColor Gray