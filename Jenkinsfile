pipeline {
    agent any

    options {
        timestamps()
        skipDefaultCheckout(true)
    }

    environment {
        APP_IMAGE = 'travel-booking:ci'
        TEST_IMAGE = 'travel-booking-tests:ci'
        DEPLOY_CONTAINER = 'travel-booking-ci'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Build Application Image') {
            steps {
                sh 'docker build -t "$APP_IMAGE" .'
            }
        }

        stage('Build Test Image') {
            steps {
                // Copy source into the image so Docker Desktop does not need
                // to mount Jenkins' Linux-only workspace path from Windows.
                sh '''
                    docker build -t "$TEST_IMAGE" -f - . <<'DOCKERFILE'
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt pytest selenium requests
DOCKERFILE
                '''
            }
        }

        stage('API Tests') {
            steps {
                sh '''
                    docker run --rm \\
                      --add-host=host.docker.internal:host-gateway \\
                      -e APP_URL=http://host.docker.internal:5000 \\
                      "$TEST_IMAGE" \\
                      python -m pytest tests/test_api.py -v
                '''
            }
        }

        stage('Selenium UI Tests') {
            steps {
                sh '''
                    docker run --rm \\
                      --add-host=host.docker.internal:host-gateway \\
                      -e SELENIUM_URL=http://host.docker.internal:4444/wd/hub \\
                      -e UI_APP_URL=http://host.docker.internal:5000 \\
                      "$TEST_IMAGE" \\
                      python -m pytest tests/test_ui.py -v
                '''
            }
        }

        stage('Deploy Validated Application') {
            steps {
                // This stage cannot run unless both test stages succeed.
                sh '''
                    docker rm -f "$DEPLOY_CONTAINER" >/dev/null 2>&1 || true
                    docker run -d --name "$DEPLOY_CONTAINER" \\
                      -p 5002:5000 \\
                      "$APP_IMAGE"
                    sleep 5
                    docker run --rm \\
                      --add-host=host.docker.internal:host-gateway \\
                      "$TEST_IMAGE" \\
                      python -c 'import urllib.request; print(urllib.request.urlopen("http://host.docker.internal:5002/health", timeout=10).read().decode())'
                '''
                echo 'Validated application deployed on http://localhost:5002'
            }
        }
    }

    post {
        success {
            echo 'CI/CD succeeded: image built, API and Selenium tests passed, deployment health check passed.'
        }
        failure {
            echo 'Pipeline failed. Later stages, including deployment, were skipped after the failure.'
        }
        always {
            echo 'Pipeline execution finished.'
        }
    }
}
