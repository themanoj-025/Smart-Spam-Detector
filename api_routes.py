"""API routes -- prediction, health, and info endpoints."""

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
