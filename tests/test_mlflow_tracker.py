import pytest

pytestmark = pytest.mark.unit

"""Tests for MLflow tracker module."""

from unittest.mock import MagicMock, patch

from src.utils.mlflow_tracker import MLFlowTracker


class TestMLFlowTracker:
    """Tests for MLFlowTracker."""

    def test_init(self) -> None:
        tracker = MLFlowTracker()
        assert tracker is not None

    def test_log_params(self, monkeypatch) -> None:
        monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:///tmp/mlruns")
        mock_mlflow = MagicMock()
        with patch("src.utils.mlflow_tracker._get_mlflow", return_value=mock_mlflow):
            tracker = MLFlowTracker()
            with tracker.start_run("test-run"):
                tracker.log_params({"C": 1.0, "max_iter": 100})
            mock_mlflow.log_params.assert_called_once_with({"C": 1.0, "max_iter": 100})

    def test_log_metrics(self, monkeypatch) -> None:
        monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:///tmp/mlruns")
        mock_mlflow = MagicMock()
        with patch("src.utils.mlflow_tracker._get_mlflow", return_value=mock_mlflow):
            tracker = MLFlowTracker()
            with tracker.start_run("test-run"):
                tracker.log_metrics({"accuracy": 0.95, "f1": 0.93})
            mock_mlflow.log_metrics.assert_called_once_with({"accuracy": 0.95, "f1": 0.93}, step=None)
