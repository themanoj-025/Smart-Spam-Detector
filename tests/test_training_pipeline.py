"""Tests for training pipeline."""


from src.pipeline.training_pipeline import TrainingPipeline


class TestTrainingPipeline:
    """Tests for TrainingPipeline."""

    def test_init(self):
        pipeline = TrainingPipeline()
        assert pipeline is not None
