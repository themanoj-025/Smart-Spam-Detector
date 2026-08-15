# Module Dependency — Smart-Spam-Detector

**No circular imports.** Dependencies flow downward: interface entries → `src/`
pipelines → components/utils → config. All `src` modules import as a package
(`from src.x import ...`), which works because entry points run from the repo root.

## 1. Dependency Graph

```
  api.py ──┐      app.py ──┐       classify.py ──┐
           │              │                     │
           ▼              ▼                     ▼
  ┌────────────────────────────────────────────────────────┐
  │ src/pipeline/prediction_pipeline.py  PredictionPipeline│
  │ src/pipeline/training_pipeline.py    TrainingPipeline  │
  └───────┬────────────────────────────────────┬───────────┘
          │                                    │
          ▼                                    ▼
  ┌──────────────────────────────┐   ┌──────────────────────────────┐
  │ src/components/              │   │ src/utils/                   │
  │  data_ingestion.py           │   │  email_utils · url_analyzer  │
  │  data_transformation.py      │   │  history_manager · state     │
  │  model_training.py           │   │  model_comparison · logger   │
  └──────────────┬───────────────┘   │  report_generator · utils    │
                 │                   └──────────────┬───────────────┘
                 ▼                                  ▼
  ┌────────────────────────────────────────────────────────┐
  │ src/config/config.py   (canonical paths/settings, leaf) │
  └────────────────────────────────────────────────────────┘
```

## 2. Dependency Matrix

| Module | Imports | Consumed by |
| --- | --- | --- |
| `api.py` | `src.pipeline.prediction_pipeline`, `src.utils.history_manager` | `uvicorn api:app` |
| `app.py` | `src.pipeline.prediction_pipeline`, `src.pipeline.training_pipeline`, `src.utils.*` (email_utils, model_comparison, history_manager, url_analyzer, report_generator) | `streamlit run app.py` |
| `classify.py` | `src.pipeline.prediction_pipeline` | `python classify.py` |
| `src/pipeline/prediction_pipeline.py` | `src.config.config`, `src.components.data_transformation` | api, app, classify, tests |
| `src/pipeline/training_pipeline.py` | `src.config.config`, `src.components.*` | app (training UI), tests |
| `src/components/data_ingestion.py` | `src.config.config` | training_pipeline, tests |
| `src/components/data_transformation.py` | `src.config.config` | training + prediction pipelines, tests |
| `src/components/model_training.py` | `src.config.config` | training_pipeline, tests |
| `src/utils/*` | `src.config.config` (mostly) | app, api, tests |
| `src/config/config.py` | — (leaf) | everything |
| `tests/*` | `src.*` | CI (`pytest tests/`) |

## 3. Why This Shape

- **Interface/engine separation**: UI/API/CLI never contain ML logic — they delegate
  to `src.pipeline.*`, keeping the engine fully unit-testable headlessly.
- **Stage decomposition**: ingest → transform → train stages are independent leaves
  under `src/components/`, reusable by both training and prediction paths.
- **Central config**: `src/config/config.py` is the only place that knows artifact and
  data paths — the CI import checks pin this by importing it first.

## 4. Change Warnings

- **Renaming `src/`** breaks all three entry points + every CI import check + Makefile
  `compileall` — a coordinated, high-risk change with no benefit today (src-layout is
  already canonical).
- **Renaming the tracked output run dir** (`outputs/2026-06-01_18-54-30/`) breaks the
  artifact contract in `src/config/config.py` + `.gitignore` negations.
- **Adding a service entry point** should keep the "thin interface" pattern: import
  `src.pipeline.*`, never re-implement logic.
