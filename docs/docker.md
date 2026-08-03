# Smart-Spam-Detector — Docker Guide

## Quick start

```bash
cp .env.example .env   # optionally set SPAM_API_KEY
docker compose up -d
```

Two services start on an isolated bridge network:

| Service | Image target | Purpose | Port |
|---------|--------------|---------|------|
| `api`      | `Dockerfile` → `api` | FastAPI REST API | `8000` |
| `streamlit`| `Dockerfile` → `streamlit` | Streamlit dashboard | `8501` |

Trained models ship inside the image (`outputs/<run>/models/*.pkl`).
Classification history persists in a named `history` volume (SQLite).

## Environment

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `SPAM_API_KEY` | Bearer auth for API endpoints | no | — (auth disabled) |
| `LOG_LEVEL` | Log verbosity | — | `INFO` |
| `CORS_ORIGINS` | Allowed CORS origins (api) | — | localhost set |

## Authentication

Set `SPAM_API_KEY` to protect `/predict*` endpoints. All requests must
then send `Authorization: Bearer <key>`. Leave empty to keep open access.

## Development

```bash
make up   # dev override: source bind mounts + hot reload (both services)
```

## Production

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Restart `always`, 1G memory limits, no dev mounts.

## Volumes

| Volume | Contents | Backup? |
|--------|----------|---------|
| `history` | SQLite classification history | Recommended if you use it |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| API returns 503 "Model not loaded" | `outputs/` artifacts missing — the image needs a trained run; run the training pipeline (`docker compose exec api python -m src.pipeline.training_pipeline`) |
| 401/403 on /predict | Set `SPAM_API_KEY` in `.env` consistently |
| Port conflicts | Change `ports` in `docker-compose.yml` |
| History reset | Use `docker compose down` (not `-v`) to preserve the volume |
