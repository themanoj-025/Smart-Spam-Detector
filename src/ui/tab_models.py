"""Tab 3: Model comparison dashboard."""

from __future__ import annotations

import json
import os

import streamlit as st

from src.utils.model_comparison import ModelComparison

try:
    import plotly.express as px
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    go = None
    px = None


def render_model_comparison() -> None:
    """Render the model comparison dashboard tab."""
"""Tab 3: Model comparison dashboard."""




# Try to load Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    go = None
    px = None

st.header("📊 Model Performance Comparison")

st.markdown(
    "Compare all trained models side-by-side with radar charts, "
    "confusion matrices, and detailed performance metrics."
)

@st.cache_resource(show_spinner="Loading model comparison data...")
def get_model_comparison() -> None:
    mc = ModelComparison()

    loaded = mc.load()

    return mc, loaded

mc, comparison_loaded = get_model_comparison()

if not comparison_loaded:
    st.info(
        f"🚫 {mc.error_message or 'No trained models found.'}\n\n"
        "Train the models first, then return here to see the comparison dashboard.",
        icon="🤖",
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🚀 Train Models Now", type="primary", use_container_width=True):
            with st.spinner("🔄 Training all models (this may take a few minutes)..."):
                from src.pipeline.training_pipeline import TrainingPipeline

                tp = TrainingPipeline()

                state = tp.run_pipeline()

                st.success(
                    f"✅ Training complete! Best model: **{state.best_model_name}** "
                    f"(F1: {state.model_metrics[state.best_model_name]['f1_score']:.4f})"
                )

                st.cache_resource.clear()

                st.rerun()

else:
    if not HAS_PLOTLY:
        st.warning("⚠️ Plotly is required for charts. Install with: `pip install plotly`")

        st.stop()

    st.subheader("📈 Overall Summary")

    df = mc.get_comparison_df()

    best_row = (
        df[df["Best"] == "⭐"].iloc[0] if not df.empty and "⭐" in df["Best"].values else None
    )

    if best_row is not None:
        cols = st.columns(4)

        cols[0].metric("🏆 Best Model", best_row["Model"])

        cols[1].metric("🎯 Accuracy", f"{best_row['Accuracy'] * 100:.2f}%")

        cols[2].metric("📐 Precision", f"{best_row['Precision'] * 100:.2f}%")

        cols[3].metric("📊 F1-Score", f"{best_row['F1-Score'] * 100:.2f}%")

    else:
        st.caption("No best model selected yet.")

    st.subheader("🕸️ Radar Chart — Metrics Comparison")

    radar_fig = mc.get_radar_chart()

    if radar_fig:
        text_color = "#e8eaed" if st.session_state.theme == "dark" else "#1a1a2e"

        radar_fig.update_layout(
            font={"color": text_color},
            polar={
                "radialaxis": {
                    "gridcolor": "#444" if st.session_state.theme == "dark" else "#e0e0e0"
                },
                "angularaxis": {
                    "gridcolor": "#444" if st.session_state.theme == "dark" else "#e0e0e0"
                },
            },
        )

        st.plotly_chart(radar_fig, use_container_width=True)

    else:
        st.caption("Radar chart not available.")

    st.subheader("🏅 Model Rankings")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Model": st.column_config.TextColumn("Model", width="medium"),
            "Accuracy": st.column_config.NumberColumn("Accuracy", format="%.2f%%"),
            "Precision": st.column_config.NumberColumn("Precision", format="%.2f%%"),
            "Recall": st.column_config.NumberColumn("Recall", format="%.2f%%"),
            "F1-Score": st.column_config.NumberColumn("F1-Score", format="%.2f%%"),
            "Best": st.column_config.TextColumn(" ", width="small"),
        },
    )

    st.subheader("🔢 Confusion Matrices")

    st.markdown(
        "Each cell shows **count** and **percentage** (by row). "
        "Rows = true labels, columns = predictions."
    )

    cm_figs = mc.get_all_confusion_matrices()

    if cm_figs:
        cm_names = list(cm_figs.keys())

        cm_chunks = [cm_names[i : i + 3] for i in range(0, len(cm_names), 3)]

        for chunk in cm_chunks:
            cols = st.columns(len(chunk))

            for col, name in zip(cols, chunk):
                with col:
                    fig = cm_figs[name]

                    if fig:
                        text_color = (
                            "#e8eaed" if st.session_state.theme == "dark" else "#1a1a2e"
                        )

                        fig.update_layout(
                            font={"color": text_color},
                            title={
                                "text": ("⭐ " if name == mc.best_model_name else "") + name,
                                "font": {"size": 13},
                            },
                        )

                        st.plotly_chart(fig, use_container_width=True)

    else:
        st.caption("Confusion matrices not available. Train models to generate them.")

    with st.expander("📁 Training Run Details"):
        if mc.run_dir:
            st.markdown(f"**Run directory:** `{mc.run_dir}`")

            meta_path = os.path.join(mc.run_dir, "observations", "model_metadata.json")

            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    meta = json.load(f)

                st.json(meta)

            else:
                st.code(
                    "\n".join(os.listdir(os.path.join(mc.run_dir, "models")))
                    if os.path.exists(os.path.join(mc.run_dir, "models"))
                    else "No model files found."
                )

        else:
            st.caption("No run directory discovered.")

    st.divider()

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_resource.clear()

        st.rerun()




