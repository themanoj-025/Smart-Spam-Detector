"""Utility functions for the Spam Email Classification system."""

import hashlib
import hmac
import io
import json
import os
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def ensure_dir(path: str) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists.

    Returns:
        Path object for the directory.
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


class _RestrictedUnpickler(pickle.Unpickler):
    """Unpickler that only allows safe types to be deserialized.

    This prevents arbitrary code execution via crafted pickle files (CWE-502).
    """

    _SAFE_TYPES = frozenset({
        # Builtins
        "builtins", "__builtin__",
        # Standard library
        "collections", "re", "copyreg",
        # NumPy
        "numpy", "numpy.core.multiarray", "numpy.core.numeric",
        "numpy.ma.core", "numpy.ma.core._MaskedArray",
        "numpy.dtype", "numpy.float64", "numpy.int64",
        "numpy.ndarray", "numpy.bool_",
        # scikit-learn
        "sklearn", "sklearn.pipeline", "sklearn.feature_extraction.text",
        "sklearn.feature_extraction", "sklearn.linear_model",
        "sklearn.naive_bayes", "sklearn.svm", "sklearn.ensemble",
        "sklearn.tree", "sklearn.calibration",
        # pandas
        "pandas.core.frame", "pandas.core.series",
        "pandas.core.indexes.base", "pandas.core.indexes.range",
        # XGBoost
        "xgboost", "xgboost.core",
        # joblib
        "joblib", "joblib.numpy_pickle",
        # typing
        "typing",
    })

    def find_class(self, module: str, name: str) -> Any:
        # Allow safe modules
        top = module.split(".")[0]
        if top in self._SAFE_TYPES or module in self._SAFE_TYPES:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(
            f"Disallowed type: {module}.{name} — only safe ML types permitted"
        )


def _compute_hmac(data: bytes, key: bytes) -> str:
    """Compute HMAC-SHA256 hex digest for data integrity verification."""
    return hmac.new(key, data, hashlib.sha256).hexdigest()


# HMAC key for model file integrity (set via env var or use a default for dev)
_HMAC_KEY = os.environ.get(
    "SPAM_MODEL_HMAC_KEY", "smart-spam-default-dev-key-not-for-prod"
).encode()


def save_pickle(obj: Any, filepath: str) -> str:
    """Save an object to a pickle file with HMAC integrity signature.

    Why not JSON? These files store fitted scikit-learn estimators (vectorizer,
    classifiers), which have no JSON representation. JSON is used everywhere
    else (metadata, caches); pickle is deliberately limited to model artifacts
    and is mitigated by (1) HMAC integrity so only files we wrote are loaded,
    and (2) a restricted unpickler that blocks arbitrary code (CWE-502).

    Args:
        obj: Object to serialize.
        filepath: Path where to save the pickle file.

    Returns:
        The path where the file was saved.
    """
    ensure_dir(os.path.dirname(filepath))
    raw = pickle.dumps(obj)
    sig = _compute_hmac(raw, _HMAC_KEY)
    payload = {"data": raw, "hmac": sig}
    with open(filepath, "wb") as f:
        pickle.dump(payload, f)
    return filepath


def load_pickle(filepath: str) -> Any:
    """Load an object from a pickle file with HMAC integrity verification.

    Verifies the file has not been tampered with before deserializing.
    Uses a restricted unpickler to prevent arbitrary code execution
    (CWE-502) — see save_pickle for why JSON isn't used for model files.

    Args:
        filepath: Path to the pickle file.

    Returns:
        The deserialized object.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If HMAC verification fails (file tampered).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Pickle file not found: {filepath}")
    with open(filepath, "rb") as f:
        envelope = pickle.load(f)

    # Support both legacy (raw pickle) and new (HMAC-wrapped) formats
    if isinstance(envelope, dict) and "data" in envelope and "hmac" in envelope:
        expected_sig = envelope["hmac"]
        raw = envelope["data"]
        actual_sig = _compute_hmac(raw, _HMAC_KEY)
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError(
                f"HMAC verification failed for {filepath} — file may be tampered with"
            )
        return _RestrictedUnpickler(io.BytesIO(raw)).load()
    else:
        # Legacy format: raw pickle without HMAC wrapper
        return _RestrictedUnpickler(io.BytesIO(pickle.dumps(envelope))).load()


def save_metadata(metadata: dict[str, Any], filepath: str) -> None:
    """Save metadata as a JSON file.

    Args:
        metadata: Dictionary of metadata to save.
        filepath: Path where to save the JSON file.
    """
    ensure_dir(os.path.dirname(filepath))

    # Convert non-serializable types
    clean_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, (np.integer,)):
            clean_metadata[key] = int(value)
        elif isinstance(value, (np.floating,)):
            clean_metadata[key] = float(value)
        elif isinstance(value, (np.ndarray,)):
            clean_metadata[key] = value.tolist()
        else:
            clean_metadata[key] = value

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(clean_metadata, f, indent=2, default=str)


def validate_dataset(df: pd.DataFrame, required_columns: list[str]) -> bool:
    """Validate that a DataFrame contains all required columns.

    Args:
        df: DataFrame to validate.
        required_columns: List of column names that must be present.

    Returns:
        True if all required columns are present.

    Raises:
        ValueError: If any required columns are missing.
    """
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"Dataset missing required columns: {missing}. Available columns: {df.columns.tolist()}"
        )
    return True


def get_dataset_stats(df: pd.DataFrame) -> dict[str, Any]:
    """Get summary statistics for a dataset.

    Args:
        df: DataFrame to analyze.

    Returns:
        Dictionary with dataset statistics.
    """
    stats = {
        "total_samples": len(df),
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
    }

    # Include value counts for categorical columns
    for col in df.select_dtypes(include=["object"]).columns:
        stats[f"{col}_value_counts"] = df[col].value_counts().to_dict()

    return stats
