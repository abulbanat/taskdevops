# MyApp DevOps Assignment

## Submission Artifacts
- GitHub Repo Link: `https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>`
- Docker Hub Image Link: `https://hub.docker.com/r/<DOCKERHUB_USERNAME>/myapp`
- Kubernetes YAML Files:
  - `k8s/deployment.yaml`
  - `k8s/service.yaml`
- CI Workflow File:
  - `.github/workflows/docker-build-push.yml`

## Project Structure
```text
.
├─ app/
│  ├─ main.py
│  └─ requirements.txt
├─ Dockerfile
├─ k8s/
│  ├─ deployment.yaml
│  └─ service.yaml
├─ logging/
└─ .github/
   └─ workflows/
      └─ docker-build-push.yml
```

## Application Details
- The app runs on port `8080`.
- It prints a heartbeat log to stdout every 5 seconds.
- It also exposes a basic `/` endpoint for quick verification.

## GitHub Actions: Docker Build and Push
Workflow file: `.github/workflows/docker-build-push.yml`

### Trigger
- Runs on every push to `main`.

### Required GitHub Secrets
Set these in GitHub: `Settings -> Secrets and variables -> Actions -> New repository secret`

- `DOCKERHUB_USERNAME`: your Docker Hub username
- `DOCKERHUB_TOKEN`: a Docker Hub access token (recommended) or password

### Docker image tags pushed
- `DOCKERHUB_USERNAME/myapp:latest`
- `DOCKERHUB_USERNAME/myapp:${GITHUB_SHA}`

## Build and Run Locally (Optional)
```bash
docker build -t myapp:local .
docker run --rm -p 8080:8080 myapp:local
```

## Deploy to Minikube
Before applying manifests, replace `DOCKERHUB_USERNAME` in `k8s/deployment.yaml` with your real Docker Hub username.

```bash
minikube start
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get pods
minikube service myapp-svc --url
```

Useful checks:
```bash
kubectl get deploy myapp
kubectl get svc myapp-svc
kubectl logs -l app=myapp --tail=50
```

## Install Logging Stack (Loki + Promtail + Grafana)
These commands use Helm flags only (no custom values files required).

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

kubectl create namespace logging

helm upgrade --install loki grafana/loki \
  --namespace logging

helm upgrade --install promtail grafana/promtail \
  --namespace logging \
  --set "config.clients[0].url=http://loki-gateway.logging.svc.cluster.local/loki/api/v1/push"

helm upgrade --install grafana grafana/grafana \
  --namespace logging \
  --set service.type=NodePort \
  --set adminPassword='admin123!'
```

### Change Grafana admin password later
```bash
helm upgrade --install grafana grafana/grafana \
  --namespace logging \
  --set service.type=NodePort \
  --set adminPassword='<NEW_PASSWORD>'
```

## Verify Logs in Grafana
1. Get Grafana URL:
```bash
minikube service grafana -n logging --url
```
2. Open Grafana in browser and log in (`admin` / password from Helm value).
3. Add Loki data source:
   - URL: `http://loki.logging.svc.cluster.local:3100`
4. Go to **Explore** and run query:
   - `{app="myapp"}`

If no logs appear immediately, wait ~30-60 seconds and retry.

## Screenshot Commands and What to Capture

### 1) GitHub Actions success screenshot
Command:
```bash
git push origin main
```
Capture:
- In GitHub web UI, open **Actions** tab.
- Screenshot the latest workflow run showing green/success for Docker build & push.

### 2) Kubernetes pods screenshot (all namespaces)
Command:
```bash
kubectl get pods -A
```
Capture:
- Terminal screenshot showing:
  - `myapp` pods in `default`
  - `loki`, `promtail`, and `grafana` pods in `logging`

### 3) Grafana Explore logs screenshot
Commands:
```bash
minikube service grafana -n logging --url
kubectl logs -l app=myapp --tail=20
```
Capture:
- Grafana **Explore** page with query `{app="myapp"}` and visible log lines.

## Short Explanation
This project automates container delivery by building and pushing a Docker image to Docker Hub on every push to the `main` branch. The workflow publishes two tags so you always have a stable `latest` image and an immutable commit-specific image tied to `GITHUB_SHA`. The Kubernetes Deployment runs two replicas of the app and includes CPU/memory requests and limits to demonstrate basic resource governance. A NodePort Service exposes the app so it can be reached easily in Minikube. For observability, Loki stores logs, Promtail collects Kubernetes pod logs, and Grafana provides a UI to query them. The app emits periodic stdout logs, which makes end-to-end log ingestion easy to validate quickly. The README includes copy-paste commands and screenshot steps so the assignment can be submitted consistently.
