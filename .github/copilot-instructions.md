# Smart-Spam-Detector — Copilot Instructions

## Code conventions
- Python with 4-space indentation
- scikit-learn + XGBoost for ML, TF-IDF for feature extraction
- FastAPI for API with bearer token auth + rate limiting
- Streamlit for dashboard UI

## Key commands
- Dashboard: `streamlit run app.py`
- API: `uvicorn api:app --reload --port 8000`
- Tests: `pytest tests/ -v`
- Train: `python src/pipeline/training_pipeline.py`

## Architecture
- `src/components/` — data_ingestion, data_transformation, model_training
- `src/pipeline/` — training_pipeline, prediction_pipeline
- `src/config/config.py` — Config dataclass with auto-discovery of latest model
- Models auto-discovered from `outputs/{timestamp}/models/`
- API key via `SPAM_API_KEY` env var for bearer auth
