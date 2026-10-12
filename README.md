<p align="center">
  <img src="https://img.shields.io/badge/SmartSpamDetector-Email%20Spam%20Classification-red?style=for-the-badge" alt="SmartSpamDetector Logo" />
</p>

<h1 align="center">Smart Spam Detector</h1>

<p align="center">
  <strong>Production-grade spam email classification and MLOps pipeline with SHAP explainability, drift monitoring, and multi-interface access.</strong>
</p>

<p align="center">
  <a href="https://github.com/themanoj-025/Smart-Spam-Detector/actions"><img src="https://img.shields.io/github/actions/workflow/status/themanoj-025/Smart-Spam-Detector/ci.yml?style=flat-square&label=CI" alt="CI Status" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License MIT" /></a>
  <a href="https://github.com/themanoj-025/Smart-Spam-Detector/stargazers"><img src="https://img.shields.io/github/stars/themanoj-025/Smart-Spam-Detector?style=social" alt="GitHub Stars" /></a>
  <a href="https://github.com/themanoj-025/Smart-Spam-Detector/issues"><img src="https://img.shields.io/github/issues/themanoj-025/Smart-Spam-Detector?style=flat-square" alt="GitHub Issues" /></a>
  <a href="https://github.com/themanoj-025/Smart-Spam-Detector/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" alt="PRs Welcome" /></a>
</p>

---

## Overview

Smart Spam Detector provides a full-lifecycle machine learning system for detecting email spam and malicious text communications. It benchmarks six classifiers (Logistic Regression, Random Forest, XGBoost, SGDClassifier, LinearSVC, and a Stacking Ensemble), delivers SHAP feature attributions for every prediction, tracks data drift, and provides automated retraining workflows.

Users can interact with the system via a multi-page Streamlit portal, an automated CLI tool, or a production FastAPI service.

---

## Table of Contents

- [Key Features](#key-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Quick Start](#installation--quick-start)
- [REST API Reference](#rest-api-reference)
- [Configuration](#configuration)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)
- [Support](#support)

---

## Key Features

- **Six Benchmarked Classifiers**: Trains and compares Logistic Regression, Random Forest, XGBoost, SGD, SVC, and a Stacking Ensemble to maximize F1-score.
- **SHAP Token Attributions**: Computes per-word importance weights explaining which specific tokens triggered the spam classification.
- **Data & Concept Drift Monitoring**: Observes incoming inference payloads for statistical vocabulary drift to trigger scheduled retraining pipelines.
- **Batch Processing**: Ingests and scores raw text strings or entire mailbox `.mbox` archive files.
- **Triple Serving Modes**: Access through Streamlit web UI (`app.py`), terminal CLI (`classify.py`), or high-throughput REST API (`api.py`).

---

## Architecture

```text
               Incoming Email / Raw Text
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
       Streamlit App      CLI Tool    FastAPI Server
         (app.py)      (classify.py)     (api.py)
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
               Text Cleaning & TF-IDF
                           │
                           ▼
          Stacking Ensemble & ML Classifiers
      (Logistic Regression, XGBoost, Random Forest)
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
    Spam Probability Score      SHAP Feature Analysis
             │                           │
             └─────────────┬─────────────┘
                           │
                           ▼
            Evaluation & Drift Monitoring
```

---

## Project Structure

```text
Smart-Spam-Detector/
├── src/
│   ├── components/         # Ingestion, transformation, and model trainers
│   ├── pipeline/           # Training and batch prediction pipelines
│   ├── utils/              # Model evaluation metrics and logger utilities
│   └── config.py           # Core path and hyperparameter configurations
├── tests/                  # Pytest automated test suites
├── api.py                  # FastAPI REST API entry point
├── app.py                  # Streamlit web dashboard entry point
├── classify.py             # Single-command CLI classification utility
├── Dockerfile              # Multi-stage production container build
├── docker-compose.yml      # Local container orchestration
├── pyproject.toml          # Build backend and tool settings
├── requirements.txt        # Runtime dependencies
└── README.md               # Project documentation
```

---

## Prerequisites

- **Python**: `>= 3.10`
- **Memory**: Minimum 1 GB RAM

---

## Installation & Quick Start

### 1. Clone & Setup Environment

```bash
# Clone the repository
git clone https://github.com/themanoj-025/Smart-Spam-Detector.git
cd Smart-Spam-Detector

# Create virtual environment
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

### 2. Train Models

```bash
python -m src.pipeline.training_pipeline
```

### 3. Run Inference

**Run Streamlit Web Dashboard**:
```bash
streamlit run app.py
```
*Open http://localhost:8501 in your browser.*

**Run FastAPI Server**:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
*Open Swagger documentation at http://localhost:8000/docs.*

**Run CLI Classifier**:
```bash
python classify.py "Urgent: Your account security was compromised, click here to verify."
```

---

## REST API Reference

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check endpoint |
| `POST` | `/predict` | Classify single email text string |
| `POST` | `/predict/batch` | Classify list of email text strings |
| `GET` | `/metrics` | Retrieve model training benchmark metrics |

### Example Request (`POST /predict`)

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Congratulations! You have been selected for a cash prize. Claim now!"
  }'
```

---

## Configuration

| Environment Variable | Default | Purpose |
| :--- | :--- | :--- |
| `SPAM_API_KEY` | `""` | Optional API key token for REST API security |
| `MLFLOW_TRACKING_URI` | `sqlite:///mlflow.db` | MLflow experiment tracking backend URI |

---

## Testing

```bash
# Run pytest test suite
pytest tests/ -v

# Run with test coverage
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Roadmap

- [x] 6 ML baseline estimators and stacking ensemble
- [x] SHAP token attribution explainability
- [x] Multi-interface access (Streamlit, CLI, FastAPI)
- [x] Mailbox `.mbox` batch ingestion pipeline
- [ ] Direct IMAP / Gmail OAuth inbox monitoring integration <!-- TODO: Track via GitHub issue -->
- [ ] Active learning feedback loop from user misclassification reports <!-- TODO: Track via GitHub issue -->

---

## Contributing

Contributions are welcomed! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## Security

Please report vulnerabilities following the guidance in [SECURITY.md](SECURITY.md).

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Support

- 🐛 **Issue Tracker**: [GitHub Issues](https://github.com/themanoj-025/Smart-Spam-Detector/issues)
- 💡 **Discussions & Feedback**: [GitHub Pull Requests](https://github.com/themanoj-025/Smart-Spam-Detector/pulls)
