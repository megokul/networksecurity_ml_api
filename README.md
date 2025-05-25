# 🛡️ NetworkSecurity: Phishing Detection ML Pipeline

> 🚀 A modular, production-grade ML pipeline for phishing detection — powered by FastAPI, DVC, Optuna, MLflow, Celery, and Docker. Designed with cloud-native architecture, YAML-based configuration, and reusable components.

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

* ✅ End-to-end ML pipeline: Ingestion ➜ Validation ➜ Transformation ➜ Training ➜ Evaluation ➜ Deployment
* ✅ YAML-driven configuration system
* ✅ Optuna hyperparameter tuning with MLflow tracking
* ✅ Real-time FastAPI inference + Celery async training
* ✅ AWS S3 model upload + GitHub Actions CI/CD
* ✅ DVC for dataset versioning

---

## 📂 Project Structure

```text
networksecurity/
├── app.py                   # FastAPI application
├── main.py                  # Manual training pipeline trigger
├── Dockerfile               # Container build instructions
├── docker-compose.yaml      # Multi-container stack (FastAPI, Redis, Celery)
├── config/                  # YAML configs: schema, params, etc.
├── data/                    # DVC-tracked dataset (raw, transformed, validated)
├── artifacts/               # Timestamped artifacts per pipeline run
├── final_model/             # Final production model
├── logs/                    # Pipeline run logs
├── templates/               # Jinja2 templates for UI
├── requirements.txt         # Python dependencies
└── src/networksecurity/     # Source package
    ├── components/          # Core pipeline stages
    ├── config/              # Config manager
    ├── constants/           # Path constants
    ├── data_processors/     # Encoders, scalers, imputers
    ├── dbhandler/           # MongoDB + S3 interfaces
    ├── entity/              # Dataclass definitions
    ├── exception/           # Custom error handling
    ├── inference/           # Prediction logic
    ├── logging/             # Centralized logger
    ├── pipeline/            # Pipeline orchestration modules
    ├── utils/               # Helpers (save/load/transform)
    └── worker/              # Celery worker entrypoint
```

---

## 🔁 Pipeline Flow

```text
MongoDB → Data Ingestion → Validation → Transformation → Training → Evaluation → Push to S3
```

Each stage outputs artifacts, logs, and metrics using a standardized structure.

---


## ⚙️ Configuration

Project is fully parameterized via YAML configs and `.env` secrets.

**YAML Configs:**

* `config.yaml`: Paths, filenames, artifact roots
* `params.yaml`: Tuning ranges, preprocessing methods
* `schema.yaml`: Column dtypes and target
* `templates.yaml`: Templates for YAML-based reports

**Environment Variables (.env):**

```dotenv
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

# AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_ECR_LOGIN_URI=
ECR_REPOSITORY_NAME=

```

---

## 🧪 How to Run

### ⚙️ Local (No Docker)

```bash
uvicorn app:app --reload
```

### 🐳 Local (With Docker Compose)

```bash
docker compose up --build
```

### ☁️ On EC2 (with Nginx + GitHub Runner)

1. Create `.env` and push to instance
2. Add this user data script when launching EC2:

```bash
#!/bin/bash

set -e
export DEBIAN_FRONTEND=noninteractive

# === 1. Update system and install base packages ===
apt-get update -y && apt-get upgrade -y
apt-get install -y git curl nginx openssl ufw

# === 1.1 Install Docker ===
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

# === 4. Configure Nginx ===
cat <<EOF > /etc/nginx/sites-available/fastapi
server {
    listen 443 ssl;
    server_name _;

    ssl_certificate /etc/ssl/self-signed/self.crt;
    ssl_certificate_key /etc/ssl/self-signed/self.key;

    location / {
        proxy_pass http://localhost:8000;
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
sudo -u ubuntu ./config.sh --url <your_repo_here> \
                           --token <your_token_here> \
                           --unattended \
                           --name self-hosted \
                           --labels self-hosted,linux,x64 \
                           --work _work

# Register runner as service
sudo ./svc.sh install
sudo ./svc.sh start
```

Then access the app at: `https://<your-ec2-ip>`

---

## 📈 MLflow Tracking

* Experiment: `NetworkSecurityExperiment`
* Registry: `NetworkSecurityModel`
* Metrics: accuracy, f1, precision, recall

```bash
mlflow ui
```

Access: [http://localhost:5000](http://localhost:5000)

---

## 🧪 FastAPI Endpoints

* `POST /train` → triggers training via Celery
* `POST /predict` → accepts CSV or input JSON

---

## 🔐 Licensing

This project is licensed under **GPLv3**.

---

## 👨‍💻 Author

**Gokul Krishna N V**
Machine Learning Engineer — UK 🇬🇧
[GitHub](https://github.com/megokul) • [LinkedIn](https://www.linkedin.com/in/nv-gokul-krishna)

---

## 🙌 Acknowledgements

* Project structure: Inspired by industry ML standards
* Based on data hosted by [Krishnaik06’s GitHub](https://github.com/krishnaik06/datasets)
