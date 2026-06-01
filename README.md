<div align="center">

# 📧 Spam Email Classifier

**A production-grade machine learning system for classifying emails as Spam or Ham (legitimate).**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange?logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 🌟 Overview

This project implements a complete machine learning pipeline for **spam email detection** with both an interactive web UI and a production-grade REST API.

### What's Included

- **🧠 6 ML Models**: Logistic Regression, Decision Tree, SVM, KNN, Random Forest, and Stacking ensemble
- **🔧 Modular Pipeline**: Clean separation of data ingestion, transformation, training, and prediction
- **🎨 Streamlit Dashboard**: Interactive UI with real-time analysis, dark mode, and model comparison
- **📡 FastAPI Server**: REST API with API key auth, rate limiting, and documentation
- **📊 Model Comparison**: Radar charts, confusion matrices, and ranking tables
- **📂 Batch Processing**: Process single emails, CSV/Excel uploads, or bulk API requests
- **🔍 URL Analysis**: Automatic detection and risk scoring of URLs in emails
- **📜 History Tracking**: SQLite-backed classification history with search and export
- **📄 Report Generation**: Downloadable HTML reports with charts and metrics
- **💻 CLI Tool**: Classify emails directly from the command line

---

## 🚀 Key Results

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|:--------:|:---------:|:------:|:--------:|
| **Stacking Classifier** | **98.7%** | **98.6%** | **99.9%** | **99.2%** |
| Random Forest | 98.1% | 97.9% | 100% | 98.9% |
| Decision Tree | 96.6% | 97.3% | 98.8% | 98.0% |
| Logistic Regression | 96.2% | 95.9% | 99.9% | 97.9% |
| KNN | 90.6% | 90.1% | 100% | 94.8% |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.10+** | Core programming language |
| **scikit-learn** | ML models, preprocessing, GridSearchCV, evaluation |
| **pandas / numpy** | Data manipulation and analysis |
| **Streamlit** | Interactive web application |
| **FastAPI + uvicorn** | REST API server |
| **slowapi** | API rate limiting middleware |
| **SHAP** | Model explanation (word-level contributions) |
| **BeautifulSoup4** | HTML email content parsing |
| **matplotlib / Plotly** | Performance visualization and radar charts |
| **SQLite3** | Classification history storage |
| **openpyxl / xlsxwriter** | CSV/Excel upload and report export |

---

## 📂 Project Structure

```
spam-email-classifier/
├── app.py                          # Streamlit web application
├── api.py                          # FastAPI REST API server
├── classify.py                     # CLI classification tool
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project metadata & config
├── .python-version                 # Python version pinning
├── start.bat                       # One-click Windows launcher
├── LICENSE                         # MIT License
├── README.md                       # This file
│
├── src/
│   ├── config/
│   │   └── config.py              # Configuration, hyperparameters, auto-discovery
│   ├── components/
│   │   ├── data_ingestion.py      # Dataset loading & validation
│   │   ├── data_transformation.py # Label encoding, splitting, TF-IDF vectorization
│   │   └── model_training.py      # GridSearchCV training for 6 models
│   ├── pipeline/
│   │   ├── training_pipeline.py   # End-to-end training orchestrator
│   │   └── prediction_pipeline.py # Inference pipeline with SHAP explanations
│   └── utils/
│       ├── email_utils.py         # Email parsing (MBOX, HTML, plain text)
│       ├── history_manager.py     # SQLite-backed classification history
│       ├── model_comparison.py    # Comparison dashboard (radar, confusion matrices)
│       ├── report_generator.py    # Downloadable HTML report generation
│       ├── url_analyzer.py        # URL extraction, risk scoring, threat detection
│       ├── logger.py              # Logging configuration
│       ├── state.py               # Data state management
│       └── utils.py               # General utility functions
│
├── tests/
│   ├── test_api.py                # API endpoint tests (19 tests)
│   ├── test_config.py             # Config auto-discovery tests
│   ├── test_email_utils.py        # Email parsing tests
│   ├── test_history_manager.py    # History CRUD + stats tests
│   ├── test_prediction_pipeline.py# Prediction pipeline tests (21 tests)
│   ├── test_report_generator.py   # HTML report generation tests
│   ├── test_url_analyzer.py       # URL detection + risk scoring tests
│   └── test_utils.py              # Utility function tests
│
├── data/
│   └── dataset/
│       └── dataset.csv            # Training dataset (SMS Spam Collection)
│
└── outputs/                       # Training artifacts (auto-generated, gitignored)
    └── YYYY-MM-DD_HH-MM-SS/
        ├── models/                # Trained model .pkl files
        └── observations/          # Metrics & comparison CSVs
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (or [uv](https://github.com/astral-sh/uv) for faster installation)

### Installation

```bash
# Clone the repository
git clone https://github.com/spam-email-classifier/spam-email-detection.git
cd spam-email-detection

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🖥️ Usage

