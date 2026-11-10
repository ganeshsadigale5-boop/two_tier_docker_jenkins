
pipeline {
    agent any

    options {
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Source code checked out from GitHub'
                checkout scm
            }
        }

        stage('Build Docker Images') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Deploy Application') {
            steps {
                sh 'docker compose up -d'
            }
        }

        stage('Verify Containers') {
            steps {
                sh 'docker compose ps'
            }
        }

        stage('Application Health Check') {
            steps {
                sh '''
                    for i in $(seq 1 15); do
                        if curl -fsS http://localhost/ > /dev/null; then
                            echo "Frontend is responding successfully"
                            exit 0
                        fi
                        sleep 2
                    done

                    echo "Frontend health check failed"
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'Two-tier application deployed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the build logs.'
        }
    }
}

