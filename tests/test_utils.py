"""Tests for utility functions."""

import os
import tempfile
import pickle
from pathlib import Path

import pytest
import pandas as pd
import numpy as np

from src.utils.utils import (
    ensure_dir,
    save_pickle,
    load_pickle,
    validate_dataset,
    get_dataset_stats,
)


class TestEnsureDir:
    """Tests for ensure_dir function."""

    def test_ensure_dir_creates(self):
        """Test that ensure_dir creates a new directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, "test", "nested", "dirs")
            result = ensure_dir(new_dir)
            assert os.path.exists(new_dir)
            assert os.path.isdir(new_dir)
            assert isinstance(result, Path)

    def test_ensure_dir_existing(self):
        """Test that ensure_dir handles existing directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ensure_dir(tmpdir)
            assert os.path.exists(tmpdir)
            assert isinstance(result, Path)


class TestPickleFunctions:
    """Tests for save_pickle and load_pickle."""

    def test_save_and_load_pickle(self):
        """Test round-trip save and load of pickle files."""
        data = {"key": "value", "list": [1, 2, 3], "number": 42}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.pkl")
            
            # Save
            saved_path = save_pickle(data, filepath)
            assert saved_path == filepath
            assert os.path.exists(filepath)
            
            # Load
            loaded = load_pickle(filepath)
            assert loaded == data

    def test_load_pickle_not_found(self):
        """Test that load_pickle raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_pickle("/nonexistent/path/file.pkl")


class TestValidateDataset:
    """Tests for validate_dataset function."""

    def test_valid_dataset(self):
        """Test validation passes for correct dataset."""
        df = pd.DataFrame({
            'Category': ['spam', 'ham'],
            'Message': ['buy now', 'hello friend'],
        })
        result = validate_dataset(df, ['Category', 'Message'])
        assert result is True

    def test_missing_columns(self):
        """Test validation raises ValueError for missing columns."""
        df = pd.DataFrame({
            'Message': ['buy now', 'hello friend'],
        })
        with pytest.raises(ValueError) as exc:
            validate_dataset(df, ['Category', 'Message'])
        assert 'Category' in str(exc.value)


class TestGetDatasetStats:
    """Tests for get_dataset_stats function."""

    def test_basic_stats(self):
        """Test that stats returns expected structure."""
        df = pd.DataFrame({
            'Category': ['spam', 'ham', 'spam'],
            'Message': ['buy now', 'hello friend', 'click here'],
        })
        stats = get_dataset_stats(df)
        
        assert stats['total_samples'] == 3
        assert 'columns' in stats
        assert 'dtypes' in stats
        assert 'missing_values' in stats

    def test_missing_values(self):
        """Test that missing values are reported."""
        df = pd.DataFrame({
            'A': [1, None, 3],
            'B': ['x', 'y', None],
        })
        stats = get_dataset_stats(df)
        assert stats['missing_values']['A'] == 1
        assert stats['missing_values']['B'] == 1