### 1️⃣ Run the Streamlit Web App

The main interface with all features:

```bash
streamlit run app.py
```

Opens at **http://localhost:8501** with 4 tabs:

| Tab | Features |
|-----|----------|
| **📧 Single Email** | Classify one email with SHAP explanation, URL analysis, confidence gauge |
| **📦 Batch Processing** | Upload CSV/Excel files, paste multiple emails |
| **📊 Model Comparison** | Radar charts, confusion matrices, model ranking |
| **📜 History** | Search past classifications, view trends, export reports |

Additional features accessible from the sidebar:
- 🌙 **Dark/Light Theme Toggle** — One-click theme switching
- ⚡ **Real-time Typing Analysis** — Live predictions as you type with animated gauge
- 📄 **Download Report** — Generate comprehensive HTML reports

### 2️⃣ Run the FastAPI Server

For programmatic access:

```bash
# Start the server
uvicorn api:app --host 0.0.0.0 --port 8000

# Optional: enable API key authentication
export SPAM_API_KEY="your-secret-key"
```

#### API Endpoints

| Method | Endpoint | Rate Limit | Description |
|--------|----------|:----------:|-------------|
| `GET` | `/` | Unlimited | Root endpoint with available routes |
| `GET` | `/health` | Unlimited | Health check (uptime, model status) |
| `POST` | `/predict` | 30/min | Classify a single email |
| `POST` | `/predict/explain` | 10/min | Classify with SHAP explanation |
| `POST` | `/predict/batch` | 10/min | Batch classify multiple emails |
| `POST` | `/predict/file` | 10/min | Upload file for classification |
| `GET` | `/model/info` | 60/min | Get current model metadata |

**Example requests:**

```bash
# Health check
curl http://localhost:8000/health

# Classify an email
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"email": "Congratulations! You won a free prize!"}'

# With API key authentication
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key" \
  -d '{"email": "Hey, meeting at 3pm tomorrow."}'

# Batch classification
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"emails": ["Win a prize now!", "See you at lunch"]}'

# With SHAP explanation
curl -X POST http://localhost:8000/predict/explain \
  -H "Content-Type: application/json" \
  -d '{"email": "Free money!!! Click here"}'
```

Interactive API docs at **http://localhost:8000/docs** (Swagger UI).

### 3️⃣ CLI Tool

Classify emails directly from the terminal:

```bash
# Classify a quoted string
python classify.py "Congratulations! You won a prize!"

# Read from a file
python classify.py --file email.txt

# Pipe input
echo "Hey, are we still on for lunch?" | python classify.py
```

### 4️⃣ Train the Models

To retrain models on new data:

```bash
python -m src.pipeline.training_pipeline
```

The pipeline automatically:
1. Loads and validates the dataset from `data/dataset/dataset.csv`
2. Transforms text using TF-IDF vectorization
3. Trains 6 models with GridSearchCV hyperparameter tuning
4. Selects and saves the best performing model (by F1-score)
5. Generates comprehensive metrics reports

---

## ☁️ Deploy to Streamlit Cloud

