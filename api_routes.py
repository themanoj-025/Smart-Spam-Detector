"""API routes — prediction, health, and info endpoints."""

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
) -> dict[str, object] -> None:
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
