"""Tests for the FastAPI REST API (api.py).

Uses FastAPI's TestClient for fast, server-free endpoint testing.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from api import app


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_pipeline():
    """Reset the global pipeline before each test."""
    import api as api_module
    api_module.pipeline = None
    yield


class TestRoot:
    """Test the root endpoint."""

    def test_root_returns_endpoints(self, client):
        """GET / should return API metadata with endpoint list."""
        with patch('api.pipeline', MagicMock()):
            resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Spam Email Classifier API"
        assert "endpoints" in data
        assert "POST /predict" in data["endpoints"]
        assert "GET /health" in data["endpoints"]


class TestHealth:
    """Test the health check endpoint."""

    def test_health_healthy(self, client):
        """GET /health should return healthy status when model is loaded."""
        with patch('api.pipeline', MagicMock()):
            with patch('api._ensure_pipeline', return_value=None):
                resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["api_version"] == "1.0.0"
        assert data["uptime_seconds"] is not None

    def test_health_no_model(self, client):
        """GET /health should return 503 when model is not loaded."""
        resp = client.get("/health")
        assert resp.status_code == 503


class TestModelInfo:
    """Test the model info endpoint."""

    def test_model_info_loaded(self, client):
        """GET /model/info should return model metadata when loaded."""
        mock_pipeline = MagicMock()
        mock_pipeline.model = MagicMock()
        mock_pipeline.model.__class__.__name__ = "SVC"
        mock_pipeline.feature_transformer = MagicMock()
        mock_pipeline.feature_transformer.vocabulary_ = {"a": 1, "b": 2}
        mock_pipeline.feature_transformer.__class__.__name__ = "TfidfVectorizer"
        mock_pipeline.config.model_path = "outputs/run/models/SVM_model.pkl"
        mock_pipeline.config.feature_path = "outputs/run/models/vectorizer.pkl"
        mock_pipeline._shap_explainer = None

        with patch('api.pipeline', mock_pipeline):
            with patch('api._ensure_pipeline', return_value=None):
                resp = client.get("/model/info")

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "loaded"
        assert data["model_type"] == "SVC"
        assert data["vectorizer_type"] == "TfidfVectorizer"
        assert data["vocabulary_size"] == 2
        assert data["supports_explanations"] is False

    def test_model_info_no_model(self, client):
        """GET /model/info should return 503 when no model is loaded."""
        resp = client.get("/model/info")
        assert resp.status_code == 503


class TestPredict:
    """Test the /predict endpoint."""

    def test_predict_spam(self, client):
        """POST /predict should classify a spam email correctly."""
        mock_pipeline = MagicMock()
        mock_pipeline.predict_single_email.return_value = {
            "prediction": "Spam",
            "confidence": 99.87,
            "raw_prediction": 0,
        }

        with patch('api.pipeline', mock_pipeline):
            resp = client.post("/predict", json={"email": "Congratulations! You won!"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["prediction"] == "Spam"
        assert data["confidence"] == 99.87
        assert data["raw_prediction"] == 0
        assert data["explanation"] is None
        assert data["processing_time_ms"] is not None

    def test_predict_ham(self, client):
        """POST /predict should classify a ham email correctly."""
        mock_pipeline = MagicMock()
        mock_pipeline.predict_single_email.return_value = {
            "prediction": "Ham",
            "confidence": 95.5,
            "raw_prediction": 1,
        }

        with patch('api.pipeline', mock_pipeline):
            resp = client.post("/predict", json={"email": "Meeting tomorrow at 3pm"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["prediction"] == "Ham"
        assert data["confidence"] == 95.5

    def test_predict_empty_email(self, client):
        """POST /predict with empty email should return 422."""
        mock_pipeline = MagicMock()
        mock_pipeline.predict_single_email.side_effect = ValueError(
            "Email body is empty."
        )

        with patch('api.pipeline', mock_pipeline):
            with patch('api._ensure_pipeline', return_value=None):
                resp = client.post("/predict", json={"email": ""})

        assert resp.status_code == 422

    def test_predict_no_model(self, client):
        """POST /predict should return 503 when no model is loaded."""
        resp = client.post("/predict", json={"email": "test email"})
        assert resp.status_code == 503

    def test_predict_server_error(self, client):
        """POST /predict should return 500 on unexpected errors."""
        mock_pipeline = MagicMock()
        mock_pipeline.predict_single_email.side_effect = RuntimeError("Unexpected error")

        with patch('api.pipeline', mock_pipeline):
            resp = client.post("/predict", json={"email": "test email"})

        assert resp.status_code == 500


class TestPredictWithExplanation:
    """Test the /predict/explain endpoint."""

    def test_predict_with_explanation(self, client):
        """POST /predict/explain should return prediction + SHAP explanation."""
        mock_pipeline = MagicMock()
        mock_pipeline.predict_with_explanation.return_value = {
            "prediction": "Spam",
            "confidence": 99.0,
            "raw_prediction": 0,
            "explanation": {
                "status": "available",
                "word_contributions": [
                    {"word": "free", "contribution": 0.85, "class": "spam"},
                    {"word": "win", "contribution": 0.72, "class": "spam"},
                ],
                "top_spam_words": [
                    {"word": "free", "contribution": 0.85, "class": "spam"},
                ],
                "top_ham_words": [
                    {"word": "meeting", "contribution": -0.45, "class": "ham"},
                ],
                "highlighted_html": "<span>free</span> <span>win</span>",
                "error_message": "",
            },
        }

        with patch('api.pipeline', mock_pipeline):
            resp = client.post("/predict/explain", json={"email": "Free money!"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["prediction"] == "Spam"
        assert data["explanation"] is not None
        assert data["explanation"]["status"] == "available"
        assert len(data["explanation"]["word_contributions"]) == 2
        assert len(data["explanation"]["top_spam_words"]) == 1
        assert len(data["explanation"]["top_ham_words"]) == 1
        assert data["explanation"]["highlighted_html"] != ""

    def test_predict_explanation_no_model(self, client):
        """POST /predict/explain should return 503 when no model is loaded."""
        resp = client.post("/predict/explain", json={"email": "test email"})
        assert resp.status_code == 503


class TestPredictBatch:
    """Test the /predict/batch endpoint."""

    def test_batch_basic(self, client):
        """POST /predict/batch should classify multiple emails."""
        mock_pipeline = MagicMock()

        def mock_single(email):
            is_spam = "win" in email.lower() or "free" in email.lower()
            return {
                "prediction": "Spam" if is_spam else "Ham",
                "confidence": 98.0 if is_spam else 95.0,
                "raw_prediction": 0 if is_spam else 1,
            }

        mock_pipeline.predict_single_email.side_effect = mock_single

        with patch('api.pipeline', mock_pipeline):
            resp = client.post("/predict/batch", json={
                "emails": [
                    "Win a free iPhone!",
                    "Meeting at 3pm tomorrow",
                ],
                "include_explanations": False,
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert data["spam_count"] == 1
        assert data["ham_count"] == 1
        assert len(data["results"]) == 2
        assert data["results"][0]["prediction"] == "Spam"
        assert data["results"][1]["prediction"] == "Ham"

    def test_batch_with_explanations(self, client):
        """POST /predict/batch with explanations should include SHAP data."""
        mock_pipeline = MagicMock()
        mock_pipeline.predict_with_explanation.return_value = {
            "prediction": "Spam",
            "confidence": 99.0,
            "raw_prediction": 0,
            "explanation": {
                "status": "available",
                "word_contributions": [{"word": "free", "contribution": 0.85, "class": "spam"}],
                "top_spam_words": [{"word": "free", "contribution": 0.85, "class": "spam"}],
                "top_ham_words": [],
                "highlighted_html": "<span>free</span>",
                "error_message": "",
            },
        }

        with patch('api.pipeline', mock_pipeline):
            resp = client.post("/predict/batch", json={
                "emails": ["Free money!"],
                "include_explanations": True,
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["results"][0]["explanation"] is not None
        assert data["results"][0]["explanation"]["status"] == "available"

    def test_batch_empty_email(self, client):
        """Empty strings in batch should be handled gracefully."""
        mock_pipeline = MagicMock()

        def mock_single(email):
            return {
                "prediction": "Ham",
                "confidence": 90.0,
                "raw_prediction": 1,
            }

        mock_pipeline.predict_single_email.side_effect = mock_single
        mock_pipeline.predict_with_explanation.return_value = {
            "prediction": "Spam",
            "confidence": 99.0,
            "raw_prediction": 0,
            "explanation": None,
        }

        with patch('api.pipeline', mock_pipeline):
            resp = client.post("/predict/batch", json={
                "emails": ["", "Valid email", "  "],
                "include_explanations": False,
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        # Empty strings should be "Unknown"
        assert data["results"][0]["prediction"] == "Unknown"
        assert data["results"][1]["prediction"] == "Ham"
        assert data["results"][2]["prediction"] == "Unknown"

    def test_batch_no_model(self, client):
        """POST /predict/batch should return 503 when no model is loaded."""
        resp = client.post("/predict/batch", json={
            "emails": ["test"],
            "include_explanations": False,
        })
        assert resp.status_code == 503


class TestPredictFile:
    """Test the /predict/file endpoint."""

    def test_predict_text_file(self, client):
        """POST /predict/file with text file should classify content."""
        mock_pipeline = MagicMock()
        mock_pipeline.predict_single_email.return_value = {
            "prediction": "Spam",
            "confidence": 99.5,
            "raw_prediction": 0,
        }

        with patch('api.pipeline', mock_pipeline):
            resp = client.post(
                "/predict/file",
                files={"file": ("email.txt", "Win a free prize!")},
                data={"include_explanations": "false"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "text"
        assert data["prediction"] == "Spam"
        assert data["filename"] == "email.txt"
        assert data["size_bytes"] > 0

    def test_predict_file_no_model(self, client):
        """POST /predict/file should return 503 when no model is loaded."""
        resp = client.post(
            "/predict/file",
            files={"file": ("test.txt", b"test content")},
        )
        assert resp.status_code == 503


class TestCORS:
    """Test CORS middleware configuration."""

    def test_cors_headers(self, client):
        """API should include CORS headers in responses."""
        resp = client.options(
            "/",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200
        # When allow_credentials=True, CORS middleware echoes back the request origin
        origin = resp.headers.get("access-control-allow-origin")
        assert origin is not None and origin != ""
        assert "GET" in resp.headers.get("access-control-allow-methods", "")
