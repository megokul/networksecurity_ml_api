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

## 📊 ML Pipeline Flowchart

![ML Pipeline Flowchart](assets/network_pipeline_flowchart.png)

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
2. Use EC2 launch script (see below)
3. Access app at `https://<your-ec2-ip>`

---

## 🛠️ EC2 User Data Script

Add this during launch:

```bash
#!/bin/bash
# (full script omitted for brevity — see repo)
```

Full script installs Docker, Nginx, SSL, and GitHub runner.

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

* Dataset: Custom phishing dataset
* Project structure: Inspired by industry ML standards
