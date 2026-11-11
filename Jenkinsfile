pipeline {
    agent any

    options {
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo 'Source code checked out from GitHub'
            }
        }

        stage('Prepare Environment') {
            steps {
                sh '''
                    cp /opt/two-tier-app/.env .env
                    chmod 600 .env
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                 sh 'docker compose -p two-tier-app build'
            }
        }

        stage('Deploy Application') {
            steps {
                sh 'docker compose -p two-tier-app up -d'
            }
        }

        stage('Verify Containers') {
            steps {
                sh 'docker compose -p two-tier-app ps'
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
