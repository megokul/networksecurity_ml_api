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

## 🗂️ Project Structure (Simplified)

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

MLflow secrets are handled via `.env`:

```env
MLFLOW_TRACKING_URI=...
MLFLOW_TRACKING_USERNAME=...
MLFLOW_TRACKING_PASSWORD=...
```

---

## 🔄 Pipeline Flow

```text
MongoDB → Ingestion → Validation → Transformation → Training → Evaluation → Push (S3)
```

Each stage saves a structured artifact and logs results:

* **Data Ingestion**: Pulls from MongoDB and stores raw/ingested data
* **Validation**: Performs schema check, null/duplicate checks, drift check
* **Transformation**: Preprocesses data using factories, splits into DVC-tracked sets
* **Model Trainer**: Runs Optuna HPO, trains multiple models, logs to MLflow
* **Model Evaluator**: Evaluates trained model on all splits
* **Model Pusher**: Saves final model locally + optionally uploads to S3

---

## 🌐 FastAPI Endpoints

* `/train`: Triggers full training pipeline (via Celery)
* `/predict`: Accepts CSV upload or manual entry, returns prediction

---

## 🧪 How to Run Locally

### 🔧 Install Requirements

```bash
pip install -r requirements.txt
```

### 📦 Run FastAPI App with Celery

```bash
docker-compose up --build
```

* FastAPI UI: [http://localhost:8000](http://localhost:8000)
* Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 🧠 Run Training Manually (Optional)

```bash
python main.py
```

---

## ☁️ AWS S3 Integration

* Final model and artifacts are pushed to:

  * `networksecurity-dev-artifacts/final_model/`
  * `networksecurity-dev-artifacts/artifacts/`

AWS credentials should be stored as GitHub Secrets or in `.env` (not committed).

---

## 📊 MLflow Tracking

* Experiment: `NetworkSecurityExperiment`
* Metrics: accuracy, f1, precision, recall
* Registry: `NetworkSecurityModel`

Run locally:

```bash
mlflow ui
```

Visit: [http://localhost:5000](http://localhost:5000)

---

## 🐳 Docker & DVC

* Full pipeline is Docker-compatible
* Data files tracked using `.dvc` and stored externally
* Use `dvc repro` to re-run pipelines if needed

---

## 🚀 Tech Stack

* **Backend**: FastAPI, Celery, Redis
* **ML Ops**: DVC, Optuna, MLflow
* **Cloud**: AWS S3, GitHub Actions (CI/CD-ready)
* **Data**: MongoDB, Pandas, NumPy
* **Models**: RandomForest, GradientBoosting (via Sklearn)
* **Pipeline**: Modular classes, dataclasses, factory pattern

---

## 👤 Author

**Gokul Krishna N V**
Machine Learning Engineer | UK 🇬🇧
[GitHub](https://github.com/megokul) • [LinkedIn](https://linkedin.com/in/nv-gokul-krishna)

---

## 📄 License

Licensed under **GPLv3**

---

## 🙌 Acknowledgements

* Dataset: Custom phishing dataset
* Project Structure inspired by industry-grade ML pipelines
