"""Prediction pipeline for running inference with trained models.

Supports single email classification, MBOX file processing,
batch prediction with comprehensive result formatting,
and SHAP-based explainability for word-level predictions.
"""

import mailbox
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.logger import get_logger
from src.config.config import Config
from src.utils.email_utils import extract_body, all_recipients, clean_text
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
        self._shap_explainer: Any = None
        self._feature_names: Optional[np.ndarray] = None
        self._background_data: Optional[Any] = None

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

    def _load_background_data(self) -> Any:
        """Load a small sample of training data for SHAP background distribution.

        Reads only the necessary rows to avoid loading the full dataset into memory.

        Returns:
            Transformed TF-IDF matrix of background samples.
        """
        if self._background_data is not None:
            return self._background_data

        try:
            # Read only the rows we need — SHAP just needs a representative sample
            df = pd.read_csv(self.config.training_data_path, nrows=_SHAP_BACKGROUND_SIZE)
            sample_texts = df['Message'].dropna().tolist()
            self._background_data = self.feature_transformer.transform(sample_texts)
            logger.info(f"Loaded {len(sample_texts)} background samples for SHAP")
        except Exception as e:
            logger.warning(f"Could not load background data for SHAP: {e}")
            self._background_data = None

        return self._background_data

    def _init_explainer(self) -> None:
        """Initialize the SHAP KernelExplainer lazily.

        The explainer is created once and cached on the instance.
        """
        if self._shap_explainer is not None:
            return

        if self.model is None or self.feature_transformer is None:
            self._load_models()

        # Ensure model has predict_proba
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
                # Some shap versions removed the 'link' parameter
                logger.info("SHAP KernelExplainer does not accept 'link' param, retrying without it")
                self._shap_explainer = shap.KernelExplainer(
                    self.model.predict_proba,
                    background,
                )
            self._feature_names = self.feature_transformer.get_feature_names_out()
            logger.info(f"✓ SHAP explainer initialized ({len(self._feature_names)} features)")
        except Exception as e:
            logger.error(f"Failed to initialize SHAP explainer: {e}")
            self._shap_explainer = None

    def _get_word_contributions(
        self,
        shap_values: np.ndarray,
        class_index: int,
    ) -> List[Dict[str, Any]]:
        """Convert raw SHAP values into per-word contribution records.

        Handles both numpy arrays and ``shap.Explanation`` objects so the
        function works with shap >= 0.42 and shap >= 0.45+.

        Args:
            shap_values: SHAP values array for one sample, shape
                (n_features,) or (n_features, n_classes), **or** a
                ``shap.Explanation`` instance from newer SHAP versions.
            class_index: Index of the class to explain (0=Spam, 1=Ham).

        Returns:
            List of dicts with 'word', 'contribution', and 'class' keys,
            sorted by absolute contribution descending.
        """
        # Newer SHAP versions (>= 0.45) return Explanation objects.
        # Extract the underlying numpy array when that happens.
        if hasattr(shap_values, 'values'):
            shap_values = shap_values.values

        # Ensure we have a numpy array from here on
        shap_values = np.asarray(shap_values)

        # shap_values shape: (n_samples, n_features) for binary classification
        if shap_values.ndim == 2:
            values = shap_values[0]  # first (only) sample
        elif shap_values.ndim == 1:
            values = shap_values
        else:
            values = shap_values[0, :, class_index]

        contributions = []
        for i, val in enumerate(values):
            if abs(val) < 1e-6:
                continue
            word = self._feature_names[i] if self._feature_names is not None else f"feature_{i}"
            contributions.append({
                'word': str(word),
                'contribution': float(val),
                'class': 'spam' if val > 0 else 'ham',
            })

        contributions.sort(key=lambda x: abs(x['contribution']), reverse=True)
        return contributions

    def _highlight_text(
        self,
        text: str,
        contributions: List[Dict[str, Any]],
        max_words: int = 40,
    ) -> str:
        """Generate HTML with word-level highlighting based on SHAP contributions.

        Args:
            text: Original email text.
            contributions: Word contribution data from _get_word_contributions.
            max_words: Maximum number of top contributing words to highlight.

        Returns:
            HTML string with color-coded word spans.
        """
        # Build a lookup from word -> contribution
        word_map = {}
        for c in contributions[:max_words]:
            word_map[c['word'].lower()] = c

        def word_color(word: str) -> str:
            """Determine background color intensity based on contribution."""
            info = word_map.get(word.lower())
            if info is None:
                return ''
            val = info['contribution']
            # Clamp intensity between 0 and 1
            intensity = min(abs(val) / 2.0, 1.0)
            if val > 0:
                # Red for spam-pushing
                r = 255
                g = int(255 * (1 - intensity * 0.7))
                b = int(255 * (1 - intensity * 0.7))
            else:
                # Green for ham-pushing
                r = int(255 * (1 - intensity * 0.7))
                g = 255
                b = int(255 * (1 - intensity * 0.7))
            return f'background-color: rgba({r},{g},{b},0.5); border-radius: 3px; padding: 0 2px;'

        # Tokenize the text, preserving whitespace
        import re
        tokens = re.split(r'(\s+)', text)
        highlighted = []
        for token in tokens:
            if not token.strip():
                highlighted.append(token)
            else:
                color = word_color(token.strip('.,!?;:\'"()[]{}'))
                if color:
                    contrib = word_map[token.lower()]["contribution"]
                    highlighted.append(
                        f'<span style="{color}" '
                        f'title="contribution: {contrib:.4f}">'
                        f'{token}</span>'
                    )
                else:
                    highlighted.append(token)

        return ''.join(highlighted)

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

        logger.info(
            f"Prediction: {prediction_label} "
            f"{f'(confidence: {confidence}%)' if confidence else ''}"
        )

        return {
            'prediction': prediction_label,
            'confidence': confidence,
            'raw_prediction': int(prediction[0])
        }

    def predict_with_explanation(
        self,
        email_body: str,
        explanation_enabled: bool = True,
    ) -> Dict[str, Any]:  # noqa: C901
        """Classify a single email with SHAP-based word-level explanation.

        Builds on `predict_single_email` to avoid code duplication. If the
        explanation is available, the returned dict includes a nested 'explanation'
        key with word-level contribution data and highlighted HTML.

        Args:
            email_body: The text content of the email to classify.
            explanation_enabled: If True, compute SHAP explanation (may take 3-5s).

        Returns:
            Dictionary with keys from predict_single_email plus:
                - 'explanation': Dict with:
                    - 'word_contributions': List of word contribution records
                    - 'top_spam_words': Top 10 words pushing toward spam
                    - 'top_ham_words': Top 10 words pushing toward ham
                    - 'highlighted_html': HTML with color-coded words
                    - 'status': 'available' or 'unavailable' or 'error'
                    - 'error_message': Error message if status is 'error'

        Raises:
            ValueError: If email body is empty.
        """
        if not email_body or not email_body.strip():
            raise ValueError("Email body is empty. Please provide email text to classify.")

        # Lazy load models if not already loaded
        if self.model is None or self.feature_transformer is None:
            self._load_models()

        # Clean and vectorize (shared with predict_single_email)
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

        result = {
            'prediction': prediction_label,
            'confidence': confidence,
            'raw_prediction': int(prediction[0]),
            'explanation': {
                'status': 'unavailable',
                'word_contributions': [],
                'top_spam_words': [],
                'top_ham_words': [],
                'highlighted_html': '',
                'error_message': '',
            }
        }

        if explanation_enabled:
            try:
                self._init_explainer()
                if self._shap_explainer is None:
                    result['explanation']['error_message'] = (
                        'SHAP explainer could not be initialized. '
                        'The model may not support predictions with probability estimates.'
                    )
                    return result

                # Compute SHAP values for the spam class (index 0)
                shap_values = self._shap_explainer.shap_values(
                    features, nsamples=_SHAP_NSAMPLES
                )

                # shap_values shape for binary: (n_samples, n_features) or list of arrays
                if isinstance(shap_values, list):
                    raw_values = shap_values[0]  # spam class
                else:
                    raw_values = shap_values

                # Get word contributions
                spam_class_idx = 0
                word_contributions = self._get_word_contributions(raw_values, spam_class_idx)

                # Split into spam-pushing and ham-pushing
                spam_words = [c for c in word_contributions if c['class'] == 'spam'][:10]
                ham_words = [c for c in word_contributions if c['class'] == 'ham'][:10]

                # Generate highlighted HTML
                highlighted_html = self._highlight_text(cleaned_body, word_contributions)

                result['explanation'] = {
                    'status': 'available',
                    'word_contributions': word_contributions,
                    'top_spam_words': spam_words,
                    'top_ham_words': ham_words,
                    'highlighted_html': highlighted_html,
                    'error_message': '',
                }

                logger.info(
                    f"Explanation generated for {prediction_label}: "
                    f"{len(spam_words)} spam words, {len(ham_words)} ham words"
                )

            except ImportError:
                result['explanation']['status'] = 'error'
                result['explanation']['error_message'] = (
                    'SHAP library is not installed. Install it with: pip install shap'
                )
            except Exception as e:
                logger.error(f"SHAP explanation failed: {e}")
                result['explanation']['status'] = 'error'
                result['explanation']['error_message'] = f'Explanation failed: {str(e)}'

        return result

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
    ) -> pd.DataFrame:  # noqa: C901
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

