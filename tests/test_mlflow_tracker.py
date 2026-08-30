"""Tests for MLflow tracker module."""

from unittest.mock import patch

from src.utils.mlflow_tracker import MLFlowTracker


class TestMLFlowTracker:
    """Tests for MLFlowTracker."""

    def test_init(self) -> None:
        tracker = MLFlowTracker()
        assert tracker is not None

    @patch("src.utils.mlflow_tracker.mlflow")
    def test_log_params(self, mock_mlflow) -> None:
        tracker = MLFlowTracker()
        tracker.log_params({"C": 1.0, "max_iter": 100})
        mock_mlflow.log_params.assert_called_once()

    @patch("src.utils.mlflow_tracker.mlflow")
    def test_log_metrics(self, mock_mlflow) -> None:
        tracker = MLFlowTracker()
        tracker.log_metrics({"accuracy": 0.95, "f1": 0.93})
        mock_mlflow.log_metrics.assert_called_once()
