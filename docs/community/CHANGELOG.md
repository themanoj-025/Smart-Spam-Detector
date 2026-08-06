# Changelog

All notable changes to **Smart-Spam-Detector** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-06-01

### Added

#### ML Pipeline
- 6 trained models: Logistic Regression, Decision Tree, SVM, KNN, Random Forest, Stacking ensemble
- GridSearchCV hyperparameter tuning for all models
- TF-IDF vectorization with n-gram analysis
- Best model: Stacking Classifier with 98.7% accuracy, 98.6% precision, 99.9% recall
- Model auto-discovery from timestamped `outputs/` directories
- Feature importance and word contribution analysis

#### Streamlit Dashboard
- **Single Email Classification** — Paste email text for instant Spam/Ham classification
- **Animated confidence gauge** with color interpolation (green → yellow → red)
- **SHAP word-level explanations** — Visual breakdown of which words influenced the prediction
- **URL risk analysis** — Detection of suspicious links, shorteners, and phishing patterns
- **Real-time typing analysis** — Live spam probability gauge updating as you type
- **Batch Processing** — Upload MBOX, CSV, or Excel files for bulk classification
- **Model Comparison** — Radar charts, confusion matrices, ranking tables
- **Classification History** — SQLite-backed history with search, filter, trend charts, CSV export
- **HTML Reports** — Downloadable self-contained reports with charts and statistics
- **Dark/Light theme** toggle with smooth CSS transitions

#### REST API (FastAPI)
- `POST /predict` — Classify email text → spam/ham with confidence scores
- `POST /predict/batch` — Batch classification
- `POST /upload` — Upload file for classification
- `GET /model/info` — Current model metadata
- Bearer token authentication via `SPAM_API_KEY`
- Rate limiting via slowapi

#### Security
- Bearer token authentication for API endpoints
- Per-key rate limiting to prevent abuse
- Input sanitization (encoding handling, text extraction)
- File upload validation (content type, size)

#### Testing
- 100+ unit tests across 8 test modules
- Tests covering: API, config, email utils, history manager, prediction pipeline, report generator, URL analyzer, utils

#### Deployment
- Streamlit Cloud ready with `runtime.txt` and `packages.txt`
- Docker support for containerized deployment

---

## [0.1.0] — Initial Development

### Added
- Project scaffolding
- SMS Spam Collection dataset integration
- Initial model training pipeline
- Basic Streamlit app
