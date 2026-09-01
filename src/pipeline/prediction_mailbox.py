"""MBOX file processing helpers for batch email classification.

Provides mailbox loading, email extraction, and batch prediction
utilities. Extracted from PredictionPipeline for clarity.
"""

import mailbox
import time
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.email_utils import all_recipients, clean_text, extract_body
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_mailbox_file(mailbox_path: str) -> mailbox.mbox:
    """Load an MBOX file for batch processing.

    Args:
        mailbox_path: Path to the MBOX file.

    Returns:
        Loaded mailbox object.

    Raises:
        FileNotFoundError: If the MBOX file does not exist.
    """
    if not Path(mailbox_path).exists():
        raise FileNotFoundError(f"MBOX file not found: {mailbox_path}")

    logger.info(f"Loading mailbox: {mailbox_path}")
    mbox = mailbox.mbox(mailbox_path)
    logger.info(f"Loaded {len(mbox)} messages from mailbox")
    return mbox


def process_mailbox_messages(mbox: mailbox.mbox) -> list[dict[str, str]]:
    """Process all emails in a loaded MBOX and extract relevant fields.

    Args:
        mbox: Loaded mailbox object.

    Returns:
        List of dictionaries with email data (Time, Subject, Body, etc.).
    """
    logger.info("Processing mailbox messages...")
    data = []

    for i, message in enumerate(mbox):
        labels = (message.get("X-Gmail-Labels") or "").lower()
        category = (
            "Spam"
            if "spam" in labels
            else "Promotions"
            if "category_promotions" in labels
            else "Social"
            if "category_social" in labels
            else "Updates"
            if "category_updates" in labels
            else "Inbox"
        )

        data.append(
            {
                "Time": message.get("Date", ""),
                "Recipients": clean_text(all_recipients(message)),
                "Subject": clean_text(message.get("Subject", "")),
                "Body": clean_text(extract_body(message)),
                "Category": category,
                "Direction": "Sent" if "Sent" in labels else "Received",
            }
        )

        if (i + 1) % 100 == 0:
            logger.info(f"  Processed {i + 1}/{len(mbox)} messages...")

    logger.info(f"✓ Processed {len(data)} emails from mailbox")
    mbox.close()

    return data


def run_batch_prediction(
    mail_data: list[dict[str, str]],
    model: Any,
    feature_transformer: Any,
) -> list[dict[str, str]] -> None:
    """Run spam classification on a list of email data.

    Args:
        mail_data: List of email dictionaries with 'Body' field.
        model: Trained prediction model.
        feature_transformer: TF-IDF vectorizer.

    Returns:
        Updated list with 'Prediction' field added to each item.
    """
    start_time = time.time()
    logger.info(f"Running predictions on {len(mail_data)} emails...")

    for mail in mail_data:
        body_text = mail.get("Body", "")
        if body_text:
            features = feature_transformer.transform([body_text])
            prediction = model.predict(features)
            mail["Prediction"] = "Spam" if str(prediction[0]) == "0" else "Ham"
        else:
            mail["Prediction"] = "Unknown"

    elapsed = time.time() - start_time
    spam_count = sum(1 for m in mail_data if m.get("Prediction") == "Spam")
    logger.info(
        f"✓ Predictions completed in {elapsed:.2f}s ({len(mail_data) / elapsed:.0f} emails/sec)"
    )
    logger.info(f"  Spam: {spam_count} | Ham: {len(mail_data) - spam_count}")

    return mail_data


def predict_mbox_file(
    mailbox_path: str,
    model: Any,
    feature_transformer: Any,
    output_path: str | None = None,
) -> pd.DataFrame -> None:
    """Complete pipeline: load MBOX, process emails, run predictions.

    Args:
        mailbox_path: Path to the MBOX file.
        model: Trained prediction model.
        feature_transformer: TF-IDF vectorizer.
        output_path: Optional path to save results as CSV.

    Returns:
        DataFrame with all email data and predictions.
    """
    mbox = load_mailbox_file(mailbox_path)
    mail_data = process_mailbox_messages(mbox)
    mail_data = run_batch_prediction(mail_data, model, feature_transformer)
    df = pd.DataFrame(mail_data)

    if output_path:
        df.to_csv(output_path, index=False)
        logger.info(f"Predictions saved to {output_path}")

    return df
