# Dependency Graph — Smart-Spam-Detector

## Module Dependency Map

```
app.py (Streamlit UI)
  ├── classify.py
  │     ├── sklearn (TfidfVectorizer, classifier)
  │     ├── joblib/pickle
  │     ├── re (regex for URLs)
  │     └── numpy
  └── src/__init__.py (config)

api.py (FastAPI)
  ├── classify.py (shared logic)
  ├── fastapi
  ├── pydantic
  └── src/__init__.py (config)

tests/
  ├── test_api.py → api.py, classify.py
  ├── test_classify.py → classify.py
  ├── test_email_utils.py → classify.py (utils)
  ├── test_history_manager.py → classify.py (history)
  ├── test_prediction_pipeline.py → classify.py
  ├── test_report_generator.py → classify.py
  ├── test_url_analyzer.py → classify.py (URL utils)
  ├── test_config.py → src/__init__.py
  └── test_utils.py → utils
```

## External Dependencies
| Package | Used By | Purpose |
|---------|---------|---------|
| streamlit | app.py | Web UI |
| fastapi | api.py | REST API framework |
| uvicorn | api.py | ASGI server |
| scikit-learn | classify.py | ML: TF-IDF + classifier |
| pydantic | api.py, src/ | Data validation |
| pytest | tests/ | Testing framework |
| joblib | classify.py | Model serialization |

## Critical Files
- **classify.py**: Core ML logic — shared by both interfaces
- **app.py**: Streamlit UI entry point
- **api.py**: FastAPI entry point
