# 🛡️ Smart Spam Detector

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
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square" alt="Python" /></a>
</p>

---

## 📋 Table of Contents

- [What it does](#what-it-does)
- [📸 Screenshots](#-screenshots)
- [✨ Features](#-features)
- [🚀 Quick start](#-quick-start)
- [📋 Environment variables](#-environment-variables)
- [🏗️ Architecture](#️-architecture)
- [📁 Project structure](#-project-structure)
- [📡 API endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📬 Support](#-support)
- [License](#license)

---

## What it does

Smart Spam Detector classifies emails as Spam or Ham using a production-grade MLOps pipeline: six models are trained, evaluated, and compared; SHAP provides per-prediction explainability; drift detection monitors model decay; and automated retraining fires when drift is detected. Users can explore results in a Streamlit dashboard, call the FastAPI REST API, or run the CLI.

## Screenshots

> To add screenshots: run `streamlit run app.py`, capture your screen, save images to `docs/assets/`, and reference them below.
>
> **Suggested screenshots:**
> - Streamlit dashboard classification view
> - SHAP explanation for a spam prediction
> - Batch classification results from .mbox file

---

## ✨ Features

| Feature | Description |
| --- | --- |
| 🖥️ **Interactive dashboard** | Streamlit UI with 3 pages (classification, SHAP, batch) |
| 🔍 **SHAP explainability** | Feature importance for every prediction |
| 📊 **Drift detection** | Monitor model performance degradation over time |
| 🔄 **Auto retraining** | Automated pipeline when drift is detected |
| 📦 **Batch processing** | Classify entire mailboxes from `.mbox` files |
| ⚡ **CLI interface** | Command-line classification with confidence scores |
| 🔌 **REST API** | FastAPI endpoints for programmatic access |
| 🔬 **6 ML models** | Logistic Regression, Random Forest, XGBoost, SGD, SVC, Stacking Ensemble |

## 🚀 Quick start

### Prerequisites

- Python 3.10 or newer
- A `.mbox` file for batch demos (or use the bundled sample)

### Install & run

```bash
# 1. Clone the repository
git clone https://github.com/themanoj-025/Smart-Spam-Detector.git
cd Smart-Spam-Detector

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env

# 5. Train the models
python -m src.pipeline.training_pipeline

# 6. Run the app
#    Streamlit dashboard
streamlit run app.py

#    API server
python api.py

#    CLI classification
python classify.py "Your email text here"
```

## 📋 Environment variables

| Variable | Description | Default | Required |
| --- | --- | --- | --- |
| `SPAM_API_KEY` | API key for authentication | — | No |
| `MLFLOW_TRACKING_URI` | MLflow tracking server | `sqlite:///mlflow.db` | No |

## 🏗️ Architecture

```text
Smart-Spam-Detector/
├── src/
│   ├── pipeline/             # Training and prediction pipelines
│   ├── components/           # Pipeline components
│   ├── utils/                # Logger, model comparison, reports
│   └── config.py             # Configuration
├── app.py                    # Streamlit dashboard
├── api.py                    # FastAPI server
├── classify.py               # CLI classifier
├── tests/                    # Test suite
├── data/                     # Dataset storage
├── experiments/              # MLflow tracking
├── docs/                     # Documentation
├── requirements.txt
└── Dockerfile
```

## 📁 Project structure

```
Smart-Spam-Detector/
├── src/
│   ├── pipeline/             # Training + prediction pipelines
│   ├── components/           # Pipeline components
│   ├── utils/                # Logger, model comparison, reports
│   └── config.py             # Configuration
├── app.py                    # Streamlit dashboard
├── api.py                    # FastAPI server
├── classify.py               # CLI classifier
├── tests/                    # Test suite
├── data/                     # Dataset storage
├── experiments/              # MLflow tracking
├── docs/                     # Documentation
├── requirements.txt
└── Dockerfile
```

## 📡 API endpoints

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/predict` | Classify a single email |
| `POST` | `/predict/batch` | Classify multiple emails |
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Model performance metrics |

### Example usage

```bash
# Classify a single email
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Congratulations! You won a free iPhone!"
  }'

# Batch classify
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      "Spam text",
      "Legitimate text"
    ]
  }'
```

## 🧪 Testing

```bash
# Run the full suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## 🗺️ Roadmap

> [!CAUTION] Checked items are built and verified. Unchecked items are tracked in the issue tracker.

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

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📬 Support

- 🐛 [Report a bug](https://github.com/themanoj-025/Smart-Spam-Detector/issues)
- 💡 [Request a feature](https://github.com/themanoj-025/Smart-Spam-Detector/issues)
- ⭐ [Star the repository](https://github.com/themanoj-025/Smart-Spam-Detector)

## License

MIT License — see [LICENSE](LICENSE).
