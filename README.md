# Smart Spam Detector

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-blue)](https://scikit-learn.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36-red)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-grade spam email classifier with a complete MLOps pipeline, interactive Streamlit dashboard, FastAPI REST API, SHAP explainability, drift detection, and automated retraining.

---

## Overview

Smart Spam Detector is a machine learning system for classifying emails as spam or ham (legitimate). It provides:

- **Automated ML pipeline** — data ingestion, transformation, model training, evaluation, and registration
- **Multiple model comparison** — Logistic Regression, Random Forest, XGBoost, SGD, SVC, stacking ensemble with Optuna tuning
- **SHAP explainability** — Understand why each email was classified as spam/ham
- **Drift detection** — Monitor model performance drift and alert when retraining is needed
- **Interactive dashboard** — Streamlit UI for predictions, analysis, and monitoring
- **REST API** — FastAPI endpoints for programmatic classification
- **Batch processing** — Process entire mailboxes via CLI

---

## Features

| Feature | Description |
|---------|-------------|
| Pipeline Orchestration | End-to-end ML pipeline with data validation and logging |
| Model Training | 6 algorithms + stacking ensemble with Optuna hyperparameter tuning |
| Explainability | SHAP-based feature importance for individual predictions |
| Drift Detection | Monitor distribution drift and model performance degradation |
| Interactive Dashboard | Streamlit app with prediction, analysis, and monitoring pages |
| REST API | FastAPI server with API key authentication |
| Batch Processing | Classify entire mailboxes from .mbox files |
| CLI Interface | Command-line classification with confidence scores |

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| **Language** | Python 3.10+ |
| **ML** | scikit-learn, XGBoost |
| **Explainability** | SHAP |
| **Dashboard** | Streamlit |
| **API** | FastAPI, Pydantic |
| **Data Validation** | Great Expectations |
| **Experiment Tracking** | MLflow |
| **Testing** | pytest |
| **Linting** | Ruff, pre-commit |

---

## Installation

```bash
git clone https://github.com/themanoj-025/smart-spam-detector.git
cd smart-spam-detector
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and configure:

```env
SPAM_API_KEY=your-api-key  # Optional, enables API key auth
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
```

### Train Models

```bash
python -m src.pipeline.training_pipeline
```

### Run Dashboard

```bash
streamlit run app.py
```

### Run API Server

```bash
python api.py
```

### CLI Classification

```bash
python classify.py "Your email text here"
python classify.py --file email.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Classify a single email |
| POST | `/predict/batch` | Classify multiple emails |
| GET | `/health` | API health check |
| GET | `/metrics` | Model performance metrics |

---

## Project Structure

```
├── src/
│   ├── pipeline/          # Training and prediction pipelines
│   ├── components/        # Pipeline components (ingestion, training, etc.)
│   ├── utils/             # Logger, model comparison, report generator
│   └── config.py          # Configuration
├── app.py                 # Streamlit dashboard
├── api.py                 # FastAPI server
├── classify.py            # CLI classifier
├── tests/                 # Test suite
├── data/                  # Dataset storage
├── experiments/           # MLflow tracking
└── docs/                  # Documentation
```

---

## License

MIT
