"""Tests for data transformation pipeline."""

import pandas as pd
import pytest

from src.components.data_transformation import DataTransformation
from src.utils.state import TrainingState


class TestDataTransformation:
    """Tests for DataTransformation.transform_data."""

    def test_transform_basic(self) -> None:
        dt = DataTransformation()
        state = TrainingState()
        state.training_data = pd.DataFrame({
            "Message": ["Buy now!!!", "Hey, how are you?", "Free money!", "Meeting tomorrow"],
            "Category": ["spam", "ham", "spam", "ham"],
        })
        result = dt.transform_data(state)
        assert result.X_train_tfidf is not None
        assert result.X_test_tfidf is not None
        assert result.tfidf_vectorizer is not None
        assert result.y_train is not None
        assert result.y_test is not None

    def test_transform_empty_data_raises(self) -> None:
        dt = DataTransformation()
        state = TrainingState()
        state.training_data = pd.DataFrame()
        with pytest.raises(ValueError, match="No training data"):
            dt.transform_data(state)

    def test_transform_none_data_raises(self) -> None:
        dt = DataTransformation()
        state = TrainingState()
        state.training_data = None
        with pytest.raises(ValueError, match="No training data"):
            dt.transform_data(state)

    def test_label_encoding(self) -> None:
        dt = DataTransformation()
        state = TrainingState()
        state.training_data = pd.DataFrame({
            "Message": ["a", "b", "c", "d"],
            "Category": ["spam", "ham", "spam", "ham"],
        })
        result = dt.transform_data(state)
        # spam=0, ham=1
        assert all(v in [0, 1] for v in result.y_train)
        assert all(v in [0, 1] for v in result.y_test)

    def test_tfidf_features_shape(self) -> None:
        dt = DataTransformation()
        state = TrainingState()
        state.training_data = pd.DataFrame({
            "Message": ["hello world"] * 10 + ["goodbye world"] * 10,
            "Category": ["ham"] * 10 + ["spam"] * 10,
        })
        result = dt.transform_data(state)
        assert result.X_train_tfidf.shape[0] == len(result.y_train)
        assert result.X_test_tfidf.shape[0] == len(result.y_test)
        # TF-IDF should have features > 0
        assert result.X_train_tfidf.shape[1] > 0
