# Smart-Spam-Detector — Project Overview

## 1. Project Title
**Smart-Spam-Detector** — An ML-powered email spam classification system with a Streamlit web app, FastAPI REST API, CLI tool, and SHAP-based explainability.

## 2. Executive Summary
Smart-Spam-Detector is a comprehensive email spam classification platform that uses multiple machine learning models (Logistic Regression, Decision Tree, SVM, KNN, Random Forest, XGBoost) trained on TF-IDF vectorized email text. It provides three interfaces: a Streamlit web application for interactive classification and analysis, a FastAPI REST API for programmatic access, and a command-line tool for batch processing. Key differentiators include SHAP-based prediction explanations, batch processing (MBOX, CSV, Excel), model comparison dashboards, URL analysis, and historical prediction tracking.

## 3. Problem Statement
Email spam remains a significant problem, and existing solutions (Gmail filters, Outlook Junk) are black boxes — users cannot understand why specific emails are classified as spam. Organizations need a transparent, self-hosted spam detection system that provides explainable predictions, supports batch analysis of existing mailboxes, and offers flexible deployment options (web UI, API, CLI).

## 4. Objectives
- Classify emails as spam or ham (not spam) with high accuracy
- Provide SHAP-based explanations for every prediction
- Support multiple ML models with automatic comparison
- Offer three interfaces: web app, REST API, and CLI
- Enable batch processing of MBOX, CSV, and Excel files
- Analyze URLs in emails for suspicious characteristics
- Track prediction history with local persistence
- Support model retraining with custom data

## 5. Key Features
- **Email classification:** Single email or batch processing (MBOX, CSV, Excel)
- **Multiple models:** Logistic Regression, Decision Tree, SVM, KNN, Random Forest, XGBoost — with hyperparameter tuning via GridSearchCV
- **Model comparison:** Side-by-side metrics (F1 scoring), confusion matrices, radar charts
- **SHAP explanations:** Visual breakdown of which words contributed to the classification
- **URL analysis:** Extract and score URLs for suspicious patterns (shortened URLs, suspicious TLDs, IP-based URLs)
- **API key authentication:** Secured FastAPI endpoints via Bearer token
- **Rate limiting:** Per-key rate limits on API
- **CLI tool:** Classify emails directly from command line
- **History tracking:** Local SQLite-based prediction history with search/filter
- **Report generation:** Visual and tabular reports of classification results
- **Model management:** Train, save, load, and compare model versions
- **Auto-discovery:** Latest trained model is automatically discovered from the outputs/ directory

## 6. System Architecture
```
User Interfaces
    ├── Streamlit App (app.py)
    │     ├── Single email classification
    │     ├── Batch processing (MBOX/CSV/Excel)
    │     ├── Model comparison dashboard
    │     ├── History viewer
    │     └── SHAP explanations
    │
    ├── FastAPI (api.py)
    │     ├── POST /predict (single)
    │     ├── POST /predict/batch
    │     ├── POST /upload (file)
    │     └── GET /model/info
    │
    └── CLI (classify.py)
          └── Classify file or stdin → print result
                │
                ▼
          Prediction Pipeline (src/pipeline/prediction_pipeline.py)
            ├── Load best model + vectorizer (auto-discovered from outputs/)
            ├── TF-IDF vectorization
            └── Classification → SHAP explanation
                │
                ▼
          Training Pipeline (src/pipeline/training_pipeline.py)
            ├── Data ingestion (CSV from data/dataset/dataset.csv)
            ├── TF-IDF transformation (configurable n-gram range)
            └── Model training + GridSearchCV evaluation
                │
                ▼
          Saved Artifacts (outputs/timestamped_run/)
            ├── models/*_model.pkl (trained model)
            ├── models/vectorizer.pkl (TF-IDF vectorizer)
            └── metrics/ (evaluation metrics)
```

