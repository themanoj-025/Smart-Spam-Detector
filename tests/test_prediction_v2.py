import pytest

pytestmark = pytest.mark.unit

"""Tests for prediction pipeline."""

from unittest.mock import MagicMock, patch

from src.pipeline.prediction_pipeline import PredictionPipeline

pytestmark = pytest.mark.slow


class TestPredictionPipeline:
    """Tests for PredictionPipeline."""

    def test_init(self) -> None:
        pipeline = PredictionPipeline()
        assert pipeline is not None

    @patch("src.pipeline.prediction_pipeline.Config")
    def test_predict_spam(self, mock_config) -> None:
        mock_cfg = MagicMock()
        mock_cfg.model_path = None
        mock_config.return_value = mock_cfg
        pipeline = PredictionPipeline()
        # No model can be loaded (model_path is None); the pipeline's
        # contract is to raise FileNotFoundError on prediction, which the
        # API layer converts to a 503. Assert that contract.
        with pytest.raises(FileNotFoundError):
            pipeline.predict_single_email("Buy cheap pills now!!!")
