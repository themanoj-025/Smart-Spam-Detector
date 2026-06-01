<div align="center">

# 📧 Spam Email Classifier

**A production-grade machine learning system for classifying emails as Spam or Ham (legitimate).**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange?logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

### 🚀 **[Try the Live App →](https://smart-spam-detector.streamlit.app)**

![Deploy](https://img.shields.io/badge/Deployed_on-Streamlit_Cloud-ff4b4b?logo=streamlit&logoColor=white)

</div>

---

## 🌟 Overview

This project implements a complete machine learning pipeline for **spam email detection** with an interactive web dashboard featuring real-time analysis, explainable AI, and a polished dark/light theme.

### ✨ Live Demo

> **🔗 [smart-spam-detector.streamlit.app](https://smart-spam-detector.streamlit.app)**
>
> No installation needed — try it directly in your browser! Paste any email text and get an instant spam/ham classification with confidence scores and word-level AI explanations.

### What's Included

- **🧠 6 ML Models**: Logistic Regression, Decision Tree, SVM, KNN, Random Forest, and Stacking ensemble
- **🎨 Polished Dashboard**: Real-time typing analysis, animated confidence gauge, dark/light theme, glassmorphism cards
- **🔍 SHAP Explainability**: Word-level contributions showing exactly why an email was flagged
- **🔗 URL Risk Analysis**: Automatic detection of suspicious links, shorteners, and phishing patterns
- **📂 Batch Processing**: Upload CSV, Excel, or MBOX files for bulk classification
- **📊 Model Comparison**: Radar charts, confusion matrices, and ranking tables
- **📜 Classification History**: SQLite-backed history with search, filter, trend charts, and CSV export
- **📄 HTML Reports**: Downloadable self-contained reports with charts and statistics
- **⚡ Real-time Typing Analysis**: Live spam probability gauge that updates as you type

---

## 🚀 Key Results

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|:--------:|:---------:|:------:|:--------:|
| **🏆 Stacking Classifier** | **98.7%** | **98.6%** | **99.9%** | **99.2%** |
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
| **Streamlit** | Interactive web dashboard |
| **SHAP** | Model explainability (word-level contributions) |
| **Plotly** | Radar charts, confusion matrices |
| **BeautifulSoup4** | HTML email content parsing |
| **SQLite3** | Classification history storage |
| **openpyxl** | CSV/Excel upload support |

---

## 📂 Project Structure

```
Smart-Spam-Detector/
├── app.py                          # Streamlit web application
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project metadata & config
├── runtime.txt                     # Python version for Streamlit Cloud
├── packages.txt                    # System packages for Streamlit Cloud
├── .streamlit/config.toml          # Streamlit configuration
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
├── tests/                          # 100+ unit tests
│
├── data/
│   └── dataset/
│       └── dataset.csv            # Training dataset (SMS Spam Collection)
│
└── outputs/                       # Trained model artifacts
    └── YYYY-MM-DD_HH-MM-SS/
        ├── models/                # Trained model .pkl files
        └── observations/          # Metrics & comparison CSVs
```

---

## ⚡ Quick Start

### Try It Online (No Setup)

👉 **[Open the Live App](https://smart-spam-detector.streamlit.app)** — classify emails instantly in your browser.

### Run Locally

```bash
# Clone the repository
git clone https://github.com/themanoj-025/Smart-Spam-Detector.git
cd Smart-Spam-Detector

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

Opens at **http://localhost:8501**.

### Train Models (First Run)

```bash
python -m src.pipeline.training_pipeline
```

The pipeline automatically loads the dataset, trains 6 models with GridSearchCV, and saves the best model.

---

## 🎨 Dashboard Features

### 📧 Single Email Classification
- Paste any email and get instant Spam/Ham classification
- **Animated confidence gauge** with color interpolation (green → yellow → red)
- **SHAP word-level explanations** showing which words pushed toward spam or ham
- **URL risk analysis** detecting suspicious links, shorteners, and phishing patterns
- **Downloadable HTML reports** with full classification details

### 📂 Batch Processing
- Upload **MBOX files** (from Gmail, Thunderbird, etc.)
- Upload **CSV or Excel** files with auto-detection of email text columns
- Progress bar and summary statistics for bulk processing
- Export results as CSV or HTML report

### 📊 Model Comparison Dashboard
- **🕸️ Radar Chart** — Visual comparison of accuracy, precision, recall across models
- **🔢 Confusion Matrices** — Per-model heatmaps with count + percentage annotations
- **🏅 Ranking Table** — Models sorted by F1-score with best model highlighted

### 📜 Classification History
- **Trend Chart** — Daily classification volume over time
- **Search & Filter** — Filter by spam/ham or search by email content
- **Pagination** — Browse through historical results
- **Export** — Download full history as CSV or HTML report

### ⚡ Real-time Typing Analysis
As you type an email, a lightweight model predicts spam probability in real-time (~1ms inference). An animated SVG gauge updates with color-coded feedback.

### 🌓 Dark/Light Theme
Toggle between themes from the sidebar with smooth CSS transitions across all components — gauges, charts, tables, and inputs.

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
```

---

## 📊 Dataset

The model is trained on the **SMS Spam Collection** dataset:
- **5,574** SMS messages
- **4,827** Ham (legitimate) messages
- **747** Spam messages
- **86.6% / 13.4%** class distribution

---

## ☁️ Deploy to Streamlit Cloud

The app is already live at **[smart-spam-detector.streamlit.app](https://smart-spam-detector.streamlit.app)**. To deploy your own fork:

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → Select your fork → Branch: `main` → Main file: `app.py`
4. Click **"Deploy"**

All configuration files (`runtime.txt`, `packages.txt`, `.streamlit/config.toml`) are pre-configured.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 🙏 Acknowledgments

- [SMS Spam Collection Dataset](https://archive.ics.uci.edu/ml/datasets/sms+spam+collection)
- [scikit-learn](https://scikit-learn.org/) for the ML framework
- [Streamlit](https://streamlit.io/) for the web app framework
- [SHAP](https://shap.readthedocs.io/) for model explainability
- [Plotly](https://plotly.com/) for interactive charts

---

<div align="center">

**🔗 [Try the Live App →](https://smart-spam-detector.streamlit.app)**

Made with ❤️ for the open-source community

</div>
