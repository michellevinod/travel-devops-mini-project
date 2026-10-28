
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t travel-booking:ci .'
            }
        }

        stage('API Tests') {
            steps {
                sh '''
                    docker run --rm \
                      --network host \
                      -v "$WORKSPACE:/app" \
                      -w /app \
                      python:3.11-slim \
                      sh -c "pip install -r requirements.txt pytest && APP_URL=http://host.docker.internal:5000 python -m pytest tests/test_api.py -v"
                '''
            }
        }

        stage('Selenium UI Tests') {
            steps {
                sh '''
                    docker run --rm \
                      --network host \
                      -v "$WORKSPACE:/app" \
                      -w /app \
                      python:3.11-slim \
                      sh -c "pip install -r requirements.txt pytest selenium && SELENIUM_URL=http://host.docker.internal:4444/wd/hub UI_APP_URL=http://host.docker.internal:5000 python -m pytest tests/test_ui.py -v"
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'All automated tests passed. Deployment stage reached.'
                sh 'docker compose up -d --build app prometheus grafana'
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Deployment stage was skipped.'
        }
    }
}
