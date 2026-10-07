# AGENTS.md — Smart-Spam-Detector

> Canonical project instructions. Pointers like `CLAUDE.md` or
> `.github/copilot-instructions.md` should say "See AGENTS.md".

---

## Project overview

**Smart-Spam-Detector** — a machine-learning spam detection service.
Core components:

- **Model** — classifier for spam vs. legitimate content.
- **API** — FastAPI service exposing detection endpoints.
- **Pipeline** — inference + scoring service.
- **Web / Dashboard** — review UI.

Stack: Python 3.11+ · scikit-learn / LightGBM · FastAPI · Streamlit.

---

## Exact commands

```bash
# Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Lint / typecheck / test
make lint
pre-commit run --all-files
python -m mypy . --ignore-missing-imports
python -m pytest tests/ -v --cov=. --cov-fail-under=70

# Run
uvicorn api.main:app --reload
streamlit run dashboard/app.py
```

---

## Folder map

| Path | Purpose |
|------|---------|
| `model/` | Classifier + training |
| `api/` | FastAPI application |
| `pipeline/` | Inference + scoring jobs |
| `dashboard/` | Streamlit dashboard |
| `tests/` | pytest suite |
| `.github/workflows/` | CI (ruff, mypy, pytest, gitleaks, trivy) |

## Do / don't

- **Do** keep the model interface stable so the classifier can swap
  without breaking the API.
- **Do not** commit `.env` files.
- **Do not** commit message content with real user data.

## Security rules

- No secrets in the repository; `gitleaks` CI gate gates on hits.
- Message content containing real PII must be anonymized before any file
  leaves the sandbox.

## AI-assistance convention

Commits authored by AI must carry the trailer:

```text
AI-Assisted: yes | no | partial
```

See `.gitmessage` for the template. Do not rewrite historic commits
retroactively.
