"""Spam Email Classifier API -- Pydantic models for request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PredictRequest(BaseModel):
    """Request model for single email prediction."""

    email: str = Field(
        ...,
        min_length=1,
        max_length=100_000,
        description="The email text to classify. Supports plain text and HTML content.",
        examples=["Congratulations! You won a free prize! Click here to claim now."],
    )


class WordContribution(BaseModel):
    """Word-level SHAP contribution to the prediction."""

    model_config = ConfigDict(populate_by_name=True)
    word: str = Field(..., description="The word that influenced the prediction")
    contribution: float = Field(
        ...,
        description="SHAP value (positive = pushes toward spam, negative = pushes toward ham)",
    )
    class_: str = Field(
        ...,
        alias="class",
        description="'spam' or 'ham' -- which class this word pushes toward",
    )


class Explanation(BaseModel):
    """SHAP-based explanation data."""

    status: str = Field(..., description="'available', 'unavailable', or 'error'")
    word_contributions: list[WordContribution] = Field(
        default_factory=list,
        description="All word-level contributions sorted by absolute value",
    )
    top_spam_words: list[WordContribution] = Field(
        default_factory=list, description="Top 10 words pushing toward spam"
    )
    top_ham_words: list[WordContribution] = Field(
        default_factory=list, description="Top 10 words pushing toward ham"
    )
    highlighted_html: str = Field(
        default="", description="HTML with words color-coded by contribution"
    )
    error_message: str = Field(default="", description="Error message if status is 'error'")


class PredictResponse(BaseModel):
    """Response model for single email prediction."""

    prediction: str = Field(..., description="'Spam' or 'Ham'")
    confidence: float | None = Field(None, description="Confidence percentage (0-100)")
    raw_prediction: int = Field(..., description="Integer prediction (0 = Spam, 1 = Ham)")
    explanation: Explanation | None = Field(
        None, description="SHAP-based explanation (only with /predict/explain)"
    )
    processing_time_ms: float | None = Field(
        None, description="Time taken for prediction in milliseconds"
    )


class BatchPredictRequest(BaseModel):
    """Request model for batch prediction."""

    emails: list[str] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of email texts to classify (1-1000 emails)",
        examples=[
            [
                "Win a free iPhone now!",
                "Meeting at 3pm tomorrow",
                "Click here to claim your prize",
            ]
        ],
    )
    include_explanations: bool = Field(
        False,
        description="Whether to compute SHAP explanations for each email (significantly slower)",
    )


class BatchResult(BaseModel):
    """Single result in a batch prediction response."""

    index: int = Field(..., description="Index in the original request array")
    prediction: str = Field(..., description="'Spam' or 'Ham'")
    confidence: float | None = Field(None, description="Confidence percentage")
    explanation: Explanation | None = Field(None, description="SHAP explanation (if requested)")


class BatchPredictResponse(BaseModel):
    """Response model for batch prediction."""

    total: int = Field(..., description="Total number of emails processed")
    spam_count: int = Field(..., description="Number of emails classified as Spam")
    ham_count: int = Field(..., description="Number of emails classified as Ham")
    results: list[BatchResult] = Field(..., description="Individual prediction results")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")


class ModelInfo(BaseModel):
    """Model information response."""

    status: str = Field(..., description="'loaded' or 'not_loaded'")
    model_name: str | None = Field(None, description="Filename of the loaded model")
    vectorizer_name: str | None = Field(None, description="Filename of the loaded vectorizer")
    model_type: str | None = Field(None, description="Type of the model (e.g., 'SVC')")
    vectorizer_type: str | None = Field(
        None, description="Type of the vectorizer (e.g., 'TfidfVectorizer')"
    )
    vocabulary_size: int | None = Field(None, description="Number of features in the vocabulary")
    supports_explanations: bool = Field(
        False, description="Whether SHAP explanations are available"
    )
    api_version: str = Field("1.0.0", description="API version")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="'healthy' or 'unhealthy'")
    model_loaded: bool = Field(..., description="Whether the model is loaded")
    api_version: str = Field(..., description="API version")
    uptime_seconds: float | None = Field(None, description="Server uptime in seconds")
