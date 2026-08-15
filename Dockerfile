# syntax=docker/dockerfile:1
# ═══════════════════════════════════════════════════════════════════════
# Smart-Spam-Detector — Spam Email Classifier (FastAPI + Streamlit)
#
# Build targets:
#   api        — FastAPI REST API (:8000)
#   streamlit  — Streamlit dashboard (:8501)
#   dev        — development image with both entry points + test tooling
#
# Usage:
#   docker build --target api -t spam-api .
#   docker build --target streamlit -t spam-ui .
#   docker compose up -d          # api + streamlit
# ═══════════════════════════════════════════════════════════════════════

# ── Base stage ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

LABEL org.opencontainers.image.title="Spam Email Classifier"
LABEL org.opencontainers.image.description="ML spam classifier — FastAPI + Streamlit with SHAP explainability"
LABEL org.opencontainers.image.version="2.0.0"
LABEL org.opencontainers.image.vendor="Smart-Spam-Detector"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        tini \
        curl \
    # Remove Debian's apt-managed python packages: python:3.11-slim ships
    # python3-msgpack 1.1.2 (GHSA-6v7p-g79w-8964, HIGH) and python3-setuptools
    # 70.3.0 (CVE-2025-47273) in /usr/lib/python3/dist-packages. The pip
    # install in the deps stage provides patched versions (msgpack 1.2.1,
    # setuptools 78.1.1+) in /usr/local, but Trivy scans every copy — so the
    # unpatched apt copies must be purged or the image scan fails.
    && apt-get purge -y --auto-remove python3-msgpack python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Deps stage ─────────────────────────────────────────────────────────
FROM base AS deps

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    # Upgrade build-time/transitive packages with known HIGH CVEs
    # (setuptools CVE-2025-47273, wheel CVE-2026-24049, msgpack GHSA-6v7p-g79w-8964,
    #  jaraco.context CVE-2026-23949) — flagged by the CI trivy gate.
    pip install --no-cache-dir --upgrade \
        "setuptools>=78.1.1" \
        "wheel>=0.46.2" \
        "msgpack>=1.2.1" \
        "jaraco-context>=6.1.0"

# ── Shared app files stage ─────────────────────────────────────────────
FROM deps AS appfiles

RUN useradd --create-home --uid 10001 appuser && \
    mkdir -p /app/history && \
    chown -R appuser:appuser /app

# Application code + trained artifacts (outputs/<run>/*.pkl)
COPY api.py app.py classify.py ./
COPY src/ ./src/
COPY outputs/ ./outputs/
COPY .streamlit/ ./.streamlit/
COPY .env.example ./

USER appuser

# ── API stage ──────────────────────────────────────────────────────────
FROM appfiles AS api

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Streamlit stage ────────────────────────────────────────────────────
FROM appfiles AS streamlit

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fsS http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]

# ── Dev stage: hot reload + test tooling ───────────────────────────────
FROM appfiles AS dev

# pip install must run as root — the appfiles stage already set USER
# appuser, so temporarily switch back to root for the install.
USER root
RUN pip install --no-cache-dir pytest
USER appuser

# Test suite + scratch dirs for in-container test runs (make test)
COPY --chown=appuser:appuser tests/ ./tests/
COPY --chown=appuser:appuser data/ ./data/

# Dev default: Streamlit with polling file watcher (hot reload)
EXPOSE 8000 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false", \
     "--server.fileWatcherType=polling", \
     "--server.runOnSave=true"]
