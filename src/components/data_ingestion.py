"""Data ingestion module for loading and validating the email dataset."""

import pandas as pd
from src.utils.logger import get_logger
from src.config.config import Config
from src.utils.state import TrainingState
from src.utils.utils import validate_dataset, get_dataset_stats

logger = get_logger(__name__)


class DataIngestion:
    """Handles loading and validation of the email classification dataset.

    This component is the first step in the training pipeline. It loads
    the CSV dataset, validates the required columns exist, and logs
    comprehensive statistics about the data.
    """

    REQUIRED_COLUMNS = ['Category', 'Message']

    def __init__(self):
        self.config = Config()

    def load_data(self, state: TrainingState) -> TrainingState:
        """Load the training dataset from CSV and validate its structure.

        Args:
            state: Current training state to update with loaded data.

        Returns:
            Updated training state with loaded data.

        Raises:
            FileNotFoundError: If the dataset file does not exist.
            ValueError: If the dataset is missing required columns or is empty.
        """
        try:
            logger.info(f"Loading data from: {self.config.training_data_path}")

            # Check if file exists
            import os
            if not os.path.exists(self.config.training_data_path):
                raise FileNotFoundError(
                    f"Training data not found at: {self.config.training_data_path}. "
                    f"Please ensure the dataset is placed in the correct location."
                )

            # Load data
            state.training_data = pd.read_csv(self.config.training_data_path)

            # Validate structure
            validate_dataset(state.training_data, self.REQUIRED_COLUMNS)

            # Log dataset statistics
            stats = get_dataset_stats(state.training_data)
            logger.info(f"Dataset loaded successfully: {stats['total_samples']} emails")
            logger.info(f"Columns: {stats['columns']}")
            logger.info(f"Category distribution: {stats.get('Category_value_counts', {})}")
            logger.info(f"Missing values: {stats['missing_values']}")

            if stats['total_samples'] == 0:
                raise ValueError("Dataset is empty - no records found")

            return state

        except FileNotFoundError:
            logger.error(f"Data file not found: {self.config.training_data_path}")
            raise
        except ValueError as e:
            logger.error(f"Data validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            raise
