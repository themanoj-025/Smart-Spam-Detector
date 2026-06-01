from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import pandas as pd


@dataclass
class TrainingState:
    """Mutable state object passed through the training pipeline stages."""
    training_data_path: Optional[str] = None
    training_data: Optional[pd.DataFrame] = None
    transformed_data: Optional[pd.DataFrame] = None
    X_train: Optional[pd.Series] = None
    X_test: Optional[pd.Series] = None
    y_train: Optional[pd.Series] = None
    y_test: Optional[pd.Series] = None
    X_train_tfidf: Optional[Any] = None
    X_test_tfidf: Optional[Any] = None
    tfidf_vectorizer: Optional[Any] = None
    trained_models: Optional[Dict[str, Any]] = field(default=None)
    model_metrics: Optional[Dict[str, Dict[str, float]]] = field(default=None)
    best_model_name: Optional[str] = None
    best_model: Optional[Any] = None
    best_params: Optional[Dict[str, Any]] = field(default=None)
    cv_results: Optional[Dict[str, Any]] = field(default=None)

