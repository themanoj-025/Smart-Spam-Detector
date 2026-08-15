# Folder Structure — Smart-Spam-Detector

Annotated tree of the **current (post-restructure)** layout, one-line purpose per entry.

```
Smart-Spam-Detector/
├── .github/
│   ├── CODEOWNERS / dependabot.yml / labeler.yml / ISSUE_TEMPLATE/
│   ├── copilot-instructions.md / PULL_REQUEST_TEMPLATE.md
│   └── workflows/                 # ci.yml, codeql, gitleaks, labeler, maintenance, stale, welcome
├── .gitignore / .dockerignore / .editorconfig / .gitattributes
├── .pre-commit-config.yaml       # Pre-commit format/lint gates
├── .python-version               # Python version pin
├── .vscode/settings.json
├── AGENTS.md · LICENSE · README.md · PROJECT_ANALYSIS.md · PROJECT_OVERVIEW.md
├── api.py                        # FastAPI REST interface (entry: uvicorn api:app)
├── app.py                        # Streamlit dashboard interface (entry: streamlit run app.py)
├── classify.py                   # CLI interface (entry: python classify.py)
├── src/                          # Shared ML engine package (src-layout)
│   ├── __init__.py
│   ├── config/config.py          # Canonical paths + settings
│   ├── components/               # Pipeline stage modules
│   │   ├── data_ingestion.py     #   DataIngestion
│   │   ├── data_transformation.py#   DataTransformation
│   │   └── model_training.py     #   ModelTraining
│   ├── pipeline/
│   │   ├── prediction_pipeline.py#   PredictionPipeline (inference)
│   │   └── training_pipeline.py  #   TrainingPipeline (orchestration)
│   └── utils/                    # email_utils, url_analyzer, history_manager,
│                                 #   model_comparison, report_generator, state,
│                                 #   logger, utils
├── tests/                        # 8 pytest modules (components, pipelines, utils, API)
├── data/
│   └── dataset/dataset.csv       # Committed training dataset
├── outputs/
│   └── 2026-06-01_18-54-30/      # Tracked canonical best-run (models/*.pkl, observations/)
│                                 #   — newer runs gitignored by design
├── logs/                         # Runtime logs (gitignored)
├── docs/
│   ├── architecture.md · folder_structure.md · module_dependency.md
│   ├── startup_flow.md · package_overview.md
│   ├── migration/                # migration_summary, old_tree_to_new_tree, file_move_ledger
│   ├── community/ design/ product/ project/ reference/ technical/
├── Dockerfile                    # Multi-stage: api / app / dev targets
├── docker-compose.yml / .dev.yml / .prod.yml
├── Makefile                      # compose ergonomics + test/lint targets
├── pyproject.toml · requirements.txt · requirements-dev.txt
├── packages.txt · runtime.txt    # system deps + runtime pin (Cloud/Docker)
├── uv.lock                       # uv lockfile (dependency pinning)
└── .env.example
```

## Top-level folder purposes

| Path | Purpose |
| --- | --- |
| `src/` | The ML engine — config, components, pipelines, utils (importable, tested). |
| Root `api.py` / `app.py` / `classify.py` | Thin interface entry points (REST / dashboard / CLI). |
| `tests/` | Pytest suite. |
| `data/` | Datasets. |
| `outputs/` | Training-run artifacts (canonical run tracked; rest gitignored). |
| `docs/` | Documentation suite. |
| `.github/` | CI/CD + community health. |
| Root files | Canonical metadata + runtime infra. |

## Root hygiene notes

- `logs/` is gitignored runtime output (untracked — no action).
- `Notebook Experiments/` is an **untracked** local folder (not part of the repo; no
  action — see move ledger).
- Root holds entry points + manifests only — no stray artifacts.
