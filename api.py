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


def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> bool:
    """Verify API key if authentication is configured.

    If SPAM_API_KEY env var is set, all endpoints (except /docs, /openapi.json)
    require a valid Bearer token matching the configured key.
    If SPAM_API_KEY is empty, authentication is disabled (open access).
    """
    if not API_KEY:
        # Auth is disabled — allow all requests
        return True

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Missing API key",
                "message": "Authentication required. Provide API key via Authorization: Bearer <key> header.",
            },
        )

    if not secrets.compare_digest(credentials.credentials, API_KEY):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Invalid API key",
                "message": "The provided API key is invalid.",
            },
        )

    return True


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """Application lifespan: load models on startup, clean up on shutdown."""
    global pipeline, history_manager
    logger.info("Starting Spam Classifier API...")
    try:
        pipeline = PredictionPipeline(load_models=True)
        logger.info("✓ Models loaded successfully")
    except FileNotFoundError as e:
        logger.error(f"✗ Failed to load models: {e}")
        pipeline = None
        logger.warning("API will start but /predict endpoints will return 503")
    except (OSError, ValueError, ImportError) as e:
        logger.error(f"✗ Unexpected error during startup: {e}")
        pipeline = None

    # Initialize history manager
    try:
        history_manager = HistoryManager()
        logger.info("✓ History manager initialized")
    except (OSError, ValueError) as e:
        logger.error(f"✗ Failed to initialize history manager: {e}")
        history_manager = None

    # Log auth status
    if API_KEY:
        logger.info("✓ API key authentication enabled")
    else:
        logger.info("⚠ API key authentication DISABLED — set SPAM_API_KEY env var to enable")

    yield
    logger.info("Shutting down Spam Classifier API...")


# ── Prometheus metrics ────────────────────────────────────────────────────
if _PROM_AVAILABLE:
    SPAM_REQUEST_COUNT = Counter(
        "spam_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"],
    )
    SPAM_REQUEST_LATENCY = Histogram(
        "spam_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "endpoint"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    )
    SPAM_PREDICTIONS = Counter(
        "spam_predictions_total", "Email predictions made", ["result"])

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Spam Email Classifier API",
    description="A production-grade ML API for classifying emails as Spam or Ham, "
    "with SHAP-based explainability, URL analysis, classification history, "
    "and API key authentication.",
    version="2.0.0",
    lifespan=lifespan,
    dependencies=[Depends(verify_api_key)] if API_KEY else [],
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "General",
            "description": "API information and health check",
        },
        {
            "name": "Monitoring",
            "description": "Health check and uptime monitoring",
        },
        {
            "name": "Model",
            "description": "Model information and metadata",
        },
        {
            "name": "Prediction",
            "description": "Email classification (single, batch, explain, file upload)",
        },
    ],
)

# --- OpenTelemetry distributed tracing (OTEL_ENABLED=true) ---
try:
    from src.tracing import setup_tracing
    _otel_ok = setup_tracing("smartspam-api")
    if _otel_ok:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)
except ImportError:
    pass

# CORS — configurable via env var; defaults to localhost for dev
# Set CORS_ORIGINS env var for production (comma-separated)
CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000,http://localhost:8501,http://127.0.0.1:8501",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Security Headers ────────────────────────────────────────────────────


