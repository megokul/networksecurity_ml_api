# 🛡️ NetworkSecurity: Phishing Detection ML Pipeline

> A god-tier, production-grade ML pipeline for phishing URL detection — powered by FastAPI, DVC, Optuna, MLflow, Celery, and Docker. Built with modular components, cloud integration, and scalable architecture.

---

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-blue?logo=mlflow)
![DVC](https://img.shields.io/badge/DVC-Data_Versioning-purple?logo=dvc)
![Optuna](https://img.shields.io/badge/Optuna-HPO-orange?logo=optuna)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?logo=mongodb)
![AWS](https://img.shields.io/badge/AWS-S3-yellow?logo=amazonaws)
![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?logo=docker)
![Celery](https://img.shields.io/badge/Celery-Async-37814A?logo=celery)
![Redis](https://img.shields.io/badge/Redis-Broker-D82C20?logo=redis)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Modeling-F7931E?logo=scikit-learn)
![Pandas](https://img.shields.io/badge/Pandas-Dataframe-150458?logo=pandas)
![NumPy](https://img.shields.io/badge/NumPy-Array-013243?logo=numpy)

---

## ✅ Features

* ✅ Modular ML pipeline with reusable components
* ✅ MongoDB ingestion and schema-driven validation
* ✅ Preprocessing via custom `data_processors`
* ✅ Optuna-based hyperparameter optimization
* ✅ MLflow tracking and model registry
* ✅ Full FastAPI backend with `/train` and `/predict`
* ✅ Celery + Redis async task queue
* ✅ DVC integration for data versioning
* ✅ Auto-push models to AWS S3

---

## 📂 Project Structure (Simplified)

```text
networksecurity/
├── app.py                   # FastAPI app
├── main.py                  # Full training pipeline entrypoint
├── Dockerfile               # Container build file
├── docker-compose.yaml      # FastAPI + Redis + Celery setup
├── config/                  # YAML configs (params, schema, etc.)
├── data/                    # DVC-tracked data (raw, validated, transformed)
├── artifacts/               # Timestamped debug artifacts from runs
├── final_model/             # Final pushed model
├── logs/                    # Timestamped logs per pipeline run
├── prediction_output/       # Output of /predict endpoint
├── templates/               # HTML templates for FastAPI rendering
├── requirements.txt         # Python dependencies
├── setup.py                 # Package metadata
└── src/networksecurity/     # All core logic
    ├── components/          # Data ingestion, validation, training, etc.
    ├── config/              # Configuration manager
    ├── constants/           # Path constants
    ├── data_processors/     # Encoders, scalers, imputers
    ├── dbhandler/           # MongoDB + S3 interfaces
    ├── entity/              # Artifact/config dataclasses
    ├── exception/           # Custom exception handling
    ├── inference/           # `NetworkModel` class for prediction
    ├── logging/             # Centralized logger
    ├── pipeline/            # Orchestration logic for each pipeline stage
    ├── utils/               # Common helpers
    └── worker/              # Celery worker entrypoint
```

---

## ⚙️ Configuration System

All configs are YAML-driven and parsed via `ConfigBox` for dot-access.

* `config.yaml`: All file paths, directory names, and model filenames
* `params.yaml`: All tunable parameters (Optuna, preprocessing, validation)
* `schema.yaml`: Feature column types and target label mapping
* `templates.yaml`: Predefined templates for reports (validation, training)

### 📁 Required `.env` variables

Ensure the following are set in your `.env` file:

```env
# MongoDB
MONGODB_URI_BASE=
MONGODB_USERNAME=
MONGODB_PASSWORD=

# MLflow/DagsHub
MLFLOW_TRACKING_URI=
MLFLOW_TRACKING_USERNAME=
MLFLOW_TRACKING_PASSWORD=
DAGSHUB_REPO_NAME=
DAGSHUB_REPO_OWNER=

# AWS Credentials
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_ECR_LOGIN_URI=
ECR_REPOSITORY_NAME=

```

These values are accessed securely and not hardcoded in source code.

---

## 🚀 How to Run Locally

### ▶️ Run FastAPI app locally without Docker

```bash
uvicorn app:app --reload
```

### 🐳 Run locally using Docker Compose

```bash
docker compose up --build -d
```

### ☁️ Host on AWS EC2

1. Launch an EC2 instance (Ubuntu 22.04)
2. Add your `.env` file manually or via SCP
3. Paste the following **User Data** script under Advanced → User Data during EC2 launch:

```bash
#!/bin/bash

set -e
export DEBIAN_FRONTEND=noninteractive

# === 1. Update system and install base packages ===
apt-get update -y && apt-get upgrade -y
apt-get install -y git curl nginx openssl ufw

# === 1.1 Install Docker (official script from get.docker.com) ===
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# === 1.2 Add ubuntu user to docker group ===
usermod -aG docker ubuntu
newgrp docker

# === 2. Enable UFW and open required ports ===
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw --force enable

# === 3. Generate self-signed SSL cert for Nginx ===
mkdir -p /etc/ssl/self-signed
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" \
  --silent)
CN=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/public-ipv4 \
  --silent)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/self-signed/self.key \
  -out /etc/ssl/self-signed/self.crt \
  -subj "/C=UK/ST=Scotland/L=Glasgow/O=Self/OU=Dev/CN=$CN"

# === 4. Configure Nginx for HTTPS reverse proxy ===
cat <<EOF > /etc/nginx/sites-available/fastapi
server {
    listen 443 ssl;
    server_name _;

    ssl_certificate /etc/ssl/self-signed/self.crt;
    ssl_certificate_key /etc/ssl/self-signed/self.key;

    location / {
        proxy_pass http://localhost:8000;  # App will be deployed later by CI/CD
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}

server {
    listen 80;
    return 301 https://\$host\$request_uri;
}
EOF

ln -sf /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
systemctl enable nginx

# === 5. GitHub Actions runner ===
mkdir -p /home/ubuntu/actions-runner
cd /home/ubuntu/actions-runner

curl -o actions-runner-linux-x64-2.324.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.324.0/actions-runner-linux-x64-2.324.0.tar.gz
echo "e8e24a3477da17040b4d6fa6d34c6ecb9a2879e800aa532518ec21e49e21d7b4  actions-runner-linux-x64-2.324.0.tar.gz" | shasum -a 256 -c
tar xzf ./actions-runner-linux-x64-2.324.0.tar.gz
chown -R ubuntu:ubuntu /home/ubuntu/actions-runner

# Configure runner
sudo -u ubuntu ./config.sh --url <YOUR_REPO> \
                           --token <YOUR_REGISTRATION_TOKEN> \
                           --unattended \
                           --name self-hosted \
                           --labels self-hosted,linux,x64 \
                           --work _work

# Register runner as a persistent service
sudo ./svc.sh install
sudo ./svc.sh start
```

✅ That’s it! FastAPI will be served at `https://<your-ec2-public-ip>` with HTTPS and CI/CD ready.

---
