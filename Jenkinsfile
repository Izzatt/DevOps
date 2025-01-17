pipeline {
    agent any
    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-hub') // Учётные данные Docker Hub из Jenkins Credentials
        DOCKER_IMAGE_BACKEND = 'izya69/backend:latest' // Имя образа для backend
        DOCKER_IMAGE_FRONTEND = 'izya69/frontend:latest' // Имя образа для frontend
        KUBECONFIG = credentials('kubeconfig-file') // Файл конфигурации Kubernetes
        PATH = "/home/izzat/.local/lib/python3.10/site-packages/pytest:$PATH"
    }
    stages {
        // 1. Линтинг
        stage('Линтинг кода') {
            parallel {
                stage('Линтинг backend') {
                    steps {
                        dir('backend') {
                            sh 'flake8 app.py'
                        }
                    }
                }
                stage('Линтинг frontend') {
                    steps {
                        dir('frontend') {
                            sh 'npm install'
                            sh 'npm run lint'
                        }
                    }
                }
            }
        }
        // 2. Юнит-тесты
        stage('Запуск юнит-тестов') {
            steps {
                dir('backend') {
                    sh '/home/izzat/.local/lib/python3.10/site-packages/pytest tests'
                }
            }
        }

        // 3. Сборка и публикация Docker-образов
        stage('Сборка и публикация Docker-образов') {
            parallel {
                stage('Сборка и публикация backend') {
                    steps {
                        dir('backend') {
                            sh """
                            docker build -t $DOCKER_IMAGE_BACKEND .
                            docker login -u $DOCKERHUB_CREDENTIALS_USR -p $DOCKERHUB_CREDENTIALS_PSW
                            docker push $DOCKER_IMAGE_BACKEND
                            """
                        }
                    }
                }
                stage('Сборка и публикация frontend') {
                    steps {
                        dir('frontend') {
                            sh """
                            docker build -t $DOCKER_IMAGE_FRONTEND .
                            docker login -u $DOCKERHUB_CREDENTIALS_USR -p $DOCKERHUB_CREDENTIALS_PSW
                            docker push $DOCKER_IMAGE_FRONTEND
                            """
                        }
                    }
                }
            }
        }

        // 4. Деплой в Kubernetes
        stage('Деплой в Kubernetes') {
            steps {
                withEnv(["KUBECONFIG=${env.KUBECONFIG}"]) {
                    sh """
                    kubectl apply -f backend-deployment.yaml
                    kubectl apply -f frontend-deployment.yaml
                    kubectl apply -f backend-service.yaml
                    kubectl apply -f frontend-service.yaml
                    kubectl apply -f secrets.yaml
                    kubectl apply -f confmap.yaml
                    kubectl apply -f nsmonitoring.yaml
                    kubectl apply -f grafana-service.yaml
                    kubectl apply -f prometheus-confing.yaml
                    kubectl apply -f prometheus-service.yaml
                    kubectl rollout status deployment/backend-deployment --timeout=60s
                    kubectl rollout status deployment/frontend-deployment --timeout=60s
                    """
                }
            }
        }

        // 5. Тестирование API
        stage('Тестирование API') {
            steps {
                sh """
                curl -f http://192.168.49.2:30001/health || exit 1
                curl -f http://192.168.49.2:30002 || exit 1
                """
            }
        }
    }

    post {
        success {
            echo 'Пайплайн успешно завершён!'
        }
        failure {
            echo 'Пайплайн завершился с ошибкой. Проверьте логи.'
        }
    }
}
