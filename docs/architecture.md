# Architecture — Smart-Spam-Detector

## System Architecture

```
User (Browser)
       │
       ├── Streamlit App (app.py) ───── Web UI
       │         │
       │         ├── classify.py ───── ML Classification Engine
       │         │     ├── TF-IDF Vectorizer
       │         │     └── ML Classifier (Naive Bayes / Logistic Regression)
       │         │
       │         └── Tests (tests/)
       │
       └── FastAPI (api.py) ─────────── REST API
                 │
                 └── classify.py ───── Shared Classification Logic
```

## Architecture Overview
- **Dual-interface**: Streamlit UI + FastAPI REST API
- **Shared logic**: `classify.py` serves both interfaces
- **Modular testing**: Comprehensive test suite in `tests/`

## Component Responsibilities
| Component | File | Role |
|-----------|------|------|
| Web UI | app.py | Streamlit user interface |
| REST API | api.py | FastAPI API endpoints |
| Classification | classify.py | Core ML classification logic |
| Config | src/__init__.py | Package initialization |
| Tests | tests/*.py | Unit and integration tests |

## Design Decisions
- Dual interface (UI + API) provides flexibility
- Shared classify module ensures consistent predictions
- TF-IDF avoids need for deep learning infrastructure
