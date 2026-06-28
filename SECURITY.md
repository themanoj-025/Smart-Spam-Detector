# Security Policy for Smart-Spam-Detector

## Reporting a Vulnerability

If you discover a security vulnerability in Smart-Spam-Detector, please report it privately.

**How to report:**
- Open a private security advisory on GitHub (if this repository is public).
- Email **manojjana.0025@gmail.com** directly. This contact is also listed in our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- If neither channel works, open a standard issue with the label `security` without including exploit details.

**Expectations:**
- We will acknowledge receipt within 5 business days.
- We will provide an assessment and expected fix timeline within 10 business days.
- Please refrain from public disclosure until a fix is released.

## Security Measures

### Implemented
- **Bearer token authentication:** The FastAPI API requires a valid API key sent as `Authorization: Bearer <key>`. Configured via `SPAM_API_KEY` environment variable.
- **Rate limiting:** Per-key rate limiting is implemented via slowapi to prevent API abuse.
- **Input sanitization:** Email text is cleaned and sanitized before processing (encoding handling, text extraction).
- **File validation:** Uploaded files are validated for content type and size.

### Not Implemented
- **No HTTPS enforcement:** TLS is not configured at the application level. Deploy behind a reverse proxy.
- **No encryption at rest:** The SQLite history database is unencrypted.
- **No data anonymization:** Email text submitted for classification is stored in the prediction history.
- **No multi-user support:** API key auth is simple — there is no per-user isolation or role management.
- **No CORS restriction:** CORS should be configured based on deployment needs.

## Authentication

### API Key Management
- The API key is set via the `SPAM_API_KEY` environment variable.
- If `SPAM_API_KEY` is not set, the API may start without authentication. **Always set this variable in production.**
- Rotate the API key if it is accidentally exposed.
- There is no built-in key rotation mechanism — update the env var and restart the server.

### Endpoint Protection
All API endpoints (`/predict`, `/predict/batch`, `/upload`, `/model/info`) require authentication when `SPAM_API_KEY` is configured. The Streamlit app and CLI tool do not require authentication.

## Data Privacy

- **Prediction history:** Email text submitted for classification is stored in a local SQLite database (`history.db`). This data is not encrypted.
- **MBOX processing:** When processing MBOX files, email bodies are extracted and stored in prediction history.
- **Data retention:** There is no automatic data retention or deletion policy. Manually clear the history database as needed.
- **No external data transmission:** All processing is local — no data is sent to external services.

## Model Security

- Trained models and vectorizers (`.pkl` / `.joblib` files) can potentially execute arbitrary code when deserialized with pickle/joblib.
- **Only load models from trusted sources.**
- Models are stored in the `outputs/` directory with timestamped run directories.
- The `Config` class auto-discovers the latest model from `outputs/`. Ensure this directory has restricted permissions.

## Environment Variables

| Variable | Sensitivity | Purpose |
|---|---|---|
| `SPAM_API_KEY` | **Critical** | API authentication key. Generate a strong random value. |
| `LOG_LEVEL` | Low | Logging verbosity. Not sensitive. |

## Deployment Security

- **Docker:** If using Docker, run the container as a non-root user. Do not expose port 8000 publicly without authentication.
- **Streamlit Cloud:** The Streamlit app has no authentication by default. Use Streamlit's secrets and authentication features if needed.
- **Reverse proxy:** Deploy behind nginx or Caddy for TLS termination and additional security headers.
- **Firewall:** Restrict API port access to trusted networks.

## Dependency Security

Regularly audit dependencies:

```bash
pip-audit -r requirements.txt
pip-audit -r requirements-dev.txt
```

Key packages to monitor:
- `scikit-learn` — ML library (CVEs are rare but impactful).
- `fastapi` / `uvicorn` — Web server (keep updated).
- `shap` — Model explanation library.
- `xboost` — Gradient boosting library.
- `nltk` — NLP toolkit.
