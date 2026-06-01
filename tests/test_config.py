"""Tests for the configuration module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from src.config.config import Config, ModelConfig, find_latest_artifacts


class TestConfig:
    """Test the Config dataclass."""

    def test_config_defaults(self):
        """Test that Config resolves absolute paths from project root."""
        config = Config()
        # Paths are now resolved relative to the project root (via __file__)
        project_root = Path(__file__).resolve().parents[1]
        assert config.training_data_path == str(project_root / "data" / "dataset" / "dataset.csv")
        assert config.OUTPUT_BASE_DIR == str(project_root / "outputs")
        assert config.test_size == 0.2
        assert config.random_state == 42

    def test_config_custom_values(self):
        """Test that Config accepts custom values."""
        config = Config(
            training_data_path="custom/path.csv",
            test_size=0.3,
            random_state=123,
        )
        assert config.training_data_path == "custom/path.csv"
        assert config.test_size == 0.3
        assert config.random_state == 123


class TestModelConfig:
    """Test the ModelConfig dataclass."""

    def test_model_config_has_models(self):
        """Test that ModelConfig contains model definitions."""
        config = ModelConfig()
        assert len(config.models) > 0
        assert 'LogisticRegression' in config.models
        assert 'RandomForest' in config.models
        assert config.cv_folds == 5
        assert config.scoring == 'f1'

    def test_model_config_has_param_grids(self):
        """Test that each model has hyperparameter grids."""
        config = ModelConfig()
        for model_name, param_grid in config.models.items():
            assert len(param_grid) > 0, f"{model_name} has no parameters"


class TestFindLatestArtifacts:
    """Test the find_latest_artifacts function."""

    def _create_output_structure(self, base_dir: str, has_models: bool = False):
        """Helper to create mock output directories."""
        run_dir = os.path.join(base_dir, "outputs", "2025-01-01_00-00-00")
        os.makedirs(os.path.join(run_dir, "models"), exist_ok=True)
        os.makedirs(os.path.join(run_dir, "observations"), exist_ok=True)

        if has_models:
            # Create placeholder model files
            models_dir = os.path.join(run_dir, "models")
            Path(os.path.join(models_dir, "SVM_model.pkl")).touch()
            Path(os.path.join(models_dir, "vectorizer.pkl")).touch()

    def test_no_outputs_dir(self):
        """Test when outputs directory doesn't exist (via project_root override)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            model_path, feature_path = find_latest_artifacts(project_root=tmp_root)
            assert model_path is None
            assert feature_path is None

    def test_empty_outputs_dir(self):
        """Test when outputs directory exists but has no model artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            os.makedirs(tmp_root / "outputs" / "empty_run")
            model_path, feature_path = find_latest_artifacts(project_root=tmp_root)
            assert model_path is None
            assert feature_path is None

    def test_with_model_artifacts(self):
        """Test when valid model artifacts exist (via project_root override)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            self._create_output_structure(str(tmp_root), has_models=True)
            model_path, feature_path = find_latest_artifacts(project_root=tmp_root)
            assert model_path is not None
            assert feature_path is not None
            assert model_path.endswith("SVM_model.pkl")
            assert feature_path.endswith("vectorizer.pkl")
