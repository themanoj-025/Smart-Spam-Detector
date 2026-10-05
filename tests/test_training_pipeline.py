"""Tests for training pipeline."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

from src.components.model_training import ModelTraining, _assert_feature_alignment
from src.pipeline.training_pipeline import TrainingPipeline
from src.utils.state import TrainingState


class TestTrainingPipeline:
    """Tests for TrainingPipeline."""

    def test_init(self) -> None:
        pipeline = TrainingPipeline()
        assert pipeline is not None


class TestFeatureAlignment:
    """Hard assertions on the model contract: a trained estimator's learned
    feature space must match the matrix it is evaluated on.

    The training pipeline trains each model on the TF-IDF transformed matrix
    produced by the saved vectorizer, so a downstream vectorizer with a
    different vocabulary count breaks prediction. These tests pin that contract.
    """

    @pytest.fixture
    def state(self) -> TrainingState:
        """A minimal training state carrying TF-IDF matrices with a known feature count."""
        state = TrainingState()
        X_train = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        X_test = np.array([[1, 2, 3], [4, 5, 6]])
        state.X_train_tfidf = X_train
        state.X_test_tfidf = X_test
        state.y_train = np.array([0, 1, 0])
        state.y_test = np.array([1, 0])
        return state

    @pytest.fixture
    def model_training(self) -> ModelTraining:
        """A ModelTraining instance with a lightweight config (no MLflow run)."""
        trainer = ModelTraining()
        trainer.config = MagicMock()
        trainer.config.OUTPUT_BASE_DIR = "./outputs"
        trainer.config.random_state = 42
        return trainer

    @pytest.mark.unit
    def test_assert_feature_alignment_passes_for_matching_input(
        self, model_training: ModelTraining, state: TrainingState
    ) -> None:
        """Aligned input (same feature count) must pass the assertion unimpeded."""
        model = LogisticRegression(random_state=model_training.config.random_state)
        model.fit(state.X_train_tfidf, state.y_train)
        _assert_feature_alignment(model, state.X_test_tfidf)

    @pytest.mark.unit
    def test_assert_feature_alignment_raises_for_mismatched_input(
        self, model_training: ModelTraining, state: TrainingState
    ) -> None:
        """A vectorizer with a different vocabulary count must fail fast."""
        model = LogisticRegression(random_state=model_training.config.random_state)
        model.fit(state.X_train_tfidf, state.y_train)
        mismatched = np.zeros(
            (state.X_test_tfidf.shape[0], state.X_test_tfidf.shape[1] + 1)
        )
        with pytest.raises(AssertionError, match="Feature space mismatch"):
            _assert_feature_alignment(model, mismatched)

    @pytest.mark.unit
    def test_assert_feature_alignment_model_without_feature_names_in_skips(
        self, model_training: ModelTraining, state: TrainingState
    ) -> None:
        """Estimators without feature_names_in_ are compared against their shape."""
        class DummyClassifier:
            def fit(self, X, y):
                self.n_features_in_ = X.shape[1]
                return self

            def predict(self, X):
                return np.zeros(X.shape[0], dtype=int)

        model = DummyClassifier()
        model.fit(state.X_train_tfidf, state.y_train)
        _assert_feature_alignment(model, state.X_test_tfidf)