## 7. Tech Stack
| Category | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Web UI** | Streamlit |
| **API Framework** | FastAPI |
| **CLI** | Python argparse (classify.py) |
| **ML Models** | scikit-learn (LogisticRegression, DecisionTree, SVM, KNN, RandomForest), XGBoost |
| **NLP** | NLTK (stopwords), TF-IDF (scikit-learn) |
| **Explainability** | SHAP |
| **Data Processing** | pandas, numpy |
| **Batch Processing** | mailbox (MBOX), openpyxl (Excel) |
| **URL Analysis** | tldextract, custom regex |
| **History Storage** | SQLite (via dataset library) |
| **Auth** | FastAPI Bearer token auth |
| **Rate Limiting** | slowapi |
| **Model Serialization** | pickle, joblib |
| **Visualization** | Matplotlib, Seaborn, plotly |
| **Testing** | pytest |
| **Deployment** | Docker, Streamlit Cloud (runtime.txt) |

## 8. Architecture Diagram
See Section 6 — modular design with shared prediction pipeline used by all three interfaces. Models are auto-discovered from timestamped output directories.

## 9. Folder Structure
```
Smart-Spam-Detector/
├── app.py                      # Streamlit web application
├── api.py                      # FastAPI REST API
├── classify.py                 # CLI tool for email classification
├── pyproject.toml              # Project metadata + dependencies
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── runtime.txt                 # Python runtime version
├── packages.txt                # System packages for deployment
├── Dockerfile                  # Docker deployment
├── data/
│   └── dataset/
│       └── dataset.csv         # Training dataset
├── src/
│   ├── __init__.py
│   ├── config/
│   │   └── config.py           # Config (auto-discovers latest model), ModelConfig (hyperparameter grids)
│   ├── components/
│   │   ├── data_ingestion.py   # CSV data loading and validation
│   │   ├── data_transformation.py  # TF-IDF vectorization, train/test split
│   │   └── model_training.py   # Model training, GridSearchCV, evaluation
│   ├── pipeline/
│   │   ├── training_pipeline.py    # End-to-end training workflow
│   │   └── prediction_pipeline.py  # Model loading + prediction + explanation
│   └── utils/
│       ├── email_utils.py      # Email body extraction, text cleaning
│       ├── url_analyzer.py     # URL extraction and suspicious scoring
│       ├── model_comparison.py # Model comparison utilities
│       ├── history_manager.py  # SQLite-based prediction history
│       └── report_generator.py # Classification report generation
├── outputs/                    # Timestamped training run directories (auto-discovered)
├── tests/
│   ├── __init__.py
│   ├── test_api.py             # API endpoint tests
│   ├── test_config.py          # Configuration tests
│   ├── test_email_utils.py     # Email utility tests
│   ├── test_history_manager.py # History manager tests
│   ├── test_prediction_pipeline.py # Pipeline tests
│   ├── test_report_generator.py   # Report generator tests
│   ├── test_url_analyzer.py    # URL analyzer tests
│   └── test_utils.py           # General utility tests
├── .streamlit/
│   └── config.toml             # Streamlit configuration
├── .env.example                # Environment variable template
└── README.md                   # Project documentation
```

## 10. Module Overview
- **prediction_pipeline.py:** Central orchestrator — loads latest trained model + vectorizer (auto-discovered from outputs/), vectorizes input text, classifies, generates SHAP explanation
- **training_pipeline.py:** End-to-end training — data ingestion → transformation → model training with GridSearchCV → evaluation → serialization to timestamped output directory
- **model_training.py:** Trains 6 classifiers (LogisticRegression, DecisionTree, SVM, KNN, RandomForest, XGBoost) with hyperparameter tuning via GridSearchCV, evaluates using F1 scoring, saves best models
- **data_transformation.py:** TF-IDF vectorization with configurable n-gram range, max features, and stop words; train/test split with configurable test_size (default 0.2)
- **data_ingestion.py:** Loads CSV data from `data/dataset/dataset.csv`, validates schema, handles missing values
- **url_analyzer.py:** Extracts URLs from email body, checks against suspicious patterns (shortened URLs, IP-based URLs, suspicious TLDs using tldextract), returns risk score
- **email_utils.py:** Extracts email body from raw MIME messages, cleans text, handles encoding
- **history_manager.py:** SQLite-based storage for prediction results with search and filter capabilities

