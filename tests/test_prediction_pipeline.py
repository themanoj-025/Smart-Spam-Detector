"""Unit tests for PredictionPipeline.predict_with_explanation.

Covers all code paths:
- Empty / whitespace-only input → ValueError
- explanation_enabled=False → status 'unavailable'
- SHAP explainer not initialized → status 'unavailable' with message
- SHAP explainer fully working → status 'available' with full explanation
- ImportError during SHAP → status 'error' with install message
- General exception during SHAP → status 'error' with exception message
- Spam / Ham prediction labels
- Model with / without predict_proba → confidence value
- Lazy model loading when models are None
"""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from src.pipeline.prediction_pipeline import PredictionPipeline


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pipeline():
    """Return a PredictionPipeline with models NOT loaded so all
    _load_models / TF-IDF / model interactions can be mocked."""
    return PredictionPipeline(load_models=False)


@pytest.fixture
def mock_model_and_transformer(pipeline):
    """Set up mock model (with predict_proba) and mock transformer on the pipeline."""
    model = MagicMock()
    model.predict.return_value = np.array([0])      # spam
    model.predict_proba.return_value = np.array([[0.99, 0.01]])

    transformer = MagicMock()
    transformer.transform.return_value = MagicMock()  # sparse matrix stand-in

    pipeline.model = model
    pipeline.feature_transformer = transformer
    return model, transformer


# ---------------------------------------------------------------------------
# Helper to invoke the private helper that resets lazy-load guards
# ---------------------------------------------------------------------------

def _make_models_ready(pipeline, model=None, transformer=None):
    """Assign model & transformer so the method's lazy-load check is skipped."""
    pipeline.model = model or MagicMock()
    pipeline.feature_transformer = transformer or MagicMock()


# =============================  INPUT VALIDATION  ===========================

class TestInputValidation:
    """Empty / whitespace-only input must raise ValueError."""

    def test_empty_string_raises_value_error(self, pipeline):
        _make_models_ready(pipeline)
        with pytest.raises(ValueError, match="Email body is empty"):
            pipeline.predict_with_explanation("")

    def test_whitespace_only_raises_value_error(self, pipeline):
        _make_models_ready(pipeline)
        with pytest.raises(ValueError, match="Email body is empty"):
            pipeline.predict_with_explanation("   \t\n  ")

    def test_none_raises_value_error(self, pipeline):
        _make_models_ready(pipeline)
        with pytest.raises(ValueError, match="Email body is empty"):
            pipeline.predict_with_explanation(None)  # type: ignore[arg-type]


# =======================  EXPLANATION DISABLED  =============================

