"""
Spam Email Classifier — FastAPI REST API

Provides a production-grade REST API for the spam email classification system,
with endpoints for single prediction, SHAP-based explainability, batch processing,
URL analysis, history, and health monitoring.

Usage:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

import hashlib
import os
import secrets
import time
from contextlib import asynccontextmanager, suppress
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# ---------------------------------------------------------------------------
# Rate limiting — slowapi
# ---------------------------------------------------------------------------
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.pipeline.prediction_pipeline import PredictionPipeline
from src.utils.history_manager import HistoryManager

try:
    from prometheus_client import Counter, Histogram, generate_latest

    _PROM_AVAILABLE = True
except ImportError:
    _PROM_AVAILABLE = False


def _rate_limit_key(request: Request) -> str:
    """Determine the rate limit key for a request.

    If an API key (Bearer token) is present in the Authorization header,
    use a stable hash of it as the key so each API key gets its own quota.
    Otherwise fall back to the client's remote IP address.
    """
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth[len("bearer ") :].strip()
        if token:
            hashed = hashlib.sha256(token.encode()).hexdigest()[:16]
            return f"apikey_{hashed}"
    return get_remote_address(request)


limiter = Limiter(
    key_func=_rate_limit_key,
    default_limits=[],  # no blanket default — each route sets its own
)

from api_pkg.logging_config import setup_logging

logger = setup_logging()

# ---------------------------------------------------------------------------
# Global pipeline (lazy-loaded at startup) + history manager
# ---------------------------------------------------------------------------
pipeline: PredictionPipeline | None = None
history_manager: HistoryManager | None = None

# API Key Authentication
# Set SPAM_API_KEY env var to enable auth. Leave unset to disable.
API_KEY = os.environ.get("SPAM_API_KEY", "")
security = HTTPBearer(auto_error=False)

from api_middleware import *  # noqa: F401
