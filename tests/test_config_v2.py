"""Tests for config module."""

import os

from src.config.config import Config, ModelConfig, find_latest_artifacts


class TestFindLatestArtifacts:
    """Tests for find_latest_artifacts."""

    def test_no_outputs_dir(self, tmp_path):
        model, feat = find_latest_artifacts(tmp_path)
        assert model is None
        assert feat is None

    def test_no_runs(self, tmp_path):
        os.makedirs(tmp_path / "outputs")
        model, feat = find_latest_artifacts(tmp_path)
        assert model is None
        assert feat is None

    def test_finds_artifacts(self, tmp_path):
        run_dir = tmp_path / "outputs" / "20250101_120000" / "models"
        os.makedirs(run_dir)
        (run_dir / "test_model.pkl").touch()
        (run_dir / "vectorizer.pkl").touch()
        model, feat = find_latest_artifacts(tmp_path)
        assert model is not None
        assert "test_model.pkl" in model
        assert feat is not None
        assert "vectorizer.pkl" in feat


class TestConfig:
    """Tests for Config dataclass."""

    def test_default_config(self):
        config = Config()
        assert config.test_size == 0.2
        assert config.random_state == 42

    def test_model_config_defaults(self):
        mc = ModelConfig()
        assert mc.cv_folds == 5
        assert mc.scoring == "f1"
        assert "LogisticRegression" in mc.models
        assert "RandomForest" in mc.models
        assert "XGBoost" in mc.models
