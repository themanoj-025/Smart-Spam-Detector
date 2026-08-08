# Smart Spam Detector

> A production-grade spam email classifier with complete MLOps pipeline, interactive Streamlit dashboard, FastAPI REST API, SHAP explainability, drift detection, and automated retraining.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-blue.svg)](https://scikit-learn.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36-red.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Tech Stack & Core Technologies](#2-tech-stack--core-technologies)
- [3. High-Level Architecture](#3-high-level-architecture)
- [4. Complete Folder Structure Tree](#4-complete-folder-structure-tree)
- [5. Exhaustive File-by-File & Folder-by-Folder Breakdown](#5-exhaustive-file-by-file--folder-by-folder-breakdown)
- [6. Data Models & Schemas](#6-data-models--schemas)
- [7. API Surface](#7-api-surface)
- [8. Configuration & Environment Variables](#8-configuration--environment-variables)
- [9. Build, Run & Deployment Instructions](#9-build-run--deployment-instructions)
- [10. Data & Control Flow Walkthroughs](#10-data--control-flow-walkthroughs)
- [11. Dependency Graph Summary](#11-dependency-graph-summary)
- [12. Testing Strategy](#12-testing-strategy)
- [13. Known Issues, Technical Debt & Assumptions](#13-known-issues-technical-debt--assumptions)
- [14. Glossary](#14-glossary)
- [15. Appendix](#15-appendix)

---

## 1. Executive Summary

**Smart Spam Detector** is a production-grade machine learning system for classifying emails as spam or ham (legitimate). It provides an automated ML pipeline, multiple model comparison with Optuna tuning, SHAP explainability, drift detection, an interactive Streamlit dashboard, a FastAPI REST API, batch processing, and a CLI interface.

**Target users**: Email service providers, security teams, developers building email filtering, and data science learners.

**What problem it solves**: Spam email detection requires accurate, explainable, and maintainable ML systems. Smart Spam Detector provides a complete MLOps pipeline from data ingestion to production deployment with monitoring and retraining capabilities.

**Why it exists**: To demonstrate a production-ready ML system with all the components needed for real-world deployment: training, serving, explainability, monitoring, and drift detection.

*Note: The 6 algorithms + stacking ensemble with Optuna tuning and SHAP explainability are explicitly documented in the README and source code.*

---

## 2. Tech Stack & Core Technologies

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Language | Python | 3.10+ | Primary language |
| ML | scikit-learn | 1.7 | 6 algorithms + stacking ensemble |
| Gradient Boosting | XGBoost | — | High-performance model |
| Explainability | SHAP | 0.45+ | Per-word contribution analysis |
| Dashboard | Streamlit | 1.36+ | Interactive web UI (4 tabs) |
| API | FastAPI | 0.115+ | REST API with auth |
| Rate Limiting | SlowAPI | — | API rate limiting |
| Data Validation | Great Expectations | — | Pipeline data quality |
| Experiment Tracking | MLflow | — | Model versioning |
| HPO | Optuna | — | Hyperparameter optimization |
| Visualization | Plotly | 5.15+ | Interactive charts |
| Testing | pytest | — | Unit tests |
| Linting | Ruff | — | Code quality |

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Interfaces                                        │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Streamlit App   │  │  FastAPI Server  │  │  CLI Classifier  │  │
│  │  (app.py)        │  │  (api.py)        │  │  (classify.py)   │  │
│  │                  │  │                  │  │                  │  │
│  │  4 Tabs:         │  │  Endpoints:      │  │  Usage:          │  │
│  │  • Single Email  │  │  • /predict      │  │  python classify │  │
│  │  • Batch Process │  │  • /predict/batch│  │  "email text"    │  │
│  │  • Model Compare │  │  • /health       │  │                  │  │
│  │  • History       │  │  • /metrics      │  │                  │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                     │             │
│           └─────────────────────┼─────────────────────┘             │
│                                 │                                   │
│                                 ▼                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              Prediction Pipeline                              │   │
│  │  TF-IDF Vectorizer → Trained Model → Prediction + SHAP      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                 │                                   │
│                                 ▼                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              Training Pipeline                                │   │
│  │  Data Ingestion → Transformation → Training → Evaluation     │   │
│  │  6 Algorithms + Stacking Ensemble + Optuna HPO               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                 │                                   │
│                                 ▼                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              Monitoring Layer                                 │   │
│  │  Drift Detection + MLflow Tracking + Report Generation       │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Complete Folder Structure Tree

```
Smart-Spam-Detector/
├── .dockerignore
├── .editorconfig
├── .gitattributes
├── .github/
│   ├── CODEOWNERS
│   ├── copilot-instructions.md
│   ├── dependabot.yml
│   ├── ISSUE_TEMPLATE/
│   ├── labeler.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── ci.yml
│       ├── codeql.yml
│       ├── gitleaks.yml
│       ├── labeler.yml
│       ├── maintenance.yml
│       ├── stale.yml
│       └── welcome.yml
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── .streamlit/
│   └── config.toml
├── .vscode/
│   └── settings.json
├── AGENTS.md
├── AGENTS_FIX.md
├── api.py
├── app.py
├── classify.py
├── data/
│   └── dataset/
│       └── dataset.csv
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-compose.yml
├── Dockerfile
├── docs/
│   ├── community/
│   ├── design/
│   ├── product/
│   ├── project/
│   ├── reference/
│   └── technical/
├── LICENSE
├── Makefile
├── outputs/
│   └── 2026-06-01_18-54-30/
│       └── observations/
├── packages.txt
├── PROJECT_ANALYSIS.md
├── PROJECT_OVERVIEW.md
├── pyproject.toml
├── README.md
├── requirements-dev.txt
├── requirements.txt
├── runtime.txt
├── src/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── data_ingestion.py
│   │   ├── data_transformation.py
│   │   └── model_training.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── prediction_pipeline.py
│   │   └── training_pipeline.py
│   └── utils/
│       ├── __init__.py
│       ├── email_utils.py
│       ├── history_manager.py
│       ├── logger.py
│       ├── model_comparison.py
│       ├── report_generator.py
│       ├── state.py
│       ├── url_analyzer.py
│       └── utils.py
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_config.py
    ├── test_email_utils.py
    ├── test_history_manager.py
    ├── test_prediction_pipeline.py
    ├── test_report_generator.py
    ├── test_url_analyzer.py
    └── test_utils.py
```

---

## 5. Exhaustive File-by-File & Folder-by-Folder Breakdown

### Root Entry Points

#### `Smart-Spam-Detector/app.py`
- **Purpose**: Streamlit dashboard (1000+ lines). Features dark/light theme, animated SVG confidence gauge, real-time typing analysis, SHAP word-level explanations, batch MBOX/CSV/Excel processing, model comparison dashboard, and classification history.

#### `Smart-Spam-Detector/api.py`
- **Purpose**: FastAPI REST API with API key authentication, rate limiting, and endpoints for single/batch classification.

#### `Smart-Spam-Detector/classify.py`
- **Purpose**: CLI classifier for command-line email classification with confidence scores.

### `Smart-Spam-Detector/src/` — Core ML Package

#### `src/pipeline/training_pipeline.py`
- **Purpose**: End-to-end training pipeline — data ingestion, transformation, 6-model comparison + stacking ensemble with Optuna HPO, MLflow tracking.

#### `src/pipeline/prediction_pipeline.py`
- **Purpose**: Prediction pipeline — TF-IDF vectorization, model prediction, SHAP explanation generation.

#### `src/components/data_ingestion.py`
- **Purpose**: Data loading and validation (Great Expectations).

#### `src/components/data_transformation.py`
- **Purpose**: Text preprocessing, TF-IDF feature extraction.

#### `src/components/model_training.py`
- **Purpose**: Model training with 6 algorithms: Logistic Regression, Random Forest, XGBoost, SGD, SVC, Stacking Ensemble.

### `Smart-Spam-Detector/src/utils/` — Utilities

| Module | Purpose |
|--------|---------|
| `email_utils.py` | Email text cleaning and preprocessing |
| `url_analyzer.py` | URL risk analysis and suspicious link detection |
| `history_manager.py` | Persistent classification history (JSON) |
| `model_comparison.py` | Model performance comparison with radar charts |
| `report_generator.py` | HTML report generation |
| `logger.py` | Structured logging setup |
| `state.py` | Application state management |

---

## 6. Data Models & Schemas

### Classification Result

```json
{
  "prediction": "Spam | Ham",
  "confidence": "float — 0-100%",
  "explanation": {
    "top_spam_words": [{"word": "str", "contribution": "float"}],
    "top_ham_words": [{"word": "str", "contribution": "float"}],
    "highlighted_html": "str — word-colored HTML"
  },
  "url_analysis": {
    "total_urls": "int",
    "suspicious_count": "int",
    "risk_level": "low | medium | high"
  }
}
```

---

## 7. API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predict` | Classify single email |
| `POST` | `/predict/batch` | Classify multiple emails |
| `GET` | `/health` | API health check |
| `GET` | `/metrics` | Model performance metrics |

---

## 8. Configuration & Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `SPAM_API_KEY` | API key authentication | No (optional) |
| `MLFLOW_TRACKING_URI` | MLflow tracking URI | No |

---

## 9. Build, Run & Deployment Instructions

```bash
# Install
pip install -r requirements.txt

# Train models
python -m src.pipeline.training_pipeline

# Run dashboard
streamlit run app.py

# Run API
python api.py

# CLI classification
python classify.py "Your email text"
```

### Docker

```bash
docker compose up -d
```

---

## 10. Data & Control Flow Walkthroughs

### Flow 1: Single Email Classification

1. User pastes email text in Streamlit
2. Real-time gauge updates (lightweight prediction)
3. User clicks "Classify Email"
4. Full pipeline: clean → vectorize → predict → SHAP
5. Results displayed with animated gauge, word contributions, URL analysis

---

## 11. Dependency Graph Summary

```
app.py → src/pipeline/prediction_pipeline.py → src/components/*
api.py → src/pipeline/prediction_pipeline.py
classify.py → src/pipeline/prediction_pipeline.py
src/pipeline/training_pipeline.py → src/components/*
src/utils/* → src/config/config.py
```

---

## 12. Testing Strategy

- **Framework**: pytest
- **Tests**: 8 test files covering API, config, email utils, history, pipeline, reports, URL analyzer, utils
- **CI**: GitHub Actions with lint, test, security scans

---

## 13. Known Issues, Technical Debt & Assumptions

### Known Issues

1. **English only**: Models trained on English email text.
2. **No real-time retraining**: Drift detection alerts but doesn't auto-retrain.

### Assumptions

1. **Dataset available**: Requires `data/dataset/dataset.csv`.
2. **Models pre-trained**: App expects trained models in `outputs/`.

---

## 14. Glossary

| Term | Definition |
|------|-----------|
| **TF-IDF** | Term Frequency-Inverse Document Frequency |
| **SHAP** | SHapley Additive exPlanations |
| **Optuna** | Hyperparameter optimization framework |
| **Stacking Ensemble** | Combining multiple models via meta-learner |
| **Drift Detection** | Monitoring model performance degradation |

---

## 15. Appendix

### Supported File Formats

- **MBOX**: Email archive format (Gmail, Thunderbird export)
- **CSV**: Spreadsheet with email text column
- **Excel (.xlsx)**: Spreadsheet with email text column

---

*This document was generated as part of a comprehensive project documentation effort. Last updated: August 8, 2026.*
