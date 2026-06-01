"""Utility functions for the Spam Email Classification system."""

import os
import json
import pickle
from pathlib import Path
from typing import Any, Dict
import pandas as pd
import numpy as np


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


def save_pickle(obj: Any, filepath: str) -> str:
    """Save an object to a pickle file.

    Args:
        obj: Object to serialize.
        filepath: Path where to save the pickle file.

    Returns:
        The path where the file was saved.
    """
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)
    return filepath


def load_pickle(filepath: str) -> Any:
    """Load an object from a pickle file.

    Args:
        filepath: Path to the pickle file.

    Returns:
        The deserialized object.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Pickle file not found: {filepath}")
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def save_metadata(metadata: Dict[str, Any], filepath: str) -> None:
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

    with open(filepath, 'w', encoding='utf-8') as f:
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
            f"Dataset missing required columns: {missing}. "
            f"Available columns: {df.columns.tolist()}"
        )
    return True


def get_dataset_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Get summary statistics for a dataset.

    Args:
        df: DataFrame to analyze.

    Returns:
        Dictionary with dataset statistics.
    """
    stats = {
        'total_samples': len(df),
        'columns': df.columns.tolist(),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'missing_values': df.isnull().sum().to_dict(),
        'missing_pct': (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
    }

    # Include value counts for categorical columns
    for col in df.select_dtypes(include=['object']).columns:
        stats[f'{col}_value_counts'] = df[col].value_counts().to_dict()

    return stats
