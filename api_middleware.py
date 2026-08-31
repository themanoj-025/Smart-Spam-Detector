"""API middleware -- authentication, rate limiting, and CORS helpers."""




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
async def track_request_metrics(request: Request, call_next) -> None:
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