## 11. Database Overview
**Engine:** SQLite (via the `dataset` library)
- **Usage:** Local storage of prediction history
- **Tables:** Predictions (email text, prediction result, confidence, model used, timestamp)
- No ORM migrations — schema is created dynamically by the `dataset` library
- Primary data source for training is the CSV file (`data/dataset/dataset.csv`), not the database

## 12. API Overview
### FastAPI Endpoints (api.py)
- `POST /predict` — Classify a single email (text or file). Returns spam/ham + confidence + SHAP explanation
- `POST /predict/batch` — Batch classify multiple emails
- `POST /upload` — Upload a file for classification
- `GET /model/info` — Get model metadata (type, accuracy, features)
- All endpoints require Bearer token authentication (Authorization: Bearer <key>)

## 13. Authentication & Authorization
- **API:** Bearer token authentication (key configured via `SPAM_API_KEY` env var, sent in `Authorization: Bearer <key>` header)
- **Rate limiting:** Per-key rate limiting via slowapi
- **Streamlit app:** No authentication (open access)
- **CLI:** No authentication (local tool)
- No user management, no role-based access, no OAuth

## 14. Data Flow
1. **Training flow:** Raw CSV (data/dataset/dataset.csv) → DataIngestion (validate) → DataTransformation (TF-IDF) → ModelTraining (GridSearchCV + train + evaluate) → Saved model + vectorizer in timestamped `outputs/` directory
2. **Prediction flow:** User input text → PredictionPipeline → Auto-discover latest model from `outputs/` → Load model/vectorizer → Vectorize → Classify → SHAP explain → Return result + explanation
3. **Batch flow:** MBOX/CSV/Excel file → Parse → Predict each email → Store results in history (SQLite) → Display summary report

## 15. Request Lifecycle (API)
HTTP Request → FastAPI → Bearer Token Auth Middleware → Rate Limiter (slowapi) → Route Handler → PredictionPipeline → SHAP Explanation → JSON Response

## 16. External Integrations
No external third-party services or APIs are integrated. All processing is local — the ML models are trained and run entirely on-device. NLTK data (stopwords) is downloaded locally.

## 17. Environment Variables
From `.env.example`:
| Variable | Purpose |
|---|---|
| `SPAM_API_KEY` | API key for FastAPI Bearer token authentication (optional) |
| `LOG_LEVEL` | Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

Note: Model paths and data paths are auto-discovered by the `Config` class — no environment variables needed for them.

## 18. Configuration
The `Config` class in `src/config/config.py` defines:
- **Auto-discovery:** Latest trained model and vectorizer are found from the `outputs/` directory (sorted by timestamped run directory name)
- **Data path:** `data/dataset/dataset.csv` (default, auto-resolved relative to project root)
- **Output directory:** `outputs/` (auto-resolved)
- **Test size:** 0.2 (configurable)
- **Random state:** 42 (configurable)

The `ModelConfig` dataclass defines hyperparameter grids for 6 classifiers:
- **LogisticRegression:** C=[0.01, 0.1, 1, 10, 100], solver=[lbfgs, liblinear], max_iter=[100, 200, 300]
- **DecisionTree:** criterion=[gini, entropy], max_depth=[5, 10, 15, 20, None], min_samples_split=[2, 5, 10], min_samples_leaf=[1, 2, 4]
- **SVM:** C=[0.1, 1, 10], kernel=[linear, rbf], gamma=[scale, auto]
- **KNN:** n_neighbors=[3, 5, 7, 9, 11], weights=[uniform, distance], metric=[euclidean, manhattan]
- **RandomForest:** n_estimators=[50, 100, 200], max_depth=[10, 20, 30, None], min_samples_split=[2, 5, 10], min_samples_leaf=[1, 2, 4], max_features=[sqrt, log2]
- **XGBoost:** n_estimators=[100, 200], max_depth=[3, 6, 10], learning_rate=[0.01, 0.1, 0.2], subsample=[0.8, 1.0]

