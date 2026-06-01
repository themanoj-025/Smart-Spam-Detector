"""Training pipeline that orchestrates the complete ML workflow end-to-end.

Pipeline steps:
1. Data Ingestion - Load and validate the CSV dataset
2. Data Transformation - Encode labels, split data, apply TF-IDF
3. Model Training - Train multiple models with hyperparameter tuning
4. Artifact Saving - Save best model, vectorizer, and metrics to disk
"""

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_training import ModelTraining
from src.utils.state import TrainingState
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TrainingPipeline:
    """Complete training pipeline orchestrating data processing and model training.

    Usage:
        pipeline = TrainingPipeline()
        state = pipeline.run_pipeline()
        print(f"Best model: {state.best_model_name}")
    """

    def __init__(self):
        self.state = TrainingState()

    def run_pipeline(self) -> TrainingState:
        """Execute the full training pipeline end-to-end.

        Returns:
            Training state with all trained models, metrics, and artifacts.

        Raises:
            Exception: If any pipeline step fails.
        """
        try:
            logger.info("=" * 70)
            logger.info("TRAINING PIPELINE INITIATED")
            logger.info("=" * 70)

            # Step 1: Data Ingestion
            logger.info("\n>>> STEP 1: DATA INGESTION")
            ingestion = DataIngestion()
            self.state = ingestion.load_data(self.state)
            logger.info(
                f"✓ Data loaded: {self.state.training_data.shape[0]} emails, "
                f"{self.state.training_data.shape[1]} columns"
            )

            # Step 2: Data Transformation
            logger.info("\n>>> STEP 2: DATA TRANSFORMATION")
            transformation = DataTransformation()
            self.state = transformation.transform_data(self.state)
            logger.info(
                f"✓ Data transformed: "
                f"{len(self.state.X_train)} train + {len(self.state.X_test)} test samples"
            )

            # Step 3: Model Training
            logger.info("\n>>> STEP 3: MODEL TRAINING")
            trainer = ModelTraining()
            self.state = trainer.train_models(self.state)

            # Summary
            logger.info("\n" + "=" * 70)
            logger.info("TRAINING PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)
            logger.info(f"Best model: {self.state.best_model_name}")
            best_metrics = self.state.model_metrics[self.state.best_model_name]
            logger.info(f"Best F1-Score: {best_metrics['f1_score']:.4f}")
            logger.info(f"Best Accuracy: {best_metrics['accuracy']:.4f}")
            logger.info(f"Models trained: {', '.join(self.state.trained_models.keys())}")

            return self.state

        except Exception as e:
            logger.error(f"Pipeline failed at step: {str(e)}")
            raise


if __name__ == "__main__":
    pipeline = TrainingPipeline()
    state = pipeline.run_pipeline()

    # Print final comparison table
    print("\n[MODEL PERFORMANCE COMPARISON]")
    print("-" * 70)
    print(f"{'Model':<22} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 70)
    for model_name, metrics in sorted(
        state.model_metrics.items(),
        key=lambda x: x[1]['f1_score'],
        reverse=True
    ):
        best = " *" if model_name == state.best_model_name else "  "
        print(
            f"{model_name:<20}{best} "
            f"{metrics['accuracy']:.4f}      "
            f"{metrics['precision']:.4f}      "
            f"{metrics['recall']:.4f}      "
            f"{metrics['f1_score']:.4f}"
        )
    print("-" * 70)