Host the app for free on [Streamlit Cloud](https://share.streamlit.io) in under 5 minutes.

### Step 1 — Fork the Repository

Click **Fork** on GitHub to create your own copy, or push this repo to your own GitHub account.

### Step 2 — Go to Streamlit Cloud

1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**

### Step 3 — Configure the App

Fill in the settings:

| Field | Value |
|-------|-------|
| **Repository** | `your-username/Smart-Spam-Detector` |
| **Branch** | `main` |
| **Main file path** | `app.py` |

> `runtime.txt` (Python 3.11) and `.streamlit/config.toml` are auto-detected.

### Step 4 — Deploy

Click **"Deploy"**. Streamlit Cloud will:
1. Install dependencies from `requirements.txt`
2. Start the app on a public URL

### Step 5 — Train Models (First Run)

Since trained models are not committed to the repo, the first launch shows:

```
⚠️ No trained models found. Training is required before the app can work.
```

Click **"🚀 Train Models Now"** — training takes ~2–5 minutes on the free tier. Models are cached for the session via `@st.cache_resource`.

> **Note:** Streamlit Cloud has an ephemeral filesystem. Trained models and classification history (SQLite) are lost on app restart. The app handles this gracefully — just click **Train Models Now** again.

### Deployment Checklist

| Requirement | Status |
|-------------|--------|
| `app.py` at repo root | ✅ |
| `requirements.txt` at repo root | ✅ |
| `runtime.txt` → `python-3.11` | ✅ |
| `.streamlit/config.toml` (headless mode) | ✅ |
| Training dataset in git (`data/dataset/dataset.csv`) | ✅ |
| Auto-train fallback when models are missing | ✅ |

### Environment Variables (Optional)

No environment variables are required for basic usage. If you add a `.streamlit/secrets.toml` file, you can access secrets via `st.secrets`.

---

## ✨ Feature Deep Dive

### 🌓 Dark/Light Theme
Toggle between themes from the sidebar. All UI components—gauges, charts, tables, inputs—respond with smooth CSS transitions.

### ⚡ Real-time Typing Analysis
As you type an email, a lightweight model predicts spam probability in real-time (~1ms inference). An animated confidence gauge updates with color-coded feedback (green → yellow → red).

### 🎯 Animated Confidence Gauge
An SVG-based circular gauge with smooth `stroke-dashoffset` animation. Color interpolates from green (safe) through yellow (uncertain) to red (spam risk).

### 🔍 URL Risk Analysis
Every classified email is automatically scanned for URLs. The analyzer detects:
- Suspicious TLDs (`.xyz`, `.top`, etc.)
- URL shorteners (bit.ly, tinyurl, etc.)
- IP-based URLs (direct IP addresses)
- Deceptive keywords ("login", "verify", "secure", etc.)
- Non-HTTPS URLs

Each URL receives a risk score, and an overall email risk level is displayed.

### 📊 Model Comparison Dashboard
View all trained models side-by-side with:
- **🕸️ Radar Chart** — Compare accuracy, precision, recall, F1 across models
- **🔢 Confusion Matrices** — Per-model heatmaps with count + percentage annotations
- **🏅 Ranking Table** — Models sorted by F1-score with best model highlighted

### 📜 Classification History
Every classification is automatically saved to a local SQLite database. The History tab provides:
- **Trend Chart** — Daily classification volume over time
- **Search & Filter** — Filter by spam/ham status or search by email content
- **Pagination** — Browse through historical results
- **Export** — Download history as CSV

### 📄 HTML Report Generation
Download detailed HTML reports from the sidebar:
- Summary cards with key statistics
- Color-coded result tables
- SVG bar charts for visual analysis
- URL analysis details
- Works fully offline (self-contained HTML)

### 🔑 API Key Authentication
Protect the REST API by setting the `SPAM_API_KEY` environment variable. All endpoints (except `/health` and `/`) require a `Bearer` token in the `Authorization` header. Uses constant-time comparison to prevent timing attacks.

### 🚦 Rate Limiting
API endpoints are rate-limited using slowapi:
- `/predict` — 30 requests per minute
- `/predict/explain` — 10 requests per minute (SHAP is compute-intensive)
- `/predict/batch` — 10 requests per minute
- `/predict/file` — 10 requests per minute
- `/model/info` — 60 requests per minute
- `/health` and `/` — unlimited

---

## 🧪 Running Tests

The project has **100+ tests** covering all modules:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/ --cov-report=term-missing

# Run specific test file
pytest tests/test_prediction_pipeline.py -v

# Run API tests only
pytest tests/test_api.py -v
```

---

## ⚙️ Configuration

All configuration is managed through `src/config/config.py`:

```python
@dataclass
class Config:
    training_data_path: str = "data/dataset/dataset.csv"
    OUTPUT_BASE_DIR: str = "outputs"
    test_size: float = 0.2
    random_state: int = 42
```

Model hyperparameters for GridSearchCV are also configurable in the same file.

The API server can be configured via environment variables:
- `SPAM_API_KEY` — Enable API key authentication

---

## 📊 Model Performance

The training pipeline uses **5-fold cross-validation** with **GridSearchCV** to find optimal hyperparameters. Models are evaluated on:

- **Accuracy**: Overall correct predictions / total predictions
- **Precision**: True positives / (true positives + false positives)
- **Recall**: True positives / (true positives + false negatives)
- **F1-Score**: Harmonic mean of precision and recall

The best model is selected based on **F1-Score** and automatically saved for inference.

### Dataset
The model is trained on the **SMS Spam Collection** dataset:
- **5,574** SMS messages
- **4,827** Ham (legitimate) messages
- **747** Spam messages
- **86.6%** / **13.4%** class distribution

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function signatures
- Add docstrings for public functions/classes
- Write tests for new features

---

## 📝 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 🙏 Acknowledgments

- [SMS Spam Collection Dataset](https://archive.ics.uci.edu/ml/datasets/sms+spam+collection)
- [scikit-learn](https://scikit-learn.org/) for the ML framework
- [Streamlit](https://streamlit.io/) for the web app framework
- [FastAPI](https://fastapi.tiangolo.com/) for the REST API
- [SHAP](https://shap.readthedocs.io/) for model explainability

---

<div align="center">
    Made with ❤️ for the open-source community
</div>
