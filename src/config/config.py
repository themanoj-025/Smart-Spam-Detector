"""Configuration module for the Spam Email Classification system.

This module contains all configuration classes used throughout the project.
Model paths are auto-discovered from the latest training run in the outputs/ directory.
"""

import os
import glob
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
from pathlib import Path


def find_latest_artifacts() -> Tuple[Optional[str], Optional[str]]:
    """Auto-discover the latest trained model and vectorizer from the outputs directory.

    Returns:
        Tuple of (model_path, feature_path) or (None, None) if no artifacts found.
    """
    base_dir = Path("outputs")
    if not base_dir.exists():
        return None, None

    # Find all timestamped run directories
    run_dirs = sorted(
        [d for d in base_dir.iterdir() if d.is_dir() and d.name[:4].isdigit()],
        reverse=True
    )

    for run_dir in run_dirs:
        models_dir = run_dir / "models"
        if models_dir.exists():
            model_files = list(models_dir.glob("*_model.pkl"))
            vectorizer_files = list(models_dir.glob("vectorizer.pkl"))

            if model_files and vectorizer_files:
                return str(model_files[0]), str(vectorizer_files[0])

    return None, None


@dataclass
class Config:
    """Main configuration for data paths and model artifacts.

    Attributes:
        training_data_path: Path to the CSV dataset for training.
        OUTPUT_BASE_DIR: Directory where training outputs are saved.
        model_path: Path to the trained model pickle file (auto-discovered).
        feature_path: Path to the TF-IDF vectorizer pickle file (auto-discovered).
        test_size: Fraction of data to use for testing.
        random_state: Random seed for reproducibility.
    """
    training_data_path: str = "data/dataset/dataset.csv"
    OUTPUT_BASE_DIR: str = "outputs"
    model_path: str = ""
    feature_path: str = ""
    test_size: float = 0.2
    random_state: int = 42

    def __post_init__(self):
        """Auto-discover latest model artifacts after initialization."""
        model_path, feature_path = find_latest_artifacts()
        if model_path and feature_path:
            self.model_path = model_path
            self.feature_path = feature_path
        else:
            # Fall back to checking specific paths
            latest_dir = self._get_latest_output_dir()
            if latest_dir:
                models_dir = os.path.join(latest_dir, "models")
                self.model_path = self._find_first(models_dir, "*_model.pkl")
                self.feature_path = self._find_first(models_dir, "vectorizer.pkl")

    def _get_latest_output_dir(self) -> Optional[str]:
        """Get the most recent timestamped output directory."""
        if not os.path.exists(self.OUTPUT_BASE_DIR):
            return None
        dirs = [
            d for d in os.listdir(self.OUTPUT_BASE_DIR)
            if os.path.isdir(os.path.join(self.OUTPUT_BASE_DIR, d))
        ]
        if not dirs:
            return None
        return os.path.join(self.OUTPUT_BASE_DIR, sorted(dirs)[-1])

    def _find_first(self, directory: str, pattern: str) -> Optional[str]:
        """Find the first file matching a pattern in a directory."""
        files = glob.glob(os.path.join(directory, pattern))
        return files[0] if files else None


@dataclass
class ModelConfig:
    """Configuration for model hyperparameter grids used in GridSearchCV."""

    models: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'LogisticRegression': {
            'C': [0.01, 0.1, 1, 10, 100],
            'solver': ['lbfgs', 'liblinear'],
            'max_iter': [100, 200, 300]
        },
        'DecisionTree': {
            'criterion': ['gini', 'entropy'],
            'max_depth': [5, 10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        },
        'SVM': {
            'C': [0.1, 1, 10],
            'kernel': ['linear', 'rbf'],
            'gamma': ['scale', 'auto']
        },
        'KNN': {
            'n_neighbors': [3, 5, 7, 9, 11],
            'weights': ['uniform', 'distance'],
            'metric': ['euclidean', 'manhattan']
        },
        'RandomForest': {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2']
        }
    })

    cv_folds: int = 5
    scoring: str = 'f1'
    n_jobs: int = -1
