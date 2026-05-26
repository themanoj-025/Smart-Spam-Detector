"""Prediction pipeline for running inference with trained models.

Supports single email classification, MBOX file processing,
and batch prediction with comprehensive result formatting.
"""

import mailbox
import pickle
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

import pandas as pd

from src.utils.state import PredictionState
from src.utils.logger import get_logger
from src.config.config import Config
from src.utils.email_utils import extract_body, all_recipients, clean_text
from src.utils.utils import load_pickle

logger = get_logger(__name__)


class PredictionPipeline:
    """Handles model inference for spam email classification.
    
    Supports both single email classification and batch processing
    of MBOX files. Models are loaded lazily and cached after first load.
    """
    
    def __init__(self, load_models: bool = True):
        """Initialize the prediction pipeline.
        
        Args:
            load_models: If True, immediately load models. If False,
                        models will be loaded on first prediction.
        """
        self.config = Config()
        self.mailbox = None
        self.feature_transformer: Any = None
        self.model: Any = None
        
        if load_models:
            self._load_models()
    
    def _load_models(self) -> None:
        """Load the trained model and TF-IDF vectorizer from disk.
        
        Raises:
            FileNotFoundError: If model or vectorizer files are not found.
        """
        logger.info("Loading trained models...")
        
        if not self.config.model_path or not self.config.feature_path:
            raise FileNotFoundError(
                "No trained models found. Please run the training pipeline first:\n"
                "  python -m src.pipeline.training_pipeline"
            )
        
        self.feature_transformer = load_pickle(self.config.feature_path)
        self.model = load_pickle(self.config.model_path)
        
        logger.info(f"✓ Model loaded: {Path(self.config.model_path).name}")
        logger.info(f"✓ Vectorizer loaded: {Path(self.config.feature_path).name}")
        logger.info("Models loaded successfully")
    
    def predict_single_email(self, email_body: str) -> Dict[str, Any]:
        """Classify a single email as Spam or Ham.
        
        Args:
            email_body: The text content of the email to classify.
        
        Returns:
            Dictionary with keys:
                - 'prediction': 'Spam' or 'Ham'
                - 'confidence': Confidence percentage (or None)
                - 'raw_prediction': Integer prediction (0 or 1)
        
        Raises:
            ValueError: If email body is empty.
        """
        if not email_body or not email_body.strip():
            raise ValueError("Email body is empty. Please provide email text to classify.")
        
        # Lazy load models if not already loaded
        if self.model is None or self.feature_transformer is None:
            self._load_models()
        
        # Clean and vectorize
        cleaned_body = clean_text(email_body)
        features = self.feature_transformer.transform([cleaned_body])
        
        # Predict
        prediction = self.model.predict(features)
        prediction_label = "Spam" if str(prediction[0]) == "0" else "Ham"
        
        # Get confidence score
        confidence = None
        try:
            if hasattr(self.model, "predict_proba"):
                prediction_proba = self.model.predict_proba(features)
                confidence = float(max(prediction_proba[0])) * 100
                confidence = round(confidence, 2)
        except Exception:
            pass
        
        logger.info(f"Prediction: {prediction_label} "
                   f"{f'(confidence: {confidence}%)' if confidence else ''}")
        
        return {
            'prediction': prediction_label,
            'confidence': confidence,
            'raw_prediction': int(prediction[0])
        }
    
    def load_mailbox(self, mailbox_path: str) -> None:
        """Load an MBOX file for batch processing.
        
        Args:
            mailbox_path: Path to the MBOX file.
        
        Raises:
            FileNotFoundError: If the MBOX file does not exist.
        """
        if not Path(mailbox_path).exists():
            raise FileNotFoundError(f"MBOX file not found: {mailbox_path}")
        
        logger.info(f"Loading mailbox: {mailbox_path}")
        self.mailbox = mailbox.mbox(mailbox_path)
        logger.info(f"Loaded {len(self.mailbox)} messages from mailbox")
    
    def process_mailbox(self, mailbox_path: Optional[str] = None) -> List[Dict[str, str]]:
        """Process all emails in an MBOX file and extract relevant fields.
        
        Args:
            mailbox_path: Optional path to MBOX file. If not provided,
                         uses previously loaded mailbox.
        
        Returns:
            List of dictionaries with email data (Time, Subject, Body, etc.).
        """
        if mailbox_path:
            self.load_mailbox(mailbox_path)
        
        if self.mailbox is None:
            raise ValueError("No mailbox loaded. Call load_mailbox() or provide a path.")
        
        logger.info("Processing mailbox messages...")
        data = []
        
        for i, message in enumerate(self.mailbox):
            labels = (message.get("X-Gmail-Labels") or "").lower()
            category = (
                "Spam" if "spam" in labels else
                "Promotions" if "category_promotions" in labels else
                "Social" if "category_social" in labels else
                "Updates" if "category_updates" in labels else
                "Inbox"
            )
            
            data.append({
                "Time": message.get("Date", ""),
                "Recipients": clean_text(all_recipients(message)),
                "Subject": clean_text(message.get("Subject", "")),
                "Body": clean_text(extract_body(message)),
                "Category": category,
                "Direction": "Sent" if "Sent" in labels else "Received"
            })
            
            if (i + 1) % 100 == 0:
                logger.info(f"  Processed {i + 1}/{len(self.mailbox)} messages...")
        
        logger.info(f"✓ Processed {len(data)} emails from mailbox")
        self.mailbox.close()
        
        return data
    
    def run_prediction(self, mail_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Run spam classification on a list of email data.
        
        Args:
            mail_data: List of email dictionaries with 'Body' field.
        
        Returns:
            Updated list with 'Prediction' field added to each item.
        """
        if self.model is None or self.feature_transformer is None:
            self._load_models()
        
        start_time = time.time()
        logger.info(f"Running predictions on {len(mail_data)} emails...")
        
        for i, mail in enumerate(mail_data):
            body_text = mail.get('Body', '')
            if body_text:
                features = self.feature_transformer.transform([body_text])
                prediction = self.model.predict(features)
                mail["Prediction"] = "Spam" if str(prediction[0]) == "0" else "Ham"
            else:
                mail["Prediction"] = "Unknown"
        
        elapsed = time.time() - start_time
        spam_count = sum(1 for m in mail_data if m.get("Prediction") == "Spam")
        logger.info(f"✓ Predictions completed in {elapsed:.2f}s "
                   f"({len(mail_data)/elapsed:.0f} emails/sec)")
        logger.info(f"  Spam: {spam_count} | Ham: {len(mail_data) - spam_count}")
        
        return mail_data
    
    def predict_mbox_file(
        self,
        mailbox_path: str,
        output_path: Optional[str] = None
    ) -> pd.DataFrame:
        """Complete pipeline: load MBOX, process emails, run predictions.
        
        Args:
            mailbox_path: Path to the MBOX file.
            output_path: Optional path to save results as CSV.
        
        Returns:
            DataFrame with all email data and predictions.
        """
        mail_data = self.process_mailbox(mailbox_path)
        mail_data = self.run_prediction(mail_data)
        df = pd.DataFrame(mail_data)
        
        if output_path:
            df.to_csv(output_path, index=False)
            logger.info(f"Predictions saved to {output_path}")
        
        return df


def run_legacy_pipeline(state: PredictionState) -> None:
    """Legacy function for backward compatibility.
    
    Args:
        state: Prediction state with mailbox path.
    """
    pipeline = PredictionPipeline(load_models=False)
    pipeline.load_mailbox(state.mailbox_path)
    mail_data = pipeline.process_mailbox()
    state.mail_data = mail_data
    state.mail_data = pipeline.run_prediction(state.mail_data)
    df = pd.DataFrame(state.mail_data)
    df.to_csv("data/predictions.csv", index=False)
    logger.info("Legacy prediction completed and saved to data/predictions.csv")
