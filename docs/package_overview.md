# Package Overview — Smart-Spam-Detector

Inventory of every module (post-restructure).

## 1. Interface Entry Points (root)

| Module | Responsibility | Entry point |
| --- | --- | --- |
| `api.py` | FastAPI REST API: `/health`, `/classify`, `/classify-batch`, `/classify-file`. | `uvicorn api:app` |
| `app.py` | Streamlit dashboard: classify, training, history, comparison, URL analysis, reports. | `streamlit run app.py` |
| `classify.py` | CLI classification (text / file / stdin). | `python classify.py` |

## 2. Core Package (`src/`)

| Module | Responsibility |
| --- | --- |
| `src/config/config.py` | Canonical paths + settings (leaf). |
| `src/components/data_ingestion.py` | `DataIngestion` — dataset loading. |
| `src/components/data_transformation.py` | `DataTransformation` — cleaning, vectorization, splitting. |
| `src/components/model_training.py` | `ModelTraining` — 6-model + ensemble training/eval. |
| `src/pipeline/training_pipeline.py` | `TrainingPipeline` — end-to-end training orchestration. |
| `src/pipeline/prediction_pipeline.py` | `PredictionPipeline` — artifact loading + inference. |
| `src/utils/email_utils.py` | Email text cleaning. |
| `src/utils/url_analyzer.py` | URL presence/risk analysis in emails. |
| `src/utils/history_manager.py` | Classification history persistence. |
| `src/utils/model_comparison.py` | Model comparison summaries. |
| `src/utils/report_generator.py` | Report generation. |
| `src/utils/state.py` | Shared app state helpers. |
| `src/utils/logger.py` | Logging setup. |
| `src/utils/utils.py` | Generic helpers. |

## 3. Tests (`tests/`)

8 modules: `test_api.py`, `test_config.py`, `test_email_utils.py`,
`test_history_manager.py`, `test_prediction_pipeline.py`, `test_report_generator.py`,
`test_url_analyzer.py`, `test_utils.py`.

## 4. Data & Artifacts

| Path | Responsibility |
| --- | --- |
| `data/dataset/dataset.csv` | Committed training dataset. |
| `outputs/2026-06-01_18-54-30/models/` | Tracked canonical run: 6 model `.pkl` + `vectorizer.pkl`. |
| `outputs/2026-06-01_18-54-30/observations/` | Tracked run metadata (comparison, CV, best params). |

## 5. Infrastructure

`Dockerfile` (api/app/dev targets), `docker-compose.yml`/`.dev.yml`/`.prod.yml`,
`Makefile`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `uv.lock`,
`.python-version`, `packages.txt`, `runtime.txt`.

## 6. Documentation (`docs/`)

Root suite: `architecture.md`, `folder_structure.md`, `module_dependency.md`,
`startup_flow.md`, `package_overview.md`. Migration records: `migration/`.
Categorized: `community/`, `design/`, `product/`, `project/`, `reference/`,
`technical/`.

## 7. Test Coverage

8 pytest modules covering API endpoints, config, utilities, and pipelines — run by CI
(`pytest tests/`) and `make test`.
