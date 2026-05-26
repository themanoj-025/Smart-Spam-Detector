<div align="center">

# 📧 Spam Email Classifier

**A production-grade machine learning system for classifying emails as Spam or Ham (legitimate).**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange?logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
[![CI](https://github.com/themanoj-025/spam-email-classifier/actions/workflows/ci.yml/badge.svg)](https://github.com/themanoj-025/spam-email-classifier/actions/workflows/ci.yml)

</div>

---

## 🌟 Overview

This project implements a complete machine learning pipeline for **spam email detection**. It features:

- **🧠 Multiple ML Models**: Logistic Regression, Decision Trees, SVM, KNN, Random Forest, and a Stacking ensemble
- **🔧 Modular Pipeline Architecture**: Clean separation of data ingestion, transformation, and model training
- **🎨 Interactive Web UI**: Built with Streamlit for real-time email classification
- **📊 Comprehensive Analytics**: Detailed metrics, cross-validation, and model comparison
- **📂 Batch Processing**: Process entire MBOX email archives at once

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
| **scikit-learn** | ML models, preprocessing, evaluation |
| **pandas / numpy** | Data manipulation and analysis |
| **Streamlit** | Interactive web application |
| **BeautifulSoup4** | HTML email content parsing |
| **matplotlib** | Performance visualization |

---

## 📂 Project Structure

```
spam-email-classifier/
├── app.py                          # Streamlit web application
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project metadata & config
├── LICENSE                         # MIT License
├── README.md                       # This file
│
├── src/
│   ├── __init__.py
│   ├── config/
│   │   └── config.py              # Configuration & hyperparameters
│   ├── components/
│   │   ├── data_ingestion.py      # Dataset loading & validation
│   │   ├── data_transformation.py # Label encoding, splitting, TF-IDF
│   │   └── model_training.py      # Model training with GridSearchCV
│   ├── pipeline/
│   │   ├── training_pipeline.py   # End-to-end training orchestrator
│   │   └── prediction_pipeline.py # Inference pipeline
│   └── utils/
│       ├── email_utils.py         # Email parsing utilities
│       ├── logger.py              # Logging configuration
│       ├── state.py               # Data state management
│       └── utils.py               # General utility functions
│
├── Notebook Experiments/
│   └── Spam Email Detection.ipynb # Interactive experimentation notebook
│
├── data/
│   └── dataset/
│       └── dataset.csv            # Training dataset (SMS Spam Collection)
│
└── outputs/                       # Training artifacts (auto-generated)
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
git clone https://github.com/themanoj-025/spam-email-classifier.git
cd spam-email-classifier

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 1️⃣ Run the Web App

Launch the interactive Streamlit dashboard:

```bash
streamlit run app.py
```

Then open your browser to **http://localhost:8501** to start classifying emails!

### 2️⃣ Train the Models

To retrain models on new data:

```bash
# Place your dataset at: data/dataset/dataset.csv
# Then run:
python -m src.pipeline.training_pipeline
```

The pipeline will automatically:
1. Load and validate the dataset
2. Transform text data using TF-IDF vectorization
3. Train 5+ models with hyperparameter tuning
4. Select and save the best performing model
5. Generate comprehensive metrics reports

### 3️⃣ Interactive Notebook

For experimentation and exploration:

```bash
jupyter notebook "Notebook Experiments/Spam Email Detection.ipynb"
```

---

## 📊 Model Performance Details

The training pipeline uses **5-fold cross-validation** with **GridSearchCV** to find optimal hyperparameters for each model. Models are evaluated on:

- **Accuracy**: Overall correct predictions / total predictions
- **Precision**: True positives / (true positives + false positives)
- **Recall**: True positives / (true positives + false negatives)
- **F1-Score**: Harmonic mean of precision and recall

The best model is selected based on **F1-Score** and automatically saved for inference.

### Dataset
The model is trained on the **SMS Spam Collection** dataset, containing:
- **5,574** SMS messages
- **4,827** Ham (legitimate) messages
- **747** Spam messages
- **86.6%** / **13.4%** class distribution

---

## ⚙️ Configuration

All configuration is managed through `src/config/config.py`:

```python
@dataclass
class Config:
    training_data_path: str = "data/dataset/dataset.csv"
    OUTPUT_BASE_DIR: str = "outputs"
    # Model paths auto-discovered from latest training run
    test_size: float = 0.2
    random_state: int = 42
```

Model hyperparameters for GridSearchCV are also configurable in the same file.

---

## 🧪 Running Tests

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
pytest tests/ --cov=src/ --cov-report=term-missing
```

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

---

<div align="center">
    Made with ❤️ for the open-source community
</div>
