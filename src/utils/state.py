from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class TrainingState:
    """Mutable state object passed through the training pipeline stages."""

    training_data_path: str | None = None
    training_data: pd.DataFrame | None = None
    transformed_data: pd.DataFrame | None = None
    X_train: pd.Series | None = None
    X_test: pd.Series | None = None
    y_train: pd.Series | None = None
    y_test: pd.Series | None = None
    X_train_tfidf: Any | None = None
    X_test_tfidf: Any | None = None
    tfidf_vectorizer: Any | None = None
    trained_models: dict[str, Any] | None = field(default=None)
    model_metrics: dict[str, dict[str, float]] | None = field(default=None)
    best_model_name: str | None = None
    best_model: Any | None = None
    best_params: dict[str, Any] | None = field(default=None)
    cv_results: dict[str, Any] | None = field(default=None)
