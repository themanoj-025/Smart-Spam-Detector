# Architecture — Smart-Spam-Detector

> Production-grade ML system for classifying emails as **Spam or Ham**, with three
> interface surfaces (REST API, Streamlit dashboard, CLI) sharing one `src/` package
> and one trained-artifact contract.

---

## 1. System Overview

```
   INTERFACE LAYER (root entry points — thin, no business logic)
   ┌───────────────┐   ┌────────────────────┐   ┌───────────────┐
   │ api.py        │   │ app.py             │   │ classify.py   │
   │ FastAPI REST  │   │ Streamlit dashboard│   │ CLI           │
   │ /health,      │   │ (2400+ lines UI)   │   │               │
   │ /classify...  │   └─────────┬──────────┘   └───────┬───────┘
   └───────┬───────┘             │                      │
           └──────────────┬──────┴──────────────────────┘
                          │  from src.* import ...
                          ▼
   src/  (shared package — the entire ML engine)
   ├── pipeline/
   │   ├── prediction_pipeline.py   PredictionPipeline
   │   └── training_pipeline.py     TrainingPipeline
   ├── components/
   │   ├── data_ingestion.py        DataIngestion
   │   ├── data_transformation.py   DataTransformation
   │   └── model_training.py        ModelTraining
   ├── config/config.py             paths + settings
   └── utils/                       email_utils, url_analyzer, history_manager,
                                    model_comparison, report_generator, state,
                                    logger, utils
                          │
                          ▼
   data/dataset/dataset.csv ──► training ──► outputs/2026-06-01_18-54-30/
                                              (models/*.pkl, observations/*)
```

## 2. Major Components

| Component | Location | Responsibility |
| --- | --- | --- |
| REST API | `api.py` | FastAPI: `/health`, single/batch/file classification endpoints. Entry: `uvicorn api:app` (Docker CMD). |
| Dashboard | `app.py` | Streamlit UI (classification, training, history, model comparison, URL analysis, reports). Entry: `streamlit run app.py`. |
| CLI | `classify.py` | Text/file/stdin classification. Entry: `python classify.py`. |
| Prediction | `src/pipeline/prediction_pipeline.py` | Loads artifacts, vectorizes, predicts, returns labels. |
| Training | `src/pipeline/training_pipeline.py` | End-to-end training orchestration (ingest → transform → train). |
| Components | `src/components/` | `DataIngestion`, `DataTransformation`, `ModelTraining` (step modules). |
| Config | `src/config/config.py` | Canonical paths/settings. |
| Utils | `src/utils/` | `email_utils` (cleaning), `url_analyzer`, `history_manager`, `model_comparison`, `report_generator`, `state`, `logger`, `utils`. |
| Data | `data/dataset/dataset.csv` | Committed training dataset. |
| Artifacts | `outputs/2026-06-01_18-54-30/` | **Tracked by design** — the canonical training run (`models/*.pkl`, `observations/*`); newer runs are gitignored (`outputs/`). |
| Tests | `tests/` | 8 pytest modules covering components, pipelines, utils, API. |
| Infra | Dockerfile (api + app targets), compose, Makefile, `.pre-commit-config.yaml`, `uv.lock` | Build/run/CI/format-gates/dep-pinning (uv). |

## 3. Runtime Model

- **Two long-lived services** (Docker compose): `api` (uvicorn, :8000, healthcheck
  `/health`) and `app` (streamlit, :8501, healthcheck `/_stcore/health`).
- **Shared artifacts**: both services load `outputs/2026-06-01_18-54-30/` via
  `PredictionPipeline`; artifacts auto-trained on first run if absent (per .gitignore
  policy).
- **Persistence**: classification history persisted via `src/utils/history_manager.py`.

## 4. Key Design Points

1. **Thin interfaces, fat package** — `api.py`/`app.py`/`classify.py` contain only
   I/O + presentation; all ML logic lives in `src/` (importable, unit-tested).
2. **Pipeline decomposition** — training split into ingest/transform/train stages so
   each stage is independently testable and reusable.
3. **Canonical best-run retention** — `outputs/` is gitignored except the designated
   first run, so the app always has a known-good artifact set without bloating the repo.

## 5. Configuration

`.env.example` documents env vars; `src/config/config.py` reads them. `.python-version`
pins the interpreter; `uv.lock` pins deps; `packages.txt` lists system packages.

## 6. Deployment

- **Docker**: multi-stage; `api` target runs uvicorn, `app` target runs streamlit;
  dev target adds pytest.
- **CI** (`ci.yml`): py_compile sweep → `src.*` import checks (DataIngestion,
  DataTransformation, ModelTraining, TrainingPipeline, PredictionPipeline) →
  `pytest tests/` → Bandit → lychee → Docker build + Trivy.
- **Makefile**: `test` (pytest in api image), `lint` (compileall api.py app.py src).

See also: `docs/module_dependency.md`, `docs/startup_flow.md`,
`docs/package_overview.md`, `docs/migration/old_tree_to_new_tree.md`.
