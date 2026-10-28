
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Application Image') {
            steps {
                echo 'Building Travel Booking Docker image'
                sh 'docker version'
                sh 'docker build -t travel-booking:latest .'
            }
        }

        stage('API Tests') {
            steps {
                echo 'Running API tests against the running application'
                sh '''
                    python3 -m pip install -r requirements.txt pytest
                    APP_URL=http://host.docker.internal:5000 python3 -m pytest tests/test_api.py -v
                '''
            }
        }

        stage('Selenium UI Tests') {
            steps {
                echo 'Running Selenium browser tests'
                sh '''
                    python3 -m pip install -r requirements.txt pytest selenium
                    SELENIUM_URL=http://host.docker.internal:4444/wd/hub \
                    UI_APP_URL=http://host.docker.internal:5000 \
                    python3 -m pytest tests/test_ui.py -v
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deployment stage reached only if all tests pass'
            }
        }
    }

    post {
        success {
            echo 'CI pipeline passed.'
        }
        failure {
            echo 'Pipeline failed. Deployment stage was skipped.'
        }
        always {
            echo 'Pipeline execution finished.'
        }
    }
}