@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> None:
    """Add security headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), interest-cohort=()"
    )
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none';"

    if _PROM_AVAILABLE:
        import time as _time

        path = request.url.path
        SPAM_REQUEST_COUNT.labels(
            method=request.method, endpoint=path, status=response.status_code
        ).inc()
        if hasattr(request.state, "start_time"):
            SPAM_REQUEST_LATENCY.labels(method=request.method, endpoint=path).observe(
                _time.time() - request.state.start_time
            )

    return response


@app.middleware("http")
async def track_request_metrics(request: Request, call_next):
    import time as _time
    request.state.start_time = _time.time()
    return await call_next(request)


# Rate limiting — slowapi
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Log rate limit configuration
logger.info(
    "Rate limiting enabled: POST /predict → 30/min, "
    "/predict/explain → 10/min, /predict/batch → 10/min, "
    "/predict/file → 10/min, GET /model/info → 60/min"
)

from api_pkg.models import (  # noqa: E402
    BatchPredictRequest,
    BatchPredictResponse,
    BatchResult,
    Explanation,
    HealthResponse,
    ModelInfo,
    PredictRequest,
    PredictResponse,
    WordContribution,
)

# ---------------------------------------------------------------------------
# Startup timestamp for uptime tracking
# ---------------------------------------------------------------------------# ---------------------------------------------------------------------------
# Startup timestamp for uptime tracking
# ---------------------------------------------------------------------------
_start_time: float = time.time()


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _ensure_pipeline() -> None:
    """Ensure the prediction pipeline is loaded. Raises 503 if not available."""
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Model not loaded",
                "message": "The prediction model could not be loaded. "
                "Ensure trained models exist in the outputs/ directory "
                "or run the training pipeline.",
            },
        )


def _get_model_info() -> dict[str, Any] | None:
    """Extract model metadata from the pipeline if available."""
    if pipeline is None or pipeline.model is None:
        return None
    info = {
        "model_type": type(pipeline.model).__name__,
        "vectorizer_type": type(pipeline.feature_transformer).__name__
        if pipeline.feature_transformer
        else None,
        "vocabulary_size": len(pipeline.feature_transformer.vocabulary_)
        if pipeline.feature_transformer
        else None,
    }
    return info


# ---------------------------------------------------------------------------
# API v1 Router
# ---------------------------------------------------------------------------
v1_router = APIRouter(prefix="/api/v1")


@v1_router.get("/model/info", response_model=ModelInfo, tags=["Model"])
@limiter.limit("60/minute")
async def model_info(request: Request) -> None:
    """Get information about the loaded model."""
    _ensure_pipeline()
    model_meta = _get_model_info()

    has_shap = False
    if pipeline is not None and pipeline._shap_explainer is not None:
        has_shap = True

    return ModelInfo(
        status="loaded" if pipeline is not None else "not_loaded",
        model_name=os.path.basename(pipeline.config.model_path)
        if pipeline and pipeline.config.model_path
        else None,
        vectorizer_name=os.path.basename(pipeline.config.feature_path)
        if pipeline and pipeline.config.feature_path
        else None,
        model_type=model_meta.get("model_type") if model_meta else None,
        vectorizer_type=model_meta.get("vectorizer_type") if model_meta else None,
        vocabulary_size=model_meta.get("vocabulary_size") if model_meta else None,
        supports_explanations=has_shap,
        api_version="1.0.0",
    )


@v1_router.post("/predict", response_model=PredictResponse, tags=["Prediction"])
@limiter.limit("30/minute")
async def predict(request: Request, body: PredictRequest) -> None:
    """Classify a single email as Spam or Ham.

    Returns the prediction label, confidence score, and processing time.
    For word-level explanations, use `/predict/explain`.
    """
    _ensure_pipeline()

    start = time.time()
    try:
        result = pipeline.predict_single_email(body.email)
        if _PROM_AVAILABLE:
            SPAM_PREDICTIONS.labels(result=result["prediction"]).inc()
        elapsed = round((time.time() - start) * 1000, 2)  # ms

        return PredictResponse(
            prediction=result["prediction"],
            confidence=result.get("confidence"),
            raw_prediction=result["raw_prediction"],
            explanation=None,
            processing_time_ms=elapsed,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=422, detail={"error": "Validation error", "message": str(e)}
        )
    except (RuntimeError, KeyError, TypeError) as e:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500, detail={"error": "Prediction failed", "message": str(e)}
        )


@v1_router.post("/predict/explain", response_model=PredictResponse, tags=["Prediction"])
@limiter.limit("10/minute")
async def predict_with_explanation(request: Request, body: PredictRequest) -> None:
    """Classify a single email with SHAP-based word-level explanation.

    Returns the prediction along with word-level contributions, top spam/ham words,
    and color-highlighted HTML of the email text.
    This endpoint takes 3-5 seconds longer than /predict due to SHAP computation.
    """
    _ensure_pipeline()

    start = time.time()
    try:
        result = pipeline.predict_with_explanation(body.email, explanation_enabled=True)
        elapsed = round((time.time() - start) * 1000, 2)  # ms

        explanation_data = result.get("explanation", {})
        explanation = None
        if explanation_data:
            word_contribs = explanation_data.get("word_contributions", [])
            top_spam = explanation_data.get("top_spam_words", [])
            top_ham = explanation_data.get("top_ham_words", [])

            explanation = Explanation(
                status=explanation_data.get("status", "unavailable"),
                word_contributions=[
                    WordContribution(
                        word=w["word"],
                        contribution=w["contribution"],
                        class_=w["class"],
                    )
                    for w in word_contribs
                ],
                top_spam_words=[
                    WordContribution(
                        word=w["word"],
                        contribution=w["contribution"],
                        class_=w["class"],
                    )
                    for w in top_spam
                ],
                top_ham_words=[
                    WordContribution(
                        word=w["word"],
                        contribution=w["contribution"],
                        class_=w["class"],
                    )
                    for w in top_ham
                ],
                highlighted_html=explanation_data.get("highlighted_html", ""),
                error_message=explanation_data.get("error_message", ""),
            )

        return PredictResponse(
            prediction=result["prediction"],
            confidence=result.get("confidence"),
            raw_prediction=result["raw_prediction"],
            explanation=explanation,
            processing_time_ms=elapsed,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=422, detail={"error": "Validation error", "message": str(e)}
        )
    except (RuntimeError, KeyError, TypeError) as e:
        logger.exception("Prediction with explanation failed")
        raise HTTPException(
            status_code=500, detail={"error": "Prediction failed", "message": str(e)}
        )


@v1_router.post("/predict/batch", response_model=BatchPredictResponse, tags=["Prediction"])
@limiter.limit("10/minute")
async def predict_batch(request: Request, body: BatchPredictRequest) -> None:
    """Classify multiple emails in batch.

    Processes up to 1000 emails at once. If `include_explanations` is True,
    SHAP explanations are computed for each email (much slower).
    """
    _ensure_pipeline()

    start = time.time()
    try:
        results = []
        spam_count = 0
        ham_count = 0

        for i, email_text in enumerate(body.emails):
            if not email_text or not email_text.strip():
                results.append(
                    BatchResult(
                        index=i,
                        prediction="Unknown",
                        confidence=None,
                        explanation=None,
                    )
                )
                continue

            if body.include_explanations:
                result = pipeline.predict_with_explanation(email_text, explanation_enabled=True)
                explanation_data = result.get("explanation", {})
                explanation = None
                if explanation_data:
                    explanation = Explanation(
                        status=explanation_data.get("status", "unavailable"),
                        word_contributions=[
                            WordContribution(
                                word=w["word"],
                                contribution=w["contribution"],
                                class_=w["class"],
                            )
                            for w in explanation_data.get("word_contributions", [])
                        ],
                        top_spam_words=[
                            WordContribution(
                                word=w["word"],
                                contribution=w["contribution"],
                                class_=w["class"],
                            )
                            for w in explanation_data.get("top_spam_words", [])
                        ],
                        top_ham_words=[
                            WordContribution(
                                word=w["word"],
                                contribution=w["contribution"],
                                class_=w["class"],
                            )
                            for w in explanation_data.get("top_ham_words", [])
                        ],
                        highlighted_html=explanation_data.get("highlighted_html", ""),
                        error_message=explanation_data.get("error_message", ""),
                    )
            else:
                result = pipeline.predict_single_email(email_text)
                explanation = None

            pred = result["prediction"]
            if pred == "Spam":
                spam_count += 1
            elif pred == "Ham":
                ham_count += 1

            results.append(
                BatchResult(
                    index=i,
                    prediction=pred,
                    confidence=result.get("confidence"),
                    explanation=explanation,
                )
            )

        elapsed = round((time.time() - start) * 1000, 2)

        return BatchPredictResponse(
            total=len(body.emails),
            spam_count=spam_count,
            ham_count=ham_count,
            results=results,
            processing_time_ms=elapsed,
        )
    except (RuntimeError, ValueError, KeyError, TypeError) as e:
        logger.exception("Batch prediction failed")
        raise HTTPException(
            status_code=500,
            detail={"error": "Batch prediction failed", "message": str(e)},
        )


@v1_router.post("/predict/file", tags=["Prediction"])
@limiter.limit("10/minute")
async def predict_file(
    request: Request,
    file: UploadFile = File(..., description="Text or MBOX file to classify"),
    include_explanations: bool = Form(False, description="Whether to compute SHAP explanations"),
) -> dict[str, object]:
    """Upload a text or MBOX file for classification.

    For MBOX files, all emails are extracted and classified.
    For plain text files, the content is classified as a single email.
    """
    _ensure_pipeline()

    start = time.time()
    try:
        content = await file.read()

        # Enforce a 100 MB file size limit
        MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail={
                    "error": "File too large",
                    "message": "File size exceeds the 100 MB limit.",
                },
            )

        # Check if it's an MBOX file based on extension
        if file.filename and file.filename.lower().endswith((".mbox", ".mbx")):
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mbox") as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            try:
                df = pipeline.predict_mbox_file(tmp_path)
                results = []
                spam_count = 0
                ham_count = 0
                for _, row in df.iterrows():
                    pred = row.get("Prediction", "Unknown")
                    if pred == "Spam":
                        spam_count += 1
                    elif pred == "Ham":
                        ham_count += 1
                    results.append(
                        {
                            "subject": row.get("Subject", ""),
                            "time": row.get("Time", ""),
                            "prediction": pred,
                        }
                    )

                elapsed = round((time.time() - start) * 1000, 2)
                return {
                    "type": "mbox",
                    "total": len(results),
                    "spam_count": spam_count,
                    "ham_count": ham_count,
                    "results": results,
                    "processing_time_ms": elapsed,
                }
            finally:
                import os

                with suppress(PermissionError, OSError):
                    os.unlink(tmp_path)
        else:
            # Plain text file
            email_text = content.decode("utf-8", errors="ignore")

            if include_explanations:
                result = pipeline.predict_with_explanation(email_text, explanation_enabled=True)
            else:
                result = pipeline.predict_single_email(email_text)

            elapsed = round((time.time() - start) * 1000, 2)
            return {
                "type": "text",
                "filename": file.filename,
                "size_bytes": len(content),
                "prediction": result["prediction"],
                "confidence": result.get("confidence"),
                "processing_time_ms": elapsed,
            }

    except (RuntimeError, ValueError, KeyError, TypeError) as e:
        logger.exception("File prediction failed")
        raise HTTPException(
            status_code=500,
            detail={"error": "File prediction failed", "message": str(e)},
        )


app.include_router(v1_router)


# ---------------------------------------------------------------------------
# Unversioned endpoints (health, metrics, root)
# ---------------------------------------------------------------------------


@app.get("/", tags=["General"])
async def root() -> None:
    """Root endpoint with API overview."""
    endpoints = {
        "GET /health": "Health check",
        "GET /model/info": "Model information",
        "POST /predict": "Single email prediction",
        "POST /predict/explain": "Single email prediction with SHAP explanation",
        "POST /predict/batch": "Batch email prediction",
    }
    if _PROM_AVAILABLE:
        endpoints["GET /metrics"] = "Prometheus metrics"
    return {
        "name": "Spam Email Classifier API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": endpoints,
    }


@app.get("/metrics", tags=["Monitoring"])
async def metrics() -> dict[str, object]:
    """Prometheus metrics endpoint."""
    if not _PROM_AVAILABLE:
        return {"status": "prometheus_client not installed"}
    return Response(content=generate_latest(), media_type="text/plain")


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health() -> None:
    """Health check endpoint for monitoring and orchestration."""
    _ensure_pipeline()
    return HealthResponse(
        status="healthy",
        model_loaded=pipeline is not None,
        api_version="1.0.0",
        uptime_seconds=round(time.time() - _start_time, 2),
    )


# (old unversioned endpoints removed — now under /api/v1 via v1_router)
