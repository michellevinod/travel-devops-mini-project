pipeline {
  agent any
  options { timestamps() }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Build application image') {
      steps { bat 'docker build -t travel-booking:%BUILD_NUMBER% .' }
    }
    stage('Start test environment') {
      steps { bat 'docker compose up -d app selenium' }
    }
    stage('API automated tests') {
      steps { bat 'python -m pip install -r requirements.txt' ; bat 'python -m pytest tests/test_api.py -v' }
    }
    stage('Selenium UI tests') {
      steps {
        bat 'python -m pytest tests/test_ui.py -v'
      }
    }
    stage('Deploy with Docker Compose') {
      steps { bat 'docker compose up -d --build app prometheus grafana' }
    }
  }
  post {
    always { bat 'docker compose ps' }
    failure { echo 'Tests/build failed. Pipeline stops before the deploy stage.' }
  }
}
