"""Tests for training pipeline."""

import pytest
from unittest.mock import MagicMock, patch

from src.pipeline.training_pipeline import TrainingPipeline


class TestTrainingPipeline:
    """Tests for TrainingPipeline."""

    def test_init(self):
        pipeline = TrainingPipeline()
        assert pipeline is not None
