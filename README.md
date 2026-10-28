# Travel Booking DevOps Mini Project

## What it demonstrates
- Flask demo travel portal: login, trip search, booking and cancellation.
- Jenkins pipeline: build -> API tests -> Selenium UI tests -> deploy. A failed test makes the pipeline fail and prevents later deployment stages.
- Docker image and Compose runtime.
- Kubernetes Deployment with 2 replicas and liveness/readiness probes.
- Prometheus scrapes application metrics; Grafana provisions a dashboard.

## Quick start (Windows PowerShell)
Prerequisites: Docker Desktop running, Python 3.10+, Git. Docker Desktop must be configured for Linux containers. See https://docs.docker.com/desktop/setup/install/windows-install/

From this folder:
```powershell
docker compose up -d --build app prometheus grafana
```
Open:
- App: http://localhost:5000
- Prometheus: http://localhost:9090 (query `up` or `travel_http_requests_total`)
- Grafana: http://localhost:3000 (admin / admin123), Dashboards -> Travel Booking -> Travel Booking Reliability

For UI tests, start Selenium:
```powershell
docker compose up -d selenium
python -m pip install -r requirements.txt
$env:SELENIUM_URL="http://localhost:4444/wd/hub"
$env:UI_APP_URL="http://host.docker.internal:5000"
python -m pytest tests/test_ui.py -v
```
API tests:
```powershell
python -m pytest tests/test_api.py -v
```
Stop:
```powershell
docker compose down
```

## Jenkins setup
Install Jenkins on a machine/agent with Git, Python, Docker CLI, and Docker Compose plugin. Create a Pipeline job, choose Pipeline script from SCM, connect your GitHub repository, and set Script Path to `Jenkinsfile`. Ensure the Jenkins agent can execute `docker` commands and has Python installed. The Jenkinsfile uses Windows `bat` steps; for a Linux agent, replace `bat` with `sh` and commands with shell syntax. Install the Pipeline and Git plugins.

The tests execute before the deploy stage. To demonstrate the quality gate, temporarily change an expected assertion in `tests/test_api.py` to an incorrect expected value, commit/push, and rerun the build. The build should turn red and the deploy stage should be skipped. Restore the assertion afterwards.

If you changed `app.py`, rebuild the app container before retesting: `docker compose up -d --build app`.

## Kubernetes demo
Kubernetes is optional if Docker Desktop/Kubernetes is not already enabled; enabling it for the first time can take longer than the available time.
1. Docker Desktop -> Settings -> Kubernetes -> Enable Kubernetes, Apply and wait until ready.
2. Build image: `docker build -t travel-booking:latest .`
3. Deploy: `kubectl apply -f k8s/deployment.yml`
4. Check: `kubectl get deployments,pods,services`
5. Access: `kubectl port-forward service/travel-booking 5001:5000`, then http://localhost:5001
6. Scale: `kubectl scale deployment/travel-booking --replicas=3`
7. Clean up: `kubectl delete -f k8s/deployment.yml`

Note: Kubernetes manifest deploys the application. The included Prometheus/Grafana setup runs with Docker Compose to keep the local demo simple. For a full Kubernetes monitoring deployment, install the kube-prometheus-stack Helm chart and configure a scrape target for the app.

## Runtime problem demonstration
- Availability: stop the app container with `docker stop travel-app`. Prometheus should show the target as down after scrape timeout; restart using `docker start travel-app`.
- Response time: use the app repeatedly or add a temporary `time.sleep(2)` inside a route, make requests, and watch average response time in Grafana. Remove the sleep afterwards.
- Resource utilization: Docker Desktop -> Containers -> travel-app shows CPU and memory. For Kubernetes, run `kubectl top pods` if Metrics Server is available.

## Limitations
This is a teaching demo, not a production booking system: credentials and bookings are simulated, data is not persisted, and no payment or personal travel data is processed.
