# Smart-Spam-Detector

## Stack
- **ML:** scikit-learn + XGBoost, TF-IDF vectorization, SHAP explanations
- **UI:** Streamlit (classification + model comparison)
- **API:** FastAPI with bearer token auth + slowapi rate limiting
- **Deployment:** Streamlit Cloud (UI), Railway/Docker (API)

## Dev commands
- `streamlit run app.py` — launch dashboard
- `uvicorn api:app --reload` — start API
- `pytest tests/ -v` — run tests
- `python src/pipeline/training_pipeline.py` — train models

## Key conventions
- 4-space indent for Python
- `src/components/` = ML pipeline stages, `src/pipeline/` = orchestration
- Model auto-discovery from `outputs/{timestamp}/models/`
- Config via `src/config/config.py` with auto-discovered model paths
- API key via `SPAM_API_KEY` env var