CV folds: 5, Scoring: F1, n_jobs: 1 (to prevent OOM on Streamlit Cloud).

## 19. Security Measures
- **Bearer token auth:** All API endpoints require valid API key in Authorization header
- **Rate limiting:** Prevents abuse via slowapi
- **Input validation:** Email text is sanitized and cleaned before processing
- No HTTPS enforcement, no encryption at rest, no data anonymization

## 20. Logging & Monitoring
Basic Python logging configured with configurable log level via `LOG_LEVEL` env var. No external monitoring, metrics, or alerting.

## 21. Error Handling
- **API:** Structured error responses via FastAPI exception handlers
- **Streamlit:** try/except blocks with user-friendly error messages
- **CLI:** Error messages printed to stderr with non-zero exit codes

## 22. Performance Optimizations
- **Model caching:** Models are loaded once and cached in memory
- **Batch processing:** Efficiently processes MBOX files without loading entire file into memory
- **TF-IDF caching:** Pre-computed vectorizer in pipeline
- **Auto-discovery:** Latest model found automatically, no manual path updates needed
- No async processing, no database connection pooling

## 23. Deployment Architecture
- **Docker:** Dockerfile for containerized deployment
- **Streamlit Cloud:** runtime.txt + packages.txt for cloud deployment
- **FastAPI standalone:** Deployable via uvicorn
- Models must be pre-trained (outputs/ directory) or trained at startup

## 24. Testing Strategy
- **Framework:** pytest
- **Test files:** 8 test modules covering: API, config, email utils, history manager, prediction pipeline, report generator, URL analyzer, general utilities
- Good test coverage across core modules
- No CI pipeline configured

## 25. Development Workflow
No CONTRIBUTING.md found. No documented conventions.

## 26. Known Limitations
- **English only:** Models are trained on English text; may not generalize to other languages
- **No deep learning:** Uses traditional ML (TF-IDF + classifiers); no transformer models (BERT, etc.)
- **Static training data:** Model needs retraining to adapt to new spam patterns
- **Single-user API:** API key auth is simple; no multi-user or multi-tenant support
- **No container orchestration:** Dockerfile exists but no docker-compose or k8s configs

## 27. Future Roadmap
No documented roadmap found. Code evidence suggests:
- Transformer-based models (BERT/RoBERTa) integration
- Enhanced phishing detection
- Real-time email monitoring integration

## 28. Troubleshooting
- **No trained model:** Run the training pipeline (`python -m src.pipeline.training_pipeline`) to train and save models to `outputs/`
- **API authentication fails:** Set `SPAM_API_KEY` env var with your secret key
- **Memory issues with large MBOX:** Process in smaller batches using the `--max-emails` CLI flag
- **SHAP explanation fails:** SHAP can be slow for large feature spaces; consider reducing max_features in config
- **Model not found after training:** The Config class auto-discovers the latest model from the `outputs/` directory — ensure training completed successfully

## 29. FAQ
- **How to run the Streamlit app?** `streamlit run app.py`
- **How to run the API?** `uvicorn api:app --reload`
- **How to use the CLI?** `python classify.py "your email text"` or `python classify.py --file email.txt`
- **How to retrain the model?** Run `python -m src.pipeline.training_pipeline`
- **How to get API keys?** Set the `SPAM_API_KEY` environment variable.
- **What models are used?** Logistic Regression, Decision Tree, SVM, KNN, Random Forest, and XGBoost.

## 30. Contributing Guidelines
Not yet defined. No CONTRIBUTING.md file exists in the repository.

## 31. License
No license file found in the repository root.

## 32. Maintainers & Contacts
No author/maintainer information specified in source files.
