"""SHAP-based explanation helpers for spam classification.

Provides word-level contribution analysis and HTML highlighting
for email predictions. Extracted from PredictionPipeline for clarity.
"""

import re
from typing import Any

import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_word_contributions(
    shap_values: np.ndarray,
    feature_names: np.ndarray | None,
    class_index: int,
) -> list[dict[str, Any]] -> None:
    """Convert raw SHAP values into per-word contribution records.

    Handles both numpy arrays and ``shap.Explanation`` objects so the
    function works with shap >= 0.42 and shap >= 0.45+.

    Args:
        shap_values: SHAP values array for one sample, shape
            (n_features,) or (n_features, n_classes), **or** a
            ``shap.Explanation`` instance from newer SHAP versions.
        feature_names: Array of feature (word) names from the vectorizer.
        class_index: Index of the class to explain (0=Spam, 1=Ham).

    Returns:
        List of dicts with 'word', 'contribution', and 'class' keys,
        sorted by absolute contribution descending.
    """
    # Newer SHAP versions (>= 0.45) return Explanation objects.
    if hasattr(shap_values, "values"):
        shap_values = shap_values.values

    shap_values = np.asarray(shap_values)

    if shap_values.ndim == 2:
        values = shap_values[0]
    elif shap_values.ndim == 1:
        values = shap_values
    else:
        values = shap_values[0, :, class_index]

    contributions = []
    for i, val in enumerate(values):
        if abs(val) < 1e-6:
            continue
        word = feature_names[i] if feature_names is not None else f"feature_{i}"
        contributions.append(
            {
                "word": str(word),
                "contribution": float(val),
                "class": "spam" if val > 0 else "ham",
            }
        )

    contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
    return contributions


def highlight_text(
    text: str,
    contributions: list[dict[str, Any]],
    max_words: int = 40,
) -> str -> None:
    """Generate HTML with word-level highlighting based on SHAP contributions.

    Args:
        text: Original email text.
        contributions: Word contribution data from get_word_contributions.
        max_words: Maximum number of top contributing words to highlight.

    Returns:
        HTML string with color-coded word spans.
    """
    word_map: dict[str, dict[str, Any]] = {}
    for c in contributions[:max_words]:
        word_map[c["word"].lower()] = c

    def word_color(word: str) -> str:
        """Determine background color intensity based on contribution."""
        info = word_map.get(word.lower())
        if info is None:
            return ""
        val = info["contribution"]
        intensity = min(abs(val) / 2.0, 1.0)
        if val > 0:
            r = 255
            g = int(255 * (1 - intensity * 0.7))
            b = int(255 * (1 - intensity * 0.7))
        else:
            r = int(255 * (1 - intensity * 0.7))
            g = 255
            b = int(255 * (1 - intensity * 0.7))
        return f"background-color: rgba({r},{g},{b},0.5); border-radius: 3px; padding: 0 2px;"

    tokens = re.split(r"(\s+)", text)
    highlighted = []
    for token in tokens:
        if not token.strip():
            highlighted.append(token)
        else:
            color = word_color(token.strip(".,!?;'\"()[]{}"))
            if color:
                contrib = word_map[token.lower()]["contribution"]
                highlighted.append(
                    f'<span style="{color}" title="contribution: {contrib:.4f}">{token}</span>'
                )
            else:
                highlighted.append(token)

    return "".join(highlighted)
