<p align="center">
  <img src="https://img.shields.io/badge/SmartSpamDetector-Spam%20Detection-red?style=for-the-badge" alt="SmartSpamDetector Logo" />
</p>

<h1 align="center">🛡️ Smart Spam Detector</h1>

<p align="center">
  <strong>Production-Grade Spam Email Classification with MLOps Pipeline</strong>
</p>

<p align="center">
  <a href="https://github.com/themanoj-025/Smart-Spam-Detector/actions"><img src="https://img.shields.io/github/actions/workflow/status/themanoj-025/Smart-Spam-Detector/ci.yml?style=flat-square&label=CI" alt="CI Status" /></a>
  <a href="https://github.com/themanoj-025/Smart-Spam-Detector/blob/main/LICENSE"><img src="https://img.shields.io/github/license/themanoj-025/Smart-Spam-Detector?style=flat-square" alt="License" /></a>
  <a href="https://github.com/themanoj-025/Smart-Spam-Detector/stargazers"><img src="https://img.shields.io/github/stars/themanoj-025/Smart-Spam-Detector?style=social" alt="Stars" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square" alt="Python" /></a>
</p>

---

<p align="center">
  <strong>Stop spam before it reaches your inbox.</strong>
  <br />
  ML-powered classification with SHAP explainability, drift detection, and automated retraining.
</p>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📋 Environment Variables](#-environment-variables)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [📡 API Endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🙏 Acknowledgements](#-acknowledgements)

---

> 📸 **Screenshot placeholder:** Add a screenshot of the Streamlit dashboard's classification view.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **6 ML Models** | Logistic Regression, Random Forest, XGBoost, SGD, SVC, Stacking Ensemble |
| 🔍 **SHAP Explainability** | Feature importance for every prediction |
| 📊 **Drift Detection** | Monitor model performance degradation |
| 🔄 **Auto Retraining** | Automated pipeline when drift detected |
| 🖥️ **Interactive Dashboard** | Streamlit UI with 3 pages |
| 🔌 **REST API** | FastAPI endpoints for programmatic access |
| 📦 **Batch Processing** | Classify entire mailboxes from .mbox files |
| ⚡ **CLI Interface** | Command-line classification with confidence scores |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+

### Installation

```bash
# Clone the repository
git clone https://github.com/themanoj-025/Smart-Spam-Detector.git
cd Smart-Spam-Detector

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

### Train Models

```bash
python -m src.pipeline.training_pipeline
```

### Run the App

```bash
# Streamlit dashboard
streamlit run app.py

# API server
python api.py

# CLI classification
python classify.py "Your email text here"
```

---

## 📋 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SPAM_API_KEY` | API key for authentication | — | Optional |
| `MLFLOW_TRACKING_URI` | MLflow tracking server | `sqlite:///mlflow.db` | ❌ |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interface                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Streamlit   │  │   FastAPI    │  │     CLI      │          │
│  │  Dashboard   │  │   REST API   │  │  classify.py │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              ML Pipeline                                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │ Ingestion│ │Transform │ │ Training │ │Evaluation│    │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│  └───────────────────────┬──────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              6 ML Models                                  │   │
│  │  LR │ RF │ XGBoost │ SGD │ SVC │ Stacking                │   │
│  └───────────────────────┬──────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              MLflow Tracking                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Smart-Spam-Detector/
├── src/
│   ├── pipeline/          # Training and prediction pipelines
│   ├── components/        # Pipeline components
│   ├── utils/             # Logger, model comparison, reports
│   └── config.py          # Configuration
├── app.py                 # Streamlit dashboard
├── api.py                 # FastAPI server
├── classify.py            # CLI classifier
├── tests/                 # Test suite
├── data/                  # Dataset storage
├── experiments/           # MLflow tracking
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
└── Dockerfile             # Docker build
```

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/predict` | Classify a single email |
| `POST` | `/predict/batch` | Classify multiple emails |
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Model performance metrics |

### Example Usage

```bash
# Classify email
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Congratulations! You won a free iPhone!"}'

# Batch classify
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"emails": ["Spam text", "Legitimate text"]}'
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

---

## 🗺️ Roadmap

- [x] 6 ML models + stacking ensemble
- [x] SHAP explainability
- [x] Drift detection
- [x] Streamlit dashboard
- [x] FastAPI REST API
- [x] CLI interface
- [x] Batch processing
- [x] MLflow tracking
- [ ] Real-time email integration
- [ ] Slack/Teams notifications
- [ ] Multi-language support
- [ ] Active learning

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [scikit-learn](https://scikit-learn.org/) - ML framework
- [XGBoost](https://xgboost.readthedocs.io/) - Gradient boosting
- [SHAP](https://shap.readthedocs.io/) - Model explainability
- [Streamlit](https://streamlit.io/) - Dashboard framework
- [FastAPI](https://fastapi.tiangolo.com/) - REST API framework
- [MLflow](https://mlflow.org/) - Experiment tracking

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/themanoj-025">themanoj-025</a>
</p>

<p align="center">
  If you find this project useful, please give it a ⭐ star!
</p>
---

## ⭐ Star History

[![Last Commit](https://img.shields.io/github/last-commit/themanoj-025/Smart-Spam-Detector?style=flat-square)](https://github.com/themanoj-025/Smart-Spam-Detector)
[![Contributors](https://img.shields.io/github/contributors/themanoj-025/Smart-Spam-Detector?style=flat-square)](https://github.com/themanoj-025/Smart-Spam-Detector/graphs/contributors)

[![Star History Chart](https://api.star-history.com/svg?repos=themanoj-025/Smart-Spam-Detector&type=Date)](https://star-history.com/#Smart-Spam-Detector&Date)
