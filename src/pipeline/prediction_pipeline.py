"""Prediction pipeline for running inference with trained models.

Supports single email classification, MBOX file processing,
batch prediction with comprehensive result formatting,
and SHAP-based explainability for word-level predictions.
"""

import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.config.config import Config
from src.pipeline.prediction_explainer import get_word_contributions, highlight_text
from src.pipeline.prediction_mailbox import (
    load_mailbox_file,
    process_mailbox_messages,
    run_batch_prediction,
)
from src.pipeline.prediction_mailbox import (
    predict_mbox_file as _predict_mbox_file,
)
from src.utils.email_utils import clean_text
from src.utils.logger import get_logger
from src.utils.mlflow_tracker import MLflowTracker
from src.utils.utils import load_pickle

logger = get_logger(__name__)

# Constants for SHAP explainability
_SHAP_BACKGROUND_SIZE = 80
_SHAP_NSAMPLES = 80


class PredictionPipeline:
    """Handles model inference for spam email classification.

    Supports both single email classification and batch processing
    of MBOX files. Models are loaded lazily and cached after first load.
    """

    def __init__(self, load_models: bool = True) -> None:
        """Initialize the prediction pipeline.

        Args:
            load_models: If True, immediately load models. If False,
                        models will be loaded on first prediction.
        """
        self.config = Config()
        self.mailbox = None
        self.feature_transformer: Any = None
        self.model: Any = None
        self._shap_explainer: Any = None
        self._feature_names: np.ndarray | None = None
        self._background_data: Any | None = None

        if load_models:
            self._load_models()

    def _load_models(self) -> None:
        """Load the trained model and TF-IDF vectorizer from disk or MLflow."""
        logger.info("Loading trained models...")

        tracker = MLflowTracker()
        mlflow_model = tracker.load_model("smart-spam-detector")
        if mlflow_model is not None:
            self.model = mlflow_model
            logger.info("✓ Model loaded from MLflow Model Registry")
            if self.config.feature_path:
                self.feature_transformer = load_pickle(self.config.feature_path)
                logger.info(f"✓ Vectorizer loaded: {Path(self.config.feature_path).name}")
            logger.info("Models loaded successfully (MLflow)")
            return

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

    def _load_background_data(self) -> Any:
        """Load a small sample of training data for SHAP background distribution."""
        if self._background_data is not None:
            return self._background_data

        try:
            import pandas as _pd

            df = _pd.read_csv(self.config.training_data_path, nrows=_SHAP_BACKGROUND_SIZE)
            sample_texts = df["Message"].dropna().tolist()
            self._background_data = self.feature_transformer.transform(sample_texts)
            logger.info(f"Loaded {len(sample_texts)} background samples for SHAP")
        except (OSError, ValueError, KeyError) as e:
            logger.warning(f"Could not load background data for SHAP: {e}")
            self._background_data = None

        return self._background_data

    def _init_explainer(self) -> None:
        """Initialize the SHAP KernelExplainer lazily."""
        if self._shap_explainer is not None:
            return

        if self.model is None or self.feature_transformer is None:
            self._load_models()

        if not hasattr(self.model, "predict_proba"):
            logger.warning("Model does not support predict_proba — SHAP explanations unavailable")
            return

        background = self._load_background_data()
        if background is None:
            logger.warning("No background data available — SHAP explanations unavailable")
            return

        try:
            import shap

            logger.info("Initializing SHAP KernelExplainer...")
            try:
                self._shap_explainer = shap.KernelExplainer(
                    self.model.predict_proba,
                    background,
                    link="logit",
                )
            except TypeError:
                logger.info(
                    "SHAP KernelExplainer does not accept 'link' param, retrying without it"
                )
                self._shap_explainer = shap.KernelExplainer(
                    self.model.predict_proba,
                    background,
                )
            self._feature_names = self.feature_transformer.get_feature_names_out()
            logger.info(f"✓ SHAP explainer initialized ({len(self._feature_names)} features)")
        except (OSError, ValueError, ImportError) as e:
            logger.error(f"Failed to initialize SHAP explainer: {e}")
            self._shap_explainer = None

    def predict_single_email(self, email_body: str) -> dict[str, Any]:
        """Classify a single email as Spam or Ham."""
        if not email_body or not email_body.strip():
            raise ValueError("Email body is empty. Please provide email text to classify.")

        if self.model is None or self.feature_transformer is None:
            self._load_models()

        cleaned_body = clean_text(email_body)
        features = self.feature_transformer.transform([cleaned_body])

        prediction = self.model.predict(features)
        prediction_label = "Spam" if str(prediction[0]) == "0" else "Ham"

        confidence = None
        try:
            if hasattr(self.model, "predict_proba"):
                prediction_proba = self.model.predict_proba(features)
                confidence = float(max(prediction_proba[0])) * 100
                confidence = round(confidence, 2)
        except (ValueError, TypeError):
            pass

        logger.info(
            f"Prediction: {prediction_label} {f'(confidence: {confidence}%)' if confidence else ''}"
        )

        return {
            "prediction": prediction_label,
            "confidence": confidence,
            "raw_prediction": int(prediction[0]),
        }

    def predict_with_explanation(
        self,
        email_body: str,
        explanation_enabled: bool = True,
    ) -> dict[str, Any] -> None:
        """Classify a single email with SHAP-based word-level explanation."""
        if not email_body or not email_body.strip():
            raise ValueError("Email body is empty. Please provide email text to classify.")

        if self.model is None or self.feature_transformer is None:
            self._load_models()

        cleaned_body = clean_text(email_body)
        features = self.feature_transformer.transform([cleaned_body])

        prediction = self.model.predict(features)
        prediction_label = "Spam" if str(prediction[0]) == "0" else "Ham"

        confidence = None
        try:
            if hasattr(self.model, "predict_proba"):
                prediction_proba = self.model.predict_proba(features)
                confidence = float(max(prediction_proba[0])) * 100
                confidence = round(confidence, 2)
        except (ValueError, TypeError, RuntimeError):
            pass

        result: dict[str, Any] = {
            "prediction": prediction_label,
            "confidence": confidence,
            "raw_prediction": int(prediction[0]),
            "explanation": {
                "status": "unavailable",
                "word_contributions": [],
                "top_spam_words": [],
                "top_ham_words": [],
                "highlighted_html": "",
                "error_message": "",
            },
        }

        if explanation_enabled:
            try:
                self._init_explainer()
                if self._shap_explainer is None:
                    result["explanation"]["error_message"] = (
                        "SHAP explainer could not be initialized. "
                        "The model may not support predictions with probability estimates."
                    )
                    return result

                shap_values = self._shap_explainer.shap_values(features, nsamples=_SHAP_NSAMPLES)

                if isinstance(shap_values, list):
                    raw_values = shap_values[0]
                else:
                    raw_values = shap_values

                word_contributions = get_word_contributions(raw_values, self._feature_names, 0)

                spam_words = [c for c in word_contributions if c["class"] == "spam"][:10]
                ham_words = [c for c in word_contributions if c["class"] == "ham"][:10]

                highlighted_html = highlight_text(cleaned_body, word_contributions)

                result["explanation"] = {
                    "status": "available",
                    "word_contributions": word_contributions,
                    "top_spam_words": spam_words,
                    "top_ham_words": ham_words,
                    "highlighted_html": highlighted_html,
                    "error_message": "",
                }

                logger.info(
                    f"Explanation generated for {prediction_label}: "
                    f"{len(spam_words)} spam words, {len(ham_words)} ham words"
                )

            except ImportError:
                result["explanation"]["status"] = "error"
                result["explanation"]["error_message"] = (
                    "SHAP library is not installed. Install it with: pip install shap"
                )
            except (ValueError, RuntimeError, TypeError) as e:
                logger.error(f"SHAP explanation failed: {e}")
                result["explanation"]["status"] = "error"
                result["explanation"]["error_message"] = f"Explanation failed: {e!s}"

        return result

    def load_mailbox(self, mailbox_path: str) -> None:
        """Load an MBOX file for batch processing."""
        self.mailbox = load_mailbox_file(mailbox_path)

    def process_mailbox(self, mailbox_path: str | None = None) -> list[dict[str, str]]:
        """Process all emails in an MBOX file and extract relevant fields."""
        if mailbox_path:
            self.load_mailbox(mailbox_path)

        if self.mailbox is None:
            raise ValueError("No mailbox loaded. Call load_mailbox() or provide a path.")

        data = process_mailbox_messages(self.mailbox)
        self.mailbox = None
        return data

    def run_prediction(self, mail_data: list[dict[str, str]]) -> list[dict[str, str]]:
        """Run spam classification on a list of email data."""
        if self.model is None or self.feature_transformer is None:
            self._load_models()

        return run_batch_prediction(mail_data, self.model, self.feature_transformer)

    def predict_mbox_file(
        self, mailbox_path: str, output_path: str | None = None
    ) -> pd.DataFrame -> None:
        """Complete pipeline: load MBOX, process emails, run predictions."""
        if self.model is None or self.feature_transformer is None:
            self._load_models()

        return _predict_mbox_file(mailbox_path, self.model, self.feature_transformer, output_path)
