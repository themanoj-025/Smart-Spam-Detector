"""Model loading and auto-train logic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st


@st.cache_resource(show_spinner="Loading trained models...")
def _load_pipeline() -> Any:
    """Initialize and load the prediction pipeline (cached)."""
    from src.pipeline.prediction_pipeline import PredictionPipeline

    return PredictionPipeline(load_models=True)


def load_model() -> tuple[Any, bool, str]:
    """Load or auto-train the prediction pipeline.

    Returns:
        (pipeline, model_loaded, model_name) tuple.
        If loading fails and training is rejected, calls ``st.stop()``.
    """
    try:
        pipeline = _load_pipeline()
        model_name = Path(pipeline.config.model_path).name if pipeline.config.model_path else "Unknown"
        return pipeline, True, model_name

    except FileNotFoundError:
        st.warning("⚠️ No trained models found. Training is required before the app can work.")

        if st.button("🚀 Train Models Now", type="primary", use_container_width=True):
            with st.spinner("🔄 Training models (this may take several minutes on first deploy)..."):
                try:
                    from src.pipeline.training_pipeline import TrainingPipeline

                    tp = TrainingPipeline()
                    tp.run_pipeline()
                    st.success("✅ Models trained successfully! Reloading...")
                    st.cache_resource.clear()
                    st.rerun()
                except (RuntimeError, OSError, ValueError) as train_err:
                    st.error(f"⚠️ Training failed: {train_err!s}")
                    st.stop()

        st.info(
            "💡 Click the button above to train models. "
            "This is only needed on the first deployment or when models are missing."
        )
        st.stop()

    except (RuntimeError, OSError, ValueError) as e:
        st.error(
            f"⚠️ Unexpected error loading models: {e!s}\n\n"
            "If you just deployed, try clicking **Rerun** from the upper-right menu. "
            "If the error persists, check the Streamlit Cloud logs for details."
        )
        st.stop()

    # Unreachable but satisfies type checker
    return None, False, "Unknown"  # pragma: no cover
