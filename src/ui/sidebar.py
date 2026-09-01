"""Sidebar UI components."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st


def render_sidebar(
    pipeline: Any,
    model_loaded: bool,
) -> tuple[bool, bool] -> None:
    """Render the sidebar and return user toggle states.

    Returns:
        (enable_explanation, enable_live) tuple.
    """
    with st.sidebar:
        # --- Theme Toggle ---
        st.header("🎨 Appearance")
        current_theme = st.session_state.theme
        theme_icon = "🌙" if current_theme == "light" else "☀️"
        theme_label = "Dark Mode" if current_theme == "light" else "Light Mode"

        def toggle_theme() -> None:
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

        st.button(
            f"{theme_icon} {theme_label}",
            on_click=toggle_theme,
            use_container_width=True,
            help="Switch between light and dark themes",
        )

        st.divider()

        # --- Model Info ---
        st.header("📊 Model Info")
        st.metric("Status", "✅ Loaded" if model_loaded else "❌ Not loaded")
        if model_loaded and pipeline.config.model_path:
            st.caption(f"Model: `{Path(pipeline.config.model_path).name}`")

        st.divider()

        # --- Explainability Toggle ---
        st.header("🧠 Explainability")
        enable_explanation = st.checkbox(
            "Show AI explanation",
            value=True,
            help="When enabled, SHAP analyzes each word's contribution to the prediction. "
            "This adds ~3-5 seconds per classification.",
        )
        st.caption(
            "Explanations highlight which words influenced the model's decision — "
            "great for understanding why an email was flagged."
        )

        st.divider()

        # --- Real-time Analysis Toggle ---
        st.header("⚡ Live Analysis")
        enable_live = st.checkbox(
            "Real-time typing analysis",
            value=True,
            help="Shows a live spam likelihood gauge while you type. "
            "Updates automatically as you edit the email text.",
        )
        st.caption(
            "The gauge updates whenever you interact with the text area. "
            "Full analysis with SHAP runs when you click **Classify**."
        )

        st.divider()

        # --- About ---
        st.header("ℹ️ About")
        st.markdown("""
This application uses a **TF-IDF Vectorizer** and trained **ML classifiers**
to detect spam emails with high accuracy.

**Supported features:**
- ✉️ Single email classification with AI explanation
- 📂 Batch MBOX / CSV / Excel file processing
- 🔗 URL analysis & suspicious link detection
- 🌓 Dark/Light theme
- ⚡ Real-time typing analysis
- 📊 Model comparison dashboard
- 📋 Persistent classification history
- 📄 Downloadable reports (HTML / CSV)
        """)

        st.divider()
        st.caption("Built using Streamlit, scikit-learn & SHAP")

    return enable_explanation, enable_live
