# Real-Time Chat App

## 📄 Project Overview
The **Real-Time Chat App** is a secure communication platform that enables users to send and receive messages in real-time. Built with a **Flask WebSocket backend**, the app supports an optional **React** interface and is designed with modern DevOps principles, including **Kubernetes deployment**, **CI/CD pipelines**, and **performance monitoring**.

---

## 🚀 Features

### Core Features
- **Real-Time Messaging**: Secure, low-latency communication powered by WebSockets.
- **User Management**:
  - Register new users.
  - User authentication with session tokens.
  - Admin access to manage all users.
- **Chat Management**:
  - Start new chats and send messages.
  - Fetch chat lists and message histories.

### DevOps Features
- **Kubernetes Deployment**:
  - Ingress configuration for WebSocket communication.
  - Secrets management for sensitive data.
- **CI/CD Pipeline**:
  - Lint Flask and React code.
  - Run backend unit tests.
  - Build and push Docker images to Docker Hub.
  - Automate deployment to Minikube or EKS.
- **Monitoring**:
  - **Prometheus** for tracking API response times and container performance.
  - **Grafana** dashboards for system insights.

---

## 🔗 Endpoints

### User Management
- **POST** `/api/users/register`: Register a new user (username, password, etc.).
- **POST** `/api/users/login`: Authenticate a user and return a session token.
- **GET** `/api/users`: Fetch all users (admin-only).

### Messaging
- **GET** `/api/chats`: Retrieve all chats for the current user.
- **POST** `/api/chats`: Start a new chat (requires `recipient_id`).
- **POST** `/api/chats/<chat_id>/message`: Send a message in a specific chat.
- **GET** `/api/chats/<chat_id>`: Fetch messages in a specific chat.

### WebSockets
- **/ws/chat/<chat_id>**: WebSocket endpoint for real-time messaging in a specific chat.

---

## 🛠️ Tech Stack

### Backend
- Flask with WebSocket support.
- MongoDB for data storage.

### Frontend (Optional)
- React.js for an interactive user interface.

### DevOps
- Docker and Docker Compose.
- Kubernetes (Minikube/EKS).
- CI/CD with Jenkins.
- Monitoring with Prometheus and Grafana.

---

## 📦 Repository Structure

### App Repository
Contains the application source code:


---

## ⚙️ CI/CD Pipeline

1. **Code Linting**:
   - Lint Flask and React code.
2. **Unit Testing**:
   - Run tests for backend logic.
3. **Docker Build**:
   - Build and push Docker images to Docker Hub.
4. **Kubernetes Deployment**:
   - Deploy application to Minikube or EKS using manifests.
5. **Monitoring Setup**:
   - Deploy Prometheus and Grafana for monitoring.
6. **API Testing**:
   - Validate API functionality in the live environment.

---

## 📈 Monitoring Setup
- **Prometheus**: Monitors API response times and resource usage.
- **Grafana**: Visualizes data via dashboards.
  - Dashboard examples:
    - WebSocket performance metrics.
    - API latency trends.

---

## 📖 How to Use

1. **Clone Repository**:
   - App repo: `git clone https://github.com/Izzatt/DevOps.git`

2. **Run Locally**:
   - Backend:
     ```bash
     cd backend
     docker build -t chat-backend .
     docker run -p 5000:5000 chat-backend
     ```
   - Frontend (optional):
     ```bash
     cd frontend
     docker build -t chat-frontend .
     docker run -p 80:80 chat-frontend
     ```

3. **Deploy with Kubernetes**:
   - Apply manifests:
     ```bash
     kubectl apply -f backend-deployment.yaml
    kubectl apply -f frontend-deployment.yaml
    kubectl apply -f backend-service.yaml
    kubectl apply -f frontend-service.yaml
    kubectl apply -f secrets.yaml
    kubectl apply -f confmap.yaml
    kubectl apply -f nsmonitoring.yaml
    kubectl apply -f grafana-service.yaml
    kubectl apply -f prometheus-config.yaml
    kubectl apply -f prometheus-service.yaml
     ```

4. **Access Monitoring**:
   - Prometheus: `http://<MinikubeIP>:30090
   - Grafana: `http://<MinikubeIP>:30003

---

## 🔒 Security
- **Secrets**: Use Kubernetes secrets to store sensitive keys and tokens.
- **Authentication**: Session-based authentication for all endpoints.

---

## 🛡️ License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
