# MEMORY.md — Smart-Spam-Detector

## Project Overview
Smart-Spam-Detector is an intelligent email/spam classification system with a Streamlit web UI and a FastAPI REST API. It uses TF-IDF vectorization and classification algorithms to detect spam emails.

## Business Purpose
Provide users with a tool to analyze emails and determine if they are spam or legitimate (ham), with detailed reporting and URL analysis capabilities.

## Tech Stack
| Category | Technology |
|----------|------------|
| Language | Python 3.12 |
| Web UI | Streamlit |
| API | FastAPI |
| ML | scikit-learn (TF-IDF + Classifier) |
| Testing | pytest |
| Config | pydantic-settings |
| Deployment | Streamlit Cloud / Render |
| Async | Python asyncio |

## Repository Structure
```
Smart-Spam-Detector/
├── app.py                  # Streamlit web application
├── api.py                  # FastAPI REST API
├── classify.py             # Classification logic
├── src/                    # Source package
├── tests/                  # Test suite
├── requirements.txt        # Dependencies
├── packages.txt            # System packages (for deployment)
├── runtime.txt             # Python version
└── pyproject.toml          # Project config
```

## Key Features
- Email classification (spam vs ham)
- URL analysis within emails
- Prediction history management
- Report generation
- REST API for programmatic access

## Data Flow
```
User Input (email text)
       ↓
  classify.py (TF-IDF Vectorizer + ML Classifier)
       ↓
  Classification Result (spam/ham)
       ↓
  UI Display or API Response
```