class TestExplanationDisabled:
    """When explanation_enabled=False the explanation dict has status 'unavailable'."""

    def test_returns_unavailable_status(self, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([0])
        _make_models_ready(pipeline, model=model)

        result = pipeline.predict_with_explanation("Hello", explanation_enabled=False)

        assert result["explanation"]["status"] == "unavailable"
        assert result["explanation"]["word_contributions"] == []
        assert result["explanation"]["top_spam_words"] == []
        assert result["explanation"]["top_ham_words"] == []
        assert result["explanation"]["highlighted_html"] == ""

    def test_prediction_is_still_produced(self, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([1])
        _make_models_ready(pipeline, model=model)

        result = pipeline.predict_with_explanation("Hello", explanation_enabled=False)

        assert result["prediction"] == "Ham"
        assert result["raw_prediction"] == 1


# ====================  EXPLAINER NOT INITIALIZED  ===========================

class TestExplainerNotInitialized:
    """When _init_explainer does NOT set _shap_explainer we get status
    'unavailable' with a descriptive error message."""

    @patch.object(PredictionPipeline, "_init_explainer")
    def test_shap_explainer_is_none(self, mock_init, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([0])
        _make_models_ready(pipeline, model=model)
        # After _init_explainer runs, _shap_explainer should still be None
        mock_init.return_value = None

        result = pipeline.predict_with_explanation("Hello", explanation_enabled=True)

        assert result["explanation"]["status"] == "unavailable"
        assert "could not be initialized" in result["explanation"]["error_message"]

    @patch.object(PredictionPipeline, "_init_explainer")
    def test_shap_explainer_stays_none_after_init(self, mock_init, pipeline):
        """When _shap_explainer remains None after _init_explainer returns
        (mocked to do nothing), status is 'unavailable' with a message."""
        model = MagicMock()
        model.predict.return_value = np.array([0])
        _make_models_ready(pipeline, model=model)
        mock_init.return_value = None

        result = pipeline.predict_with_explanation("Hello", explanation_enabled=True)

        assert result["explanation"]["status"] == "unavailable"
        assert "could not be initialized" in result["explanation"]["error_message"]


# ======================  EXPLANATION AVAILABLE  =============================

class TestExplanationAvailable:
    """When SHAP is fully initialised and returns values."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([0])
        model.predict_proba.return_value = np.array([[0.99, 0.01]])
        _make_models_ready(pipeline, model=model)

        # Mock a real-looking SHAP explainer
        pipeline._shap_explainer = MagicMock()
        pipeline._feature_names = np.array(["free", "win", "meeting", "hello"])

        return pipeline

    def test_successful_explanation_with_list_shap_values(self, pipeline):
        """SHAP values returned as a list (binary classification style)."""
        # shap_values returns a list: [spam_class_values, ham_class_values]
        pipeline._shap_explainer.shap_values.return_value = [
            np.array([[0.85, 0.72, -0.45, 0.0]]),  # spam class
            np.array([[-0.85, -0.72, 0.45, 0.0]]),  # ham class
        ]

        result = pipeline.predict_with_explanation("free win meeting hello",
                                                    explanation_enabled=True)

        assert result["explanation"]["status"] == "available"
        assert result["explanation"]["error_message"] == ""

        # word_contributions: should only contain non-zero contributions
        contributions = result["explanation"]["word_contributions"]
        assert len(contributions) == 3  # free, win, meeting (hello=0 is excluded)
        assert contributions[0]["word"] == "free"
        assert contributions[0]["class"] == "spam"
        assert contributions[2]["word"] == "meeting"
        assert contributions[2]["class"] == "ham"

        # top_spam_words / top_ham_words
        assert len(result["explanation"]["top_spam_words"]) == 2
        assert len(result["explanation"]["top_ham_words"]) == 1

        # highlighted_html should be a non-empty string
        assert isinstance(result["explanation"]["highlighted_html"], str)
        assert len(result["explanation"]["highlighted_html"]) > 0

    def test_successful_explanation_with_2d_array_shap_values(self, pipeline):
        """SHAP values returned as a 2D array (single-class style)."""
        pipeline._shap_explainer.shap_values.return_value = np.array([
            [0.85, 0.72, -0.45, 0.0]
        ])

        result = pipeline.predict_with_explanation("free win meeting hello",
                                                    explanation_enabled=True)

        assert result["explanation"]["status"] == "available"
        assert len(result["explanation"]["word_contributions"]) == 3

    def test_prediction_label_spam(self, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([0])
        model.predict_proba.return_value = np.array([[0.99, 0.01]])
        _make_models_ready(pipeline, model=model)
        pipeline._shap_explainer = MagicMock()
        pipeline._shap_explainer.shap_values.return_value = np.array([[0.5, -0.3]])
        pipeline._feature_names = np.array(["win", "hello"])

        result = pipeline.predict_with_explanation("win hello", explanation_enabled=True)
        assert result["prediction"] == "Spam"
        assert result["raw_prediction"] == 0

    def test_prediction_label_ham(self, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([1])
        model.predict_proba.return_value = np.array([[0.01, 0.99]])
        _make_models_ready(pipeline, model=model)
        pipeline._shap_explainer = MagicMock()
        pipeline._shap_explainer.shap_values.return_value = np.array([[-0.3, 0.5]])
        pipeline._feature_names = np.array(["win", "hello"])

        result = pipeline.predict_with_explanation("win hello", explanation_enabled=True)
        assert result["prediction"] == "Ham"
        assert result["raw_prediction"] == 1

    def test_confidence_is_rounded_percentage(self, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([1])
        model.predict_proba.return_value = np.array([[0.1234, 0.8766]])
        _make_models_ready(pipeline, model=model)
        pipeline._shap_explainer = MagicMock()
        pipeline._shap_explainer.shap_values.return_value = np.array([[-0.3, 0.5]])
        pipeline._feature_names = np.array(["win", "hello"])

        result = pipeline.predict_with_explanation("win hello", explanation_enabled=True)
        assert result["confidence"] == 87.66  # 0.8766 * 100 → rounded to 2 decimals


# ========================  MODEL CONFIDENCE EDGE CASES  ======================

class TestConfidenceEdgeCases:
    """Confidence should be None when the model lacks predict_proba."""

    def test_model_without_predict_proba_returns_none_confidence(self, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([0])
        # Remove predict_proba so hasattr check in method returns False
        del model.predict_proba
        _make_models_ready(pipeline, model=model)

        result = pipeline.predict_with_explanation("test", explanation_enabled=False)
        assert result["confidence"] is None

    def test_predict_proba_raises_exception_returns_none_confidence(self, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([0])
        model.predict_proba.side_effect = RuntimeError("proba failed")
        _make_models_ready(pipeline, model=model)

        result = pipeline.predict_with_explanation("test", explanation_enabled=False)
        assert result["confidence"] is None


# ========================  EXCEPTION HANDLING  ==============================

class TestExplanationExceptions:
    """ImportError and generic exceptions inside the SHAP block set status
    to 'error' with a descriptive message."""

    @patch.object(PredictionPipeline, "_init_explainer")
    def test_importerror_caught(self, mock_init, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([0])
        model.predict_proba.return_value = np.array([[0.99, 0.01]])
        _make_models_ready(pipeline, model=model)
        pipeline._shap_explainer = MagicMock()

        # Make shap_values raise ImportError (e.g. if shap is uninstalled)
        pipeline._shap_explainer.shap_values.side_effect = ImportError(
            "No module named 'shap'"
        )
        mock_init.return_value = None

        result = pipeline.predict_with_explanation("hello", explanation_enabled=True)

        assert result["explanation"]["status"] == "error"
        assert "SHAP library is not installed" in result["explanation"]["error_message"]

    @patch.object(PredictionPipeline, "_init_explainer")
    def test_generic_exception_caught(self, mock_init, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([0])
        model.predict_proba.return_value = np.array([[0.99, 0.01]])
        _make_models_ready(pipeline, model=model)
        pipeline._shap_explainer = MagicMock()
        pipeline._shap_explainer.shap_values.side_effect = ValueError("SHAP computation failed")
        mock_init.return_value = None

        result = pipeline.predict_with_explanation("hello", explanation_enabled=True)

        assert result["explanation"]["status"] == "error"
        assert "Explanation failed: SHAP computation failed" in result["explanation"]["error_message"]


# ========================  LAZY MODEL LOADING  ==============================

class TestLazyLoading:
    """When model / transformer are None, the method should call _load_models."""

    @patch.object(PredictionPipeline, "_load_models")
    def test_lazy_loads_models_when_none(self, mock_load, pipeline):
        # Both are None (the default after load_models=False)
        assert pipeline.model is None
        assert pipeline.feature_transformer is None

        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([1])
        mock_model.predict_proba.return_value = np.array([[0.05, 0.95]])
        mock_load.return_value = None

        # We need to patch the model AFTER _load_models would have been called
        # but before the code uses it — we'll set them manually after lazy load
        def _side_effect():
            pipeline.model = mock_model
            pipeline.feature_transformer = MagicMock()

        mock_load.side_effect = _side_effect

        result = pipeline.predict_with_explanation("test email", explanation_enabled=False)

        mock_load.assert_called_once()
        assert result["prediction"] == "Ham"

    @patch.object(PredictionPipeline, "_load_models")
    def test_load_models_not_called_when_already_loaded(self, mock_load, pipeline):
        _make_models_ready(pipeline)
        pipeline.predict_with_explanation("test", explanation_enabled=False)
        mock_load.assert_not_called()


# ========================  RETURN STRUCTURE INTEGRITY  ======================

class TestReturnStructure:
    """Ensure every branch returns the full expected dict keys."""

    EXPECTED_KEYS = {"prediction", "confidence", "raw_prediction", "explanation"}
    EXPLANATION_KEYS = {
        "status", "word_contributions", "top_spam_words",
        "top_ham_words", "highlighted_html", "error_message",
    }

    def _assert_structure(self, result):
        assert self.EXPECTED_KEYS.issubset(result.keys()), (
            f"Missing keys in top-level result: {self.EXPECTED_KEYS - result.keys()}"
        )
        assert self.EXPLANATION_KEYS.issubset(result["explanation"].keys()), (
            f"Missing keys in explanation: {self.EXPLANATION_KEYS - result['explanation'].keys()}"
        )

    def test_disabled_structure(self, pipeline):
        _make_models_ready(pipeline)
        result = pipeline.predict_with_explanation("test", explanation_enabled=False)
        self._assert_structure(result)

    def test_available_structure(self, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([0])
        model.predict_proba.return_value = np.array([[0.99, 0.01]])
        _make_models_ready(pipeline, model=model)
        pipeline._shap_explainer = MagicMock()
        pipeline._shap_explainer.shap_values.return_value = np.array([[0.5, -0.2]])
        pipeline._feature_names = np.array(["a", "b"])

        result = pipeline.predict_with_explanation("a b", explanation_enabled=True)
        self._assert_structure(result)

    @patch.object(PredictionPipeline, "_init_explainer")
    def test_error_structure(self, mock_init, pipeline):
        model = MagicMock()
        model.predict.return_value = np.array([0])
        model.predict_proba.return_value = np.array([[0.99, 0.01]])
        _make_models_ready(pipeline, model=model)
        pipeline._shap_explainer = MagicMock()
        pipeline._shap_explainer.shap_values.side_effect = RuntimeError("boom")
        mock_init.return_value = None

        result = pipeline.predict_with_explanation("test", explanation_enabled=True)
        self._assert_structure(result)
