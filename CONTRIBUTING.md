# Contributing to Smart-Spam-Detector

Thank you for your interest in contributing to Smart-Spam-Detector!

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Setup
1. Fork and clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. Install production dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. (Optional) Install development dependencies for testing:
   ```bash
   pip install -r requirements-dev.txt
   ```
5. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
6. Prepare the training data and train the model:
   ```bash
   # Place your dataset CSV at data/dataset/dataset.csv
   python -m src.pipeline.training_pipeline
   ```

### Running the Applications

**Streamlit web app:**
```bash
streamlit run app.py
```

**FastAPI server:**
```bash
uvicorn api:app --reload
```

**CLI tool:**
```bash
python classify.py "Your email text here"
python classify.py --file email.txt
```

### Environment Variables
| Variable | Default | Description |
|---|---|---|
| `SPAM_API_KEY` | — | API key for FastAPI Bearer token auth (optional) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

Note: Model paths are auto-discovered from the `outputs/` directory — no manual path configuration needed.

## Code Style

- Follow PEP 8 conventions.
- Use 4-space indentation.
- Write type hints for all function signatures.
- Add docstrings to public functions and classes.
- Use dataclasses for configuration objects (see `src/config/config.py`).

## Project Structure

- **`app.py`** — Streamlit web application
- **`api.py`** — FastAPI REST API
- **`classify.py`** — CLI tool for email classification
- **`src/`** — Core library
  - **`config/config.py`** — `Config` and `ModelConfig` dataclasses
  - **`components/data_ingestion.py`** — CSV data loading
  - **`components/data_transformation.py`** — TF-IDF vectorization
  - **`components/model_training.py`** — GridSearchCV + training
  - **`pipeline/training_pipeline.py`** — End-to-end training
  - **`pipeline/prediction_pipeline.py`** — Model loading + prediction + SHAP
  - **`utils/`** — Email parsing, URL analysis, history, reports
- **`data/dataset/dataset.csv`** — Training dataset
- **`outputs/`** — Timestamped training run directories (auto-discovered)

### Model Auto-Discovery
The `Config` class automatically finds the latest trained model from `outputs/`. No manual path updates are needed after training.

## Running Tests

```bash
pytest
```

Test files are in `tests/` (8 test modules):
- `test_api.py` — API endpoint tests
- `test_config.py` — Configuration tests
- `test_email_utils.py` — Email parsing tests
- `test_history_manager.py` — History persistence tests
- `test_prediction_pipeline.py` — Prediction pipeline tests
- `test_report_generator.py` — Report generation tests
- `test_url_analyzer.py` — URL analysis tests
- `test_utils.py` — General utility tests

## Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feat/my-feature
   ```
2. Make focused, minimal changes.
3. Run tests and ensure they pass:
   ```bash
   pytest
   ```
4. If adding new ML models, verify the training pipeline completes successfully:
   ```bash
   python -m src.pipeline.training_pipeline
   ```
5. Commit with a descriptive message:
   - Format: `type(scope): description`
   - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
   - Example: `feat(model): add GradientBoosting classifier`
   - Example: `fix(api): correct batch prediction response format`
6. Push and open a Pull Request.

## Reporting Issues

Include in your report:
- Steps to reproduce
- Error messages and stack traces
- Which interface is affected (Streamlit, API, CLI)
- Whether a trained model exists in `outputs/`

## Adding a New Classifier

1. Add the model and hyperparameter grid to `ModelConfig` in `src/config/config.py`.
2. The training pipeline (`src/pipeline/training_pipeline.py`) will automatically pick it up.
3. Add the import and registration in `src/components/model_training.py`.
4. Update the model list in the Streamlit UI (`app.py`) and API (`api.py`) if needed.

## API Authentication

- The FastAPI API uses Bearer token authentication.
- Set `SPAM_API_KEY` env var to enable authentication.
- Requests must include `Authorization: Bearer <key>` header.
- Rate limiting is configured via slowapi.

## Training Pipeline Notes

- The training pipeline expects a CSV at `data/dataset/dataset.csv`.
- The CSV must have `text` and `label` columns.
- Default test split: 20% (configurable via `Config.test_size`).
- GridSearchCV uses F1 scoring with 5-fold cross-validation.
- Results are saved to timestamped directories under `outputs/`.
- The `n_jobs` parameter defaults to 1 to prevent OOM on Streamlit Cloud.

## Code of Conduct

This project and everyone participating in it is governed by the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.
