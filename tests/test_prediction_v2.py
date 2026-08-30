"""Tests for prediction pipeline."""

from unittest.mock import MagicMock, patch

from src.pipeline.prediction_pipeline import PredictionPipeline




pytestmark = pytest.mark.slow
class TestPredictionPipeline:
    """Tests for PredictionPipeline."""

    def test_init(self):
        pipeline = PredictionPipeline()
        assert pipeline is not None

    @patch("src.pipeline.prediction_pipeline.Config")
    def test_predict_spam(self, mock_config):
        mock_cfg = MagicMock()
        mock_cfg.model_path = None
        mock_config.return_value = mock_cfg
        pipeline = PredictionPipeline()
        # Without a model, should handle gracefully
        result = pipeline.predict("Buy cheap pills now!!!")
        assert result is not None
        assert "prediction" in result
