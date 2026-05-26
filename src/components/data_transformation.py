"""Data transformation module for preprocessing the email dataset.

Handles label encoding, train/test splitting, and TF-IDF vectorization
of the email text data.
"""

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

from src.utils.logger import get_logger
from src.config.config import Config
from src.utils.state import TrainingState

logger = get_logger(__name__)


class DataTransformation:
    """Handles all data preprocessing steps for the spam classification pipeline.
    
    Steps performed:
    1. Encode labels (spam -> 0, ham -> 1)
    2. Split into training and testing sets
    3. Apply TF-IDF vectorization to the text data
    """
    
    def __init__(self):
        self.config = Config()
    
    def transform_data(self, state: TrainingState) -> TrainingState:
        """Execute the full data transformation pipeline.
        
        Args:
            state: Current training state containing raw data.
        
        Returns:
            Updated training state with transformed features and labels.
        
        Raises:
            ValueError: If training data is not loaded or is invalid.
        """
        logger.info("Data transformation started")
        
        try:
            # Validate input
            if state.training_data is None or state.training_data.empty:
                raise ValueError("No training data available. Run data ingestion first.")
            
            data = state.training_data.copy()
            logger.info(f"Raw data shape: {data.shape}")
            
            # Encode labels: spam -> 0, ham -> 1
            label_mapping = {'spam': 0, 'ham': 1}
            data['Category'] = data['Category'].map(label_mapping)
            
            # Check for unmapped labels
            if data['Category'].isnull().any():
                unknown_labels = state.training_data.loc[
                    data['Category'].isnull(), 'Category'
                ].unique()
                raise ValueError(f"Unknown labels found: {unknown_labels}")
            
            # Ensure Category column is integer type
            data['Category'] = data['Category'].astype(int)
            
            # Log label distribution
            spam_count = (data['Category'] == 0).sum()
            ham_count = (data['Category'] == 1).sum()
            logger.info(f"Label encoding completed")
            logger.info(f"Spam (0): {spam_count} ({spam_count/len(data)*100:.1f}%)")
            logger.info(f"Ham (1): {ham_count} ({ham_count/len(data)*100:.1f}%)")
            
            # Split features and target
            X = data['Message']
            y = data['Category']
            
            # Convert y to numpy array of integers
            y = np.array(y, dtype=int)
            
            # Split into train and test sets (80:20 ratio)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=self.config.test_size,
                random_state=self.config.random_state,
                stratify=y
            )
            
            logger.info(f"Train/test split ({1-self.config.test_size:.0f}:{self.config.test_size:.0f})")
            logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
            
            # Apply TF-IDF vectorization (proven settings from notebook experiments)
            tfidf_vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
            )
            
            X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
            X_test_tfidf = tfidf_vectorizer.transform(X_test)
            
            logger.info(f"TF-IDF transformation completed")
            logger.info(f"Training features: {X_train_tfidf.shape}")
            logger.info(f"Test features: {X_test_tfidf.shape}")
            logger.info(f"Vocabulary size: {len(tfidf_vectorizer.vocabulary_)}")
            
            # Save to state
            state.transformed_data = data
            state.X_train = X_train
            state.X_test = X_test
            state.y_train = y_train
            state.y_test = y_test
            state.X_train_tfidf = X_train_tfidf
            state.X_test_tfidf = X_test_tfidf
            state.tfidf_vectorizer = tfidf_vectorizer
            
            logger.info("Data transformation completed successfully")
            return state
            
        except ValueError as e:
            logger.error(f"Data validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to transform data: {str(e)}")
            raise
