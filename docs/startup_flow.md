# Startup Flow — Smart-Spam-Detector

## 1. API Boot (FastAPI, :8000)

```
uvicorn api:app --host 0.0.0.0 --port 8000      # Docker api target
│
├─ 1. FastAPI app constructed (title, description)
├─ 2. HistoryManager initialized (persistence path via src.config)
├─ 3. Routes registered: GET /health · POST /classify · POST /classify-batch
│      · POST /classify-file (single/batch/file classification)
└─ 4. PredictionPipeline loads artifacts lazily on first request
       (outputs/2026-06-01_18-54-30/ → models/*.pkl + vectorizer)
```

## 2. Dashboard Boot (Streamlit, :8501)

```
streamlit run app.py                            # Docker app target / Cloud
│
├─ 1. app.py imports src.pipeline.* + src.utils.*
├─ 2. PredictionPipeline + ModelComparison + HistoryManager initialized
├─ 3. UI renders: classify tab, training tab, history, model comparison,
│      URL analysis, reports
└─ 4. Ready on :8501 (healthcheck /_stcore/health)
```

## 3. CLI

```
python classify.py "text"      | stdin        | --file email.txt
→ PredictionPipeline.predict(text) → Spam/Ham + score
```

## 4. Training Flow (dashboard tab or `TrainingPipeline`)

```
TrainingPipeline.run():
  1. DataIngestion  — load data/dataset/dataset.csv
  2. DataTransformation — clean (email_utils) + vectorize + split
  3. ModelTraining — train (6 models + Stacking ensemble), evaluate
  4. Persist run to outputs/<timestamp>/ (canonical run stays tracked)
```

## 5. Docker

- **api target**: deps → `COPY api.py app.py classify.py` + `COPY src/` + artifacts →
  `CMD uvicorn api:app`; healthcheck `/health`.
- **app target**: same base → `CMD streamlit run app.py`; healthcheck `/_stcore/health`.
- **dev target**: + pytest, hot reload.
- **compose**: api + app services; **Makefile**: `test` (pytest in api image),
  `lint` (compileall api.py app.py src).

## 6. CI (push/PR)

`ci.yml`: py_compile sweep → `src.*` import checks (DataIngestion,
DataTransformation, ModelTraining, TrainingPipeline, PredictionPipeline) →
`pytest tests/` (8 modules) → Bandit → lychee → Docker build + Trivy.

## 7. Failure Modes

| Failure | Behavior |
| --- | --- |
| Artifacts missing | PredictionPipeline auto-trains on first run (per .gitignore policy) or raises a clear error in strict mode |
| Dataset missing | DataIngestion fails loudly |
| Tests fail | CI red — `pytest tests/` gates every push |
