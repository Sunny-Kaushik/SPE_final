# ML-Driven Doctor Recommendation System

## Project Overview

This project implements an intelligent doctor recommendation system that identifies the medical specialty for a given set of symptoms and recommends doctors based on the predicted specialty. It uses two key services:

1. **Specialty Predictor Service**: A Flask-based REST API that takes symptoms as input and predicts the relevant medical specialty.
2. **Doctor Recommendation Service**: A FastAPI-based service that provides doctor recommendations for a given specialty.

The system is containerized using Docker, ensuring portability and seamless deployment. It also supports running on Minikube for orchestration in a Kubernetes environment.

## Features

- Predict medical specialty based on user symptoms.
- Recommend doctors for the identified specialty.
- RESTful APIs for seamless integration.
- Dockerized services for easy deployment.
- Kubernetes-ready with Minikube support.
- Secure sensitive data management using Ansible Vault.

---

## Installation and Setup

### Prerequisites
- **Python 3.7 or higher**
- **Docker**
- **Minikube** (for Kubernetes deployment)
- **VS Code** (recommended for development)

### Python Environment Setup

To install Python libraries in VS Code, use the following command:
```bash
python3 -m pip install [library name] --break-system-packages
```
For example:
```bash
python3 -m pip install joblib --break-system-packages
```

To export all installed libraries and their versions:
```bash
python3 -m pip freeze > temp.txt
```

### Checking REST API Functionality
Use the following `curl` command to test the Doctor Recommendation API:
```bash
curl -X POST "http://localhost:8000/recommend/" \
-H "Content-Type: application/json" \
-d '{"specialists": ["Dermatology"]}'
```

---

## Running the Application

### Step 1: Start Backend Servers
1. **Specialty Predictor**
   ```bash
   docker pull sunnykaushik007/flask-specialty-predictor
   docker run --name speciality-predictor -p 8080:5000 sunnykaushik007/flask-specialty-predictor
   ```
   Access it at: [http://127.0.0.1:8080](http://127.0.0.1:8080)

2. **Doctor Recommendation Service**
   ```bash
   docker pull sunnykaushik007/bandit:latest
   docker run --name bandit_v1 -p 8000:8000 sunnykaushik007/bandit:latest
   ```
   Access it at: [http://localhost:8000/frontend](http://localhost:8000/frontend)

### Step 2: Run the Main Application
The `app.py` file connects the backend services and serves the main application. Run it using:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 5001
```
Access the page at: [http://localhost:5001/](http://localhost:5001/)

### Optional: Run on Minikube
To deploy the services on Minikube:
```bash
minikube start
kubectl apply -f main1/ml-service.yaml
kubectl apply -f main2/ml-service2.yaml
kubectl get pods -o wide
```

---

## Docker Commands

### Build and Run Containers
1. Build and run the Doctor Recommendation container:
   ```bash
   docker build -t bandit .
   docker run --name bandit_v1 -p 8000:8000 bandit
   ```

2. Build and Run the Specialty Predictor container:
   ```bash
   docker build -t speaciality_predictor .
   docker run --name second_v1 -p 8080:5000 sunnykaushik007/flask-specialty-predictor
   ```

### Inspect Docker Images
Inspect image metadata:
```bash
docker image inspect <image-name>
```

### Push to Docker Hub
1. Tag the image:
   ```bash
   docker tag bandits:latest sunnykaushik007/bandits:latest
   ```
2. Push to Docker Hub:
   ```bash
   docker push sunnykaushik007/bandits:latest
   ```

### Remove Unused Containers and Images
- Remove all stopped containers:
  ```bash
  docker container prune
  ```
- Remove unused images:
  ```bash
  docker image prune
  ```

---

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---

