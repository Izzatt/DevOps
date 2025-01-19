pipeline {
    agent any
    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-hub') // Учётные данные Docker Hub из Jenkins Credentials
        DOCKER_IMAGE_BACKEND = 'izya69/backend:latest' // Имя образа для backend
        DOCKER_IMAGE_FRONTEND = 'izya69/frontend:latest' // Имя образа для frontend
        KUBECONFIG = credentials('kubeconfig-file') // Файл конфигурации Kubernetes
        PATH = "/usr/local/bin:$PATH"
        MONGO_URI = 'mongodb+srv://izzat:dbpa$$word1234@cluster0.cvhz3.mongodb.net/?retryWrites=true&w=majority' // Ваш URI для MongoDB Atlas
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
                    sh '/usr/local/bin/pytest tests/test_app.py'
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
        stage('Копирование файлов') {
            steps {
                script {
                    // Копирование файлов в рабочую директорию Jenkins
                    sh 'cp /home/izzat/devops/*.yaml .'
                }
            }
        }
        // 4. Деплой в Kubernetes
        stage('Деплой в Kubernetes') {
            steps {
                withEnv(["KUBECONFIG=${env.KUBECONFIG}"]) {
                    sh """
                    kubectl apply -f /home/izzat/devops/backend-deployment.yaml
                    kubectl apply -f /home/izzat/devops/frontend-deployment.yaml
                    kubectl apply -f /home/izzat/devops/backend-service.yaml
                    kubectl apply -f /home/izzat/devops/frontend-service.yaml
                    kubectl apply -f /home/izzat/devops/secrets.yaml
                    kubectl apply -f /home/izzat/devops/confmap.yaml
                    kubectl apply -f /home/izzat/devops/nsmonitoring.yaml
                    kubectl apply -f /home/izzat/devops/grafana-service.yaml
                    kubectl apply -f /home/izzat/devops/prometheus-confing.yaml
                    kubectl apply -f /home/izzat/devops/prometheus-service.yaml
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
