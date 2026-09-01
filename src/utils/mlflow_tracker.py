"""MLflow tracking integration for Smart-Spam-Detector.

Provides experiment tracking, model logging, and model registry
capabilities. Falls back gracefully if MLflow is not installed
or MLFLOW_TRACKING_URI is not configured.

Usage:
    from src.utils.mlflow_tracker import MLflowTracker

    tracker = MLflowTracker()
    with tracker.start_run("spam-detection-v1"):
        # Log parameters
        tracker.log_params({"model": "logistic_regression", "cv_folds": 5})
        # Log metrics
        tracker.log_metrics({"f1": 0.95, "accuracy": 0.93})
        # Log model
        tracker.log_model(model, "spam-model", {"tfidf": vectorizer})
"""

import os
from contextlib import contextmanager
from typing import Any

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Lazy MLflow import
_mlflow: Any = None
_mlflow_available: bool | None = None


def _get_mlflow() -> Any:
    """Lazily import mlflow. Returns None if not installed."""
    global _mlflow, _mlflow_available
    if _mlflow_available is None:
        try:
            import mlflow

            _mlflow = mlflow
            _mlflow_available = True
        except ImportError:
            _mlflow_available = False
            logger.warning("mlflow not installed — tracking disabled")
    return _mlflow


class MLflowTracker:
    """MLflow experiment tracker with graceful fallback.

    If MLFLOW_TRACKING_URI is not set or mlflow is not installed,
    all operations become no-ops (logged but not persisted).
    """

    def __init__(self, experiment_name: str = "smart-spam-detector") -> None:
        self.experiment_name = experiment_name
        self._mlflow = _get_mlflow()
        self._enabled = self._mlflow is not None and bool(
            os.environ.get("MLFLOW_TRACKING_URI", "")
        )
        self._run: Any = None

        if self._enabled:
            self._mlflow.set_experiment(experiment_name)
            logger.info(f"MLflow tracking enabled: {experiment_name}")
        else:
            reason = (
                "MLFLOW_TRACKING_URI not set"
                if self._mlflow is not None
                else "mlflow not installed"
            )
            logger.info(f"MLflow tracking disabled: {reason}")

    @contextmanager
    def start_run(self, run_name: str | None = None) -> None:
        """Context manager for an MLflow run.

        Usage:
            with tracker.start_run("my-run"):
                tracker.log_params({"key": "value"})
        """
        if not self._enabled:
            yield self
            return

        self._run = self._mlflow.start_run(run_name=run_name)
        try:
            yield self
        finally:
            self._mlflow.end_run()
            self._run = None

    def log_params(self, params: dict[str, Any]) -> None:
        """Log parameters to the active MLflow run."""
        if not self._enabled or self._run is None:
            return
        self._mlflow.log_params(params)

    def log_metric(self, key: str, value: float, step: int | None = None) -> None:
        """Log a single metric."""
        if not self._enabled or self._run is None:
            return
        self._mlflow.log_metric(key, value, step=step)

    def log_metrics(self, metrics: dict[str, float], step: int | None = None) -> None:
        """Log multiple metrics."""
        if not self._enabled or self._run is None:
            return
        self._mlflow.log_metrics(metrics, step=step)

    def log_model(
        self,
        model: Any,
        artifact_name: str,
        registered_model_name: str | None = None,
        extra_artifacts: dict[str, Any] | None = None,
    ) -> str | None:
        """Log a model to MLflow.

        Args:
            model: The trained model (sklearn compatible).
            artifact_name: Name for the logged model artifact.
            registered_model_name: If provided, register in MLflow Model Registry.
            extra_artifacts: Dict of name→object to log alongside the model.

        Returns:
            Run ID if logged, None otherwise.
        """
        if not self._enabled or self._run is None:
            return None

        # Log the main model
        model_info = self._mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=artifact_name,
            registered_model_name=registered_model_name,
        )

        # Log extra artifacts (e.g., vectorizer)
        if extra_artifacts:
            import pickle
            import tempfile

            for name, obj in extra_artifacts.items():
                with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
                    pickle.dump(obj, f)
                    self._mlflow.log_artifact(f.name, artifact_path=artifact_name)
                    os.unlink(f.name)

        logger.info(f"Model logged to MLflow: {artifact_name}")
        return model_info.run_id

    def log_artifact(self, local_path: str, artifact_path: str | None = None) -> None:
        """Log a local file as an MLflow artifact."""
        if not self._enabled or self._run is None:
            return
        self._mlflow.log_artifact(local_path, artifact_path=artifact_path)

    def search_runs(self, max_results: int = 10) -> list[dict[str, Any]]:
        """Search for recent runs in the experiment."""
        if not self._enabled:
            return []
        runs = self._mlflow.search_runs(
            experiment_names=[self.experiment_name],
            max_results=max_results,
            order_by=["start_time DESC"],
        )
        return runs.to_dict("records") if hasattr(runs, "to_dict") else []

    def load_model(self, model_name: str, version: str = "latest") -> Any:
        """Load a model from the MLflow Model Registry.

        Args:
            model_name: Registered model name.
            version: "latest" or specific version number.

        Returns:
            Loaded model or None if not available.
        """
        if not self._enabled:
            return None
        try:
            model_uri = f"models:/{model_name}/{version}"
            return self._mlflow.sklearn.load_model(model_uri)
        except (OSError, ValueError) as e:
            logger.warning(f"Failed to load model from MLflow: {e}")
            return None
