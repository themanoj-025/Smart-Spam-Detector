"""Spam Email Classifier - Streamlit Web Application

A production-grade machine learning system for classifying emails as Spam or Ham.
Features include single email classification, MBOX batch processing,
SHAP-based explainable AI, dark/light theme, and real-time typing analysis.
"""

import os
import json
import time
import tempfile
from pathlib import Path

import streamlit as st
import pandas as pd

from src.pipeline.prediction_pipeline import PredictionPipeline
from src.utils.email_utils import clean_text
from src.utils.model_comparison import ModelComparison
from src.utils.history_manager import HistoryManager
from src.utils.url_analyzer import analyze_urls_in_text, get_url_risk_badge
from src.utils.report_generator import generate_classification_report, generate_email_report

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Spam Email Classifier",
    page_icon="📧",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme State
# ---------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "email_text" not in st.session_state:
    st.session_state.email_text = ""

# Initialize history manager (singleton via cache)
_history_manager = None

@st.cache_resource(show_spinner=False)
def get_history_manager():
    return HistoryManager()

# ---------------------------------------------------------------------------
# Comprehensive Theme CSS
# ---------------------------------------------------------------------------
THEME_CSS = """
<style>
    /* ================================================================
       CSS Variables — Light & Dark Themes
       ================================================================ */
    :root {
        /* Core backgrounds */
        --app-bg: #f8f9fa;
        --card-bg: #ffffff;
        --card-border: #e0e0e0;
        --card-shadow: 0 2px 12px rgba(0,0,0,0.06);

        /* Text */
        --text-primary: #1a1a2e;
        --text-secondary: #555555;
        --text-muted: #9e9e9e;

        /* Sidebar */
        --sidebar-bg: #f0f2f6;
        --sidebar-text: #1a1a2e;

        /* Accents */
        --accent-red: #ef5350;
        --accent-red-light: #ffebee;
        --accent-green: #66bb6a;
        --accent-green-light: #e8f5e9;
        --accent-yellow: #ffa726;

        /* Input */
        --input-bg: #ffffff;
        --input-border: #d0d0d0;
        --input-focus-border: #4a90d9;

        /* Dividers */
        --divider-color: #e8e8e8;

        /* Explanation box */
        --explanation-bg: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        --explanation-border: #e0e0e0;

        /* Metric backgrounds */
        --metric-bg: #f5f5f5;

        /* Bar track */
        --bar-track: #f0f0f0;

        /* Theme-aware accent text colors */
        --spam-text: #c62828;
        --ham-text: #2e7d32;
        --spam-title: #c62828;
        --ham-title: #2e7d32;

    /* Transition timing */
    --theme-transition: 0.35s ease;

    /* Gauge */
    --gauge-bg: #e0e0e0;
    }

    /* ================================================================
       Base Styles with Theme Transitions
       ================================================================ */
    .stApp {
        background-color: var(--app-bg) !important;
        color: var(--text-primary);
        transition: background-color var(--theme-transition), color var(--theme-transition);
    }

    .main-header {
        text-align: center;
        padding: 1.5rem 1rem;
        color: var(--text-primary);
        transition: color var(--theme-transition);
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4a90d9, #7c5ce0, #e84393);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
    }
    .main-header p {
        color: var(--text-secondary);
        font-size: 1.05rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 0.6rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em;
        transition: background-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.18);
    }
    .stButton > button:active {
        transform: translateY(0px);
    }

    /* ================================================================
       Prediction Box
       ================================================================ */
    .prediction-box {
        padding: 1.8rem 2rem;
        border-radius: 1rem;
        margin: 1.2rem 0;
        animation: fadeIn 0.5s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: background-color var(--theme-transition), border-color var(--theme-transition), box-shadow var(--theme-transition);
    }
    .spam-box {
        background: linear-gradient(135deg, var(--accent-red-light), #fff0f0);
        border-left: 5px solid var(--accent-red);
    }
    .ham-box {
        background: linear-gradient(135deg, var(--accent-green-light), #f0fff0);
        border-left: 5px solid var(--accent-green);
    }

    .metric-card {
        background-color: var(--metric-bg);
        padding: 1.2rem;
        border-radius: 0.75rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: background-color var(--theme-transition), box-shadow var(--theme-transition);
    }
    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    /* ================================================================
       Gauge — Animated Circular Confidence
       ================================================================ */
    .gauge-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 1.5rem 0;
        padding: 1rem;
        background: var(--card-bg);
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        transition: background-color var(--theme-transition), box-shadow var(--theme-transition);
    }
    .gauge-svg {
        width: 160px;
        height: 90px;
        overflow: visible;
    }
    .gauge-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-top: 0.3rem;
        font-weight: 500;
        transition: color var(--theme-transition);
    }
    .gauge-value {
        font-size: 0.75rem;
        color: var(--text-muted);
        transition: color var(--theme-transition);
    }

    /* ================================================================
       Real-time Analysis Status
       ================================================================ */
    .live-status {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-bottom: 8px;
        transition: background-color var(--theme-transition), color var(--theme-transition);
    }
    .live-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        animation: pulse-dot 1.5s ease-in-out infinite;
    }
    .live-dot.spam { background-color: var(--accent-red); }
    .live-dot.ham { background-color: var(--accent-green); }
    .live-dot.idle { background-color: var(--text-muted); animation: none; }

    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.85); }
    }

    /* ================================================================
       Explanation Section
       ================================================================ */
    .explanation-section {
        background: var(--explanation-bg);
        border: 1px solid var(--explanation-border);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        animation: slideUp 0.45s ease;
        transition: background var(--theme-transition), border-color var(--theme-transition), box-shadow var(--theme-transition);
    }
    .explanation-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: var(--text-primary);
        transition: color var(--theme-transition);
    }
    .word-bar-container {
        display: flex;
        align-items: center;
        margin: 4px 0;
        gap: 8px;
    }
    .word-label {
        min-width: 70px;
        font-size: 0.85rem;
        font-weight: 500;
        text-align: right;
        padding-right: 8px;
    }
    .bar-track {
        flex: 1;
        height: 22px;
        background-color: var(--bar-track);
        border-radius: 11px;
        overflow: hidden;
        position: relative;
        transition: background-color var(--theme-transition);
    }
    .bar-fill {
        height: 100%;
        border-radius: 11px;
        transition: width 0.6s ease;
    }
    .bar-fill.spam-bar {
        background: linear-gradient(90deg, #ffcdd2, var(--accent-red));
        float: right;
    }
    .bar-fill.ham-bar {
        background: linear-gradient(90deg, var(--accent-green), #a5d6a7);
    }
    .bar-value {
        min-width: 45px;
        font-size: 0.8rem;
        color: var(--text-muted);
        text-align: left;
        font-family: monospace;
        transition: color var(--theme-transition);
    }

    .highlight-box {
        background-color: var(--input-bg);
        border: 1px solid var(--divider-color);
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.95rem;
        line-height: 1.8;
        max-height: 200px;
        overflow-y: auto;
        transition: background-color var(--theme-transition), border-color var(--theme-transition);
    }

    .explanation-footer {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.8rem;
        text-align: center;
        transition: color var(--theme-transition);
    }

    /* ================================================================
       Reusable Animations
       ================================================================ */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes gaugeFill {
        from { stroke-dashoffset: 251; }
        to   { stroke-dashoffset: var(--gauge-offset); }
    }

    /* ================================================================
       Sidebar
       ================================================================ */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        transition: background-color var(--theme-transition);
    }
    section[data-testid="stSidebar"] * {
        color: var(--sidebar-text) !important;
        transition: color var(--theme-transition);
    }

    /* ================================================================
       Text Area
       ================================================================ */
    .stTextArea textarea {
        background-color: var(--input-bg) !important;
        color: var(--text-primary) !important;
        border-color: var(--input-border) !important;
        border-radius: 8px !important;
        transition: background-color var(--theme-transition),
                    color var(--theme-transition),
                    border-color var(--theme-transition);
    }
    .stTextArea textarea:focus {
        border-color: var(--input-focus-border) !important;
        box-shadow: 0 0 0 2px rgba(91, 141, 239, 0.2) !important;
    }

    /* ================================================================
       Dividers & Footer
       ================================================================ */
    hr {
        border-color: var(--divider-color) !important;
        transition: border-color var(--theme-transition);
    }

    footer {
        text-align: center;
        color: var(--text-muted) !important;
        font-size: 0.8rem;
        padding: 2rem 0;
        transition: color var(--theme-transition);
    }

    /* ================================================================
       Tabs
       ================================================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom-color: var(--divider-color) !important;
        transition: border-color var(--theme-transition);
    }
    .stTabs [data-baseweb="tab"] {
        transition: color var(--theme-transition);
        border-radius: 8px 8px 0 0;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--card-bg) !important;
        border-bottom: 3px solid var(--input-focus-border);
        transition: background-color var(--theme-transition);
    }

    /* ================================================================
       DataFrames
       ================================================================ */
    .stDataFrame {
        transition: background-color var(--theme-transition);
    }
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background-color: var(--card-bg) !important;
        color: var(--text-primary) !important;
        transition: background-color var(--theme-transition), color var(--theme-transition);
    }

    /* ================================================================
       Expander
       ================================================================ */
    .stExpander {
        border: none !important;
        box-shadow: none !important;
    }
    .stExpander details {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        transition: background-color var(--theme-transition), border-color var(--theme-transition);
    }
</style>
"""

# ---------------------------------------------------------------------------
# Import Plotly (for dashboard charts)
# ---------------------------------------------------------------------------
try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    go = None
    px = None

# ---------------------------------------------------------------------------
# Inject theme CSS + apply active theme
# ---------------------------------------------------------------------------
st.markdown(THEME_CSS, unsafe_allow_html=True)

# Apply dark theme variables directly onto .stApp and Streamlit components.
# This is needed because injected markdown lives INSIDE .stApp, so CSS
# variables set on a wrapper div won't cascade to ancestor elements.
# By targeting .stApp directly, the variables cascade DOWN to all children.
if st.session_state.theme == "dark":
    st.markdown(
        """<style>
        .stApp {
            --app-bg: #0e1117 !important;
            --card-bg: #1a1d27 !important;
            --card-border: #2e3140 !important;
            --card-shadow: 0 2px 12px rgba(0,0,0,0.3) !important;
            --text-primary: #e8eaed !important;
            --text-secondary: #b0b3b8 !important;
            --text-muted: #6b6f78 !important;
            --sidebar-bg: #131620 !important;
            --sidebar-text: #e8eaed !important;
            --accent-red: #f44336 !important;
            --accent-red-light: #2d1418 !important;
            --accent-green: #4caf50 !important;
            --accent-green-light: #142818 !important;
            --input-bg: #1a1d27 !important;
            --input-border: #3a3d4a !important;
            --input-focus-border: #5b8def !important;
            --divider-color: #2e3140 !important;
            --explanation-bg: linear-gradient(135deg, #1a1d27 0%, #222536 100%) !important;
            --explanation-border: #2e3140 !important;
            --metric-bg: #222536 !important;
            --bar-track: #2a2d3a !important;
            --gauge-bg: #2a2d3a !important;
            --spam-text: #ef9a9a !important;
            --ham-text: #81c784 !important;
            --spam-title: #ef5350 !important;
            --ham-title: #66bb6a !important;
        }
        </style>""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Model Loading
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading trained models...")
def get_pipeline():
    """Initialize and load the prediction pipeline (cached)."""
    return PredictionPipeline(load_models=True)


# Try to load models; auto-train if not found (needed for Streamlit Cloud)
try:
    pipeline = get_pipeline()
    model_loaded = True
    model_name = Path(pipeline.config.model_path).name if pipeline.config.model_path else "Unknown"
except FileNotFoundError:
    # No trained models found — offer to train automatically
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
            except Exception as train_err:
                st.error(f"⚠️ Training failed: {str(train_err)}")
                st.stop()
    st.info(
        "💡 Click the button above to train models. "
        "This is only needed on the first deployment or when models are missing."
    )
    st.stop()
except Exception as e:
    st.error(
        f"⚠️ Unexpected error loading models: {str(e)}\n\n"
        "If you just deployed, try clicking **Rerun** from the upper-right menu. "
        "If the error persists, check the Streamlit Cloud logs for details."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown("<h1>📧 Spam Email Classifier</h1>", unsafe_allow_html=True)
st.markdown(
    "Classify emails as **Spam** 🚨 or **Ham** ✅ (Safe) using "
    "Machine Learning with **scikit-learn** & **SHAP** explainability."
)
st.markdown(
    "<div style='margin-top:0.5rem;'><a href='https://smart-spam-detector.streamlit.app' target='_blank' style='color:var(--input-focus-border);font-weight:600;text-decoration:none;'>🌐 Live App: smart-spam-detector.streamlit.app</a></div>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    # --- Theme Toggle ---
    st.header("🎨 Appearance")
    current_theme = st.session_state.theme
    theme_icon = "🌙" if current_theme == "light" else "☀️"
    theme_label = "Dark Mode" if current_theme == "light" else "Light Mode"

    def toggle_theme():
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
    st.caption("Built with ❤️ using Streamlit, scikit-learn & SHAP")

# ---------------------------------------------------------------------------
# Helper: Animated Circular Confidence Gauge (SVG)
# ---------------------------------------------------------------------------
def show_confidence_gauge(confidence: float, prediction: str, is_live: bool = False):
    """Render an animated circular gauge showing the spam confidence score.

    Uses an SVG semi-circle arc that fills proportionally and changes color
    from green (safe) through yellow (uncertain) to red (spam).

    Args:
        confidence: Confidence percentage (0-100).
        prediction: 'Spam' or 'Ham' for color theming.
        is_live: If True, show as a live-updating gauge (smaller, pulsing).
    """
    # Normalize: spam_probability goes 0-100
    # For spam predictions we show confidence directly; for ham we show 100-confidence as "spam risk"
    spam_risk = confidence if prediction == "Spam" else 100.0 - confidence
    spam_risk = max(0, min(100, spam_risk))  # Clamp

    # SVG arc parameters
    radius = 70 if not is_live else 55
    circumference = 2 * 3.14159 * radius  # ~439.8 for r=70
    # Arc: 0% = all empty (offset = circumference), 100% = all filled (offset = 0)
    arc_length = circumference * (spam_risk / 100)
    offset = circumference - arc_length

    # Color interpolation: green (#4caf50) -> yellow (#ffa726) -> red (#f44336)
    if spam_risk < 50:
        ratio = spam_risk / 50
        r = int(76 + (255 - 76) * ratio)     # 76 -> 255
        g = int(175 + (167 - 175) * ratio)    # 175 -> 167
        b = int(80 + (38 - 80) * ratio)       # 80 -> 38
    else:
        ratio = (spam_risk - 50) / 50
        r = int(255 + (244 - 255) * ratio)    # 255 -> 244
        g = int(167 + (67 - 167) * ratio)     # 167 -> 67
        b = int(38 + (54 - 38) * ratio)       # 38 -> 54

    color = f"rgb({r},{g},{b})"
    size = 180 if not is_live else 140

    # Determine status text
    if spam_risk < 30:
        status_text = "✅ Safe"
        dot_class = "ham"
    elif spam_risk < 60:
        status_text = "⚠️ Uncertain"
        dot_class = "idle"
    else:
        status_text = "🚨 Spam Risk"
        dot_class = "spam"

    gauge_html = f"""
    <div class="gauge-container">
        <svg class="gauge-svg" width="{size}" height="{size // 2 + 10}" viewBox="0 0 {size} {size // 2 + 10}">
            <!-- Background arc -->
            <path d="M 10 {size // 2 + 5}
                     A {(size - 20) / 2} {(size - 20) / 2} 0 0 1 {size - 10} {size // 2 + 5}"
                  fill="none"
                  stroke="var(--gauge-bg)"
                  stroke-width="{12 if not is_live else 10}"
                  stroke-linecap="round" />
            <!-- Foreground arc (animated) -->
            <path d="M 10 {size // 2 + 5}
                     A {(size - 20) / 2} {(size - 20) / 2} 0 0 1 {size - 10} {size // 2 + 5}"
                  fill="none"
                  stroke="{color}"
                  stroke-width="{12 if not is_live else 10}"
                  stroke-linecap="round"
                  stroke-dasharray="{circumference}"
                  stroke-dashoffset="{offset}"
                  style="transition: stroke-dashoffset 0.6s ease, stroke 0.4s ease;" />
            <!-- Value text -->
            <text x="{size / 2}" y="{size // 2 - 8 if not is_live else size // 2 - 12}"
                  text-anchor="middle"
                  fill="var(--text-primary)"
                  font-size="{28 if not is_live else 22}"
                  font-weight="700"
                  style="transition: fill var(--theme-transition);">
                {spam_risk:.0f}%
            </text>
            <text x="{size / 2}" y="{size // 2 + 12 if not is_live else size // 2 + 6}"
                  text-anchor="middle"
                  fill="var(--text-muted)"
                  font-size="{12 if not is_live else 10}"
                  style="transition: fill var(--theme-transition);">
                spam risk
            </text>
        </svg>
        <div class="live-status">
            <span class="live-dot {dot_class}"></span>
            <span>{status_text}</span>
        </div>
        <div class="gauge-label">
            {"Live Analysis" if is_live else f"Confidence: {confidence:.1f}% — {prediction}"}
        </div>
        <div class="gauge-value">
            {f"Updates as you type" if is_live else f"Spam probability: {spam_risk:.1f}%"}
        </div>
    </div>
    """

    st.markdown(gauge_html, unsafe_allow_html=True)


def show_confidence_bar(confidence: float, prediction: str):
    """Legacy horizontal confidence bar (used as secondary indicator)."""
    bar_color = "#ef5350" if prediction == "Spam" else "#66bb6a"
    st.markdown(f"""
    <div style="margin: 10px 0; animation: fadeIn 0.4s ease;">
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:4px;">
            <span style="color:var(--text-secondary);">Confidence</span>
            <span style="font-weight:600; color:var(--text-primary);">{confidence:.1f}%</span>
        </div>
        <div style="background-color: var(--bar-track); border-radius: 10px; height: 12px; overflow:hidden;">
            <div style="background: linear-gradient(90deg, {bar_color}88, {bar_color});
                        width: {confidence}%; height: 12px; border-radius: 10px;
                        transition: width 0.5s ease;">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper: Lightweight real-time analysis
# ---------------------------------------------------------------------------
def compute_live_prediction(text: str):
    """Run a lightweight prediction for real-time analysis (no SHAP).

    Args:
        text: The current email text.

    Returns:
        Tuple of (prediction_label, confidence, spam_risk) or (None, None, None).
    """
    if not text or not text.strip():
        return None, None, None

    try:
        cleaned = clean_text(text)
        features = pipeline.feature_transformer.transform([cleaned])
        pred = pipeline.model.predict(features)
        label = "Spam" if str(pred[0]) == "0" else "Ham"
        if hasattr(pipeline.model, "predict_proba"):
            proba = pipeline.model.predict_proba(features)
            conf = float(max(proba[0])) * 100
            spam_risk = float(proba[0][0]) * 100 if label == "Spam" else float(proba[0][1]) * 100
        else:
            conf = None
            spam_risk = 50.0 if label == "Spam" else 50.0
        return label, conf, spam_risk
    except Exception:
        return None, None, None


# ---------------------------------------------------------------------------
# Helper: Show explanation UI
# ---------------------------------------------------------------------------
def show_explanation(explanation: dict, prediction: str):
    """Render the SHAP explanation UI components."""
    status = explanation.get("status", "unavailable")
    if status == "error":
        st.warning(f"⚠️ {explanation.get('error_message', 'Explanation unavailable')}")
        return

    if status == "unavailable":
        st.info(
            "💡 Explanation unavailable for this model. Some models don't support "
            "per-word analysis in real time.",
            icon="🧠",
        )
        return

    st.markdown('<div class="explanation-section">', unsafe_allow_html=True)
    st.markdown(
        '<div class="explanation-title">🧠 Why this prediction?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Below are the words that most influenced the model's decision. "
        "**Red** bars push toward **Spam**, **green** bars push toward **Ham (Safe)**.",
    )

    top_spam = explanation.get("top_spam_words", [])
    top_ham = explanation.get("top_ham_words", [])

    spam_col, ham_col = st.columns(2)

    with spam_col:
        st.markdown("##### 🚨 Pushes toward Spam")
        if top_spam:
            max_val = max(abs(w["contribution"]) for w in top_spam) or 1
            for w in top_spam:
                pct = abs(w["contribution"]) / max_val * 100
                st.markdown(f"""
                <div class="word-bar-container">
                    <span class="word-label" style="color:var(--spam-text);">{w['word']}</span>
                    <div class="bar-track">
                        <div class="bar-fill spam-bar" style="width:{pct}%;"></div>
                    </div>
                    <span class="bar-value">{w['contribution']:+.3f}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No spam-indicative words found")

    with ham_col:
        st.markdown("##### ✅ Pushes toward Ham")
        if top_ham:
            max_val = max(abs(w["contribution"]) for w in top_ham) or 1
            for w in top_ham:
                pct = abs(w["contribution"]) / max_val * 100
                st.markdown(f"""
                <div class="word-bar-container">
                    <span class="word-label" style="color:var(--ham-text);">{w['word']}</span>
                    <div class="bar-track">
                        <div class="bar-fill ham-bar" style="width:{pct}%;"></div>
                    </div>
                    <span class="bar-value">{w['contribution']:+.3f}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No ham-indicative words found")

    highlighted_html = explanation.get("highlighted_html", "")
    if highlighted_html:
        st.markdown("##### 📝 Word-level Analysis")
        st.markdown(
            f'<div class="highlight-box">{highlighted_html}</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Words are colored by their contribution: "
            "🔴 red = pushes toward Spam, 🟢 green = pushes toward Ham. "
            "Hover to see exact contribution values."
        )

    st.markdown(
        '<div class="explanation-footer">'
        'Explanations are computed using <strong>SHAP</strong> '
        '(SHapley Additive exPlanations) — a game-theoretic approach '
        'to model interpretability.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main Content - Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Single Email", "📂 Batch Processing", "📊 Model Comparison", "📋 History"])

# --- Tab 1: Single Email Classification ---
with tab1:
    st.header("Check a Single Email")
    st.markdown(
        "Paste the email content below. The **live gauge** updates as you type — "
        "click **Classify** for a full analysis with SHAP explanation."
    )

    # Text input with callback for live analysis
    email_text = st.text_area(
        "Email Content",
        height=200,
        placeholder="Paste email content here... e.g., 'Dear friend, I have a business proposal...'",
        label_visibility="collapsed",
        key="email_input",
    )

    # Real-time typing analysis
    if enable_live and email_text and email_text.strip():
        live_label, live_conf, live_risk = compute_live_prediction(email_text)
        if live_label is not None:
            show_confidence_gauge(live_conf if live_conf else 50.0, live_label, is_live=True)

    # Action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        classify_clicked = st.button("🔍 Classify Email", type="primary", use_container_width=True)

    if classify_clicked:
        if email_text and email_text.strip():
            # Phase 1: Quick prediction
            with st.spinner("🤖 Analyzing email content..."):
                try:
                    result = pipeline.predict_single_email(email_text)
                    prediction = result["prediction"]
                    confidence = result.get("confidence")

                    # --- URL Analysis ---
                    url_analysis = analyze_urls_in_text(email_text)

                    # Save to history
                    hm = get_history_manager()
                    spam_risk_val = confidence if prediction == "Spam" else (100.0 - confidence) if confidence else None
                    hm.add_entry(
                        email_text=email_text,
                        prediction=prediction,
                        confidence=confidence,
                        spam_risk=spam_risk_val,
                        model_used=model_name,
                        source="manual",
                        url_count=url_analysis["total_urls"],
                        suspicious_urls=url_analysis["suspicious_count"],
                    )

                    # Display result with styling
                    if prediction == "Spam":
                        st.markdown(
                            """
                            <div class="prediction-box spam-box">
                                <h2 style="color: var(--spam-title); margin: 0; font-size: 1.8rem;">🚨 SPAM DETECTED</h2>
                                <p style="font-size: 1.1rem; margin: 0.5rem 0 0 0; color: var(--text-secondary);">
                                    This email is likely <strong>Spam</strong> — proceed with caution
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            """
                            <div class="prediction-box ham-box">
                                <h2 style="color: var(--ham-title); margin: 0; font-size: 1.8rem;">✅ SAFE — HAM</h2>
                                <p style="font-size: 1.1rem; margin: 0.5rem 0 0 0; color: var(--text-secondary);">
                                    This email appears to be <strong>Safe (Ham)</strong> — no threats detected
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if confidence:
                        # Show animated gauge AND confidence bar
                        show_confidence_gauge(confidence, prediction, is_live=False)
                        with st.expander("📊 Show confidence bar"):
                            show_confidence_bar(confidence, prediction)

                    # --- URL Analysis Section ---
                    if url_analysis["total_urls"] > 0:
                        with st.expander(f"🔗 URL Analysis — {url_analysis['total_urls']} URL(s) found, {url_analysis['suspicious_count']} suspicious", expanded=url_analysis["suspicious_count"] > 0):
                            risk_level = url_analysis["risk_level"]
                            risk_icon = {"low": "🟢", "medium": "🟡", "high": "🔴", "none": "⚪"}.get(risk_level, "⚪")
                            st.markdown(f"**{risk_icon} Overall URL Risk: {url_analysis['overall_risk_score']:.0f}% — {risk_level.upper()}**")
                            url_df = pd.DataFrame([
                                {"URL": u["url"][:80], "Host": u["hostname"], "Risk": f"{u['risk_score']:.0f}%", "Flags": ", ".join(u["flags"])}
                                for u in url_analysis["urls"]
                            ])
                            st.dataframe(url_df, use_container_width=True, hide_index=True)

                except Exception as e:
                    st.error(f"⚠️ Error analyzing email: {str(e)}")

            # Phase 2: Explanation (if enabled)
            if enable_explanation and confidence:
                with st.spinner("🧠 Computing word-level explanations (may take a moment)..."):
                    try:
                        result_ex = pipeline.predict_with_explanation(
                            email_text,
                            explanation_enabled=True,
                        )
                        explanation = result_ex.get("explanation", {})
                        show_explanation(explanation, prediction)
                    except Exception as e:
                        st.warning(f"⚠️ Explanation not available: {str(e)}")

            # --- Report Download ---
            if confidence:
                explanation_summary = None
                if enable_explanation and 'explanation' in locals() and isinstance(explanation, dict) and explanation.get('status') == 'available':
                    top_spam = explanation.get('top_spam_words', [])
                    if top_spam:
                        explanation_summary = f"Top spam word: {top_spam[0].get('word', 'N/A')} ({top_spam[0].get('contribution', 0):+.4f})"

                report_html = generate_email_report(
                    email_text=email_text,
                    prediction=prediction,
                    confidence=confidence,
                    spam_risk=spam_risk_val,
                    url_analysis=url_analysis if url_analysis["total_urls"] > 0 else None,
                    explanation_summary=explanation_summary,
                )
                st.download_button(
                    "📥 Download Report (HTML)",
                    data=report_html.encode("utf-8"),
                    file_name=f"email_report_{int(time.time())}.html",
                    mime="text/html",
                    use_container_width=True,
                )
        else:
            st.warning("⚠️ Please enter some text to classify.")

# --- Tab 2: Batch Processing (MBOX + CSV/Excel) ---
with tab2:
    st.header("Batch File Processing")
    st.markdown(
        "Upload email files for bulk classification. Supports "
        "**MBOX** files, **CSV** files, and **Excel (.xlsx)** files."
    )

    # File type selector
    upload_type = st.radio(
        "File type",
        ["MBOX / Text", "CSV / Excel"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if upload_type == "MBOX / Text":
        st.markdown(
            "Upload an MBOX file (exported from Gmail, Thunderbird, etc.) "
            "to classify all emails at once."
        )
        uploaded_file = st.file_uploader(
            "Choose an MBOX file",
            type=["mbox", "txt"],
            help="Upload an MBOX file exported from your email client",
            key="mbox_uploader",
        )

        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name} "
                       f"({uploaded_file.size / 1024:.1f} KB)")

            if st.button("🚀 Process File", type="primary", use_container_width=True, key="mbox_process"):
                with st.spinner("📂 Processing file... this may take a moment"):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mbox") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name

                        try:
                            df = pipeline.predict_mbox_file(tmp_path)

                            # Save to history
                            hm = get_history_manager()
                            for _, row in df.iterrows():
                                hm.add_entry(
                                    email_text=row.get("Body", ""),
                                    prediction=row.get("Prediction", "Unknown"),
                                    source="batch",
                                    email_subject=row.get("Subject", ""),
                                )

                            # Show summary metrics
                            st.subheader("📊 Processing Results")
                            col1, col2, col3 = st.columns(3)

                            spam_count = len(df[df["Prediction"] == "Spam"])
                            ham_count = len(df[df["Prediction"] == "Ham"])

                            col1.metric("Total Emails", len(df))
                            col2.metric(
                                "Spam Found",
                                spam_count,
                                delta=f"{spam_count/len(df)*100:.1f}%" if len(df) > 0 else "0%",
                                delta_color="inverse",
                            )
                            col3.metric(
                                "Ham (Safe)",
                                ham_count,
                                delta=f"{ham_count/len(df)*100:.1f}%" if len(df) > 0 else "0%",
                            )

                            # Show preview
                            st.subheader("📋 Results Preview")
                            preview_cols = ["Time", "Subject", "Prediction"]
                            available_cols = [c for c in preview_cols if c in df.columns]
                            st.dataframe(
                                df[available_cols].head(10),
                                use_container_width=True,
                                hide_index=True,
                            )

                            # Download CSV
                            csv = df.to_csv(index=False).encode("utf-8")
                            st.download_button(
                                label="📥 Download Full Results (CSV)",
                                data=csv,
                                file_name=f"spam_predictions_{int(time.time())}.csv",
                                mime="text/csv",
                                use_container_width=True,
                            )

                            # Download HTML Report
                            report_data = []
                            for _, row in df.iterrows():
                                report_data.append({
                                    "prediction": row.get("Prediction", "Unknown"),
                                    "email_subject": row.get("Subject", ""),
                                    "timestamp": time.time(),
                                    "source": "batch",
                                })
                            report_html = generate_classification_report(
                                report_data,
                                title=f"Batch Results — {uploaded_file.name}",
                            )
                            st.download_button(
                                "📄 Download Report (HTML)",
                                data=report_html.encode("utf-8"),
                                file_name=f"spam_report_{int(time.time())}.html",
                                mime="text/html",
                                use_container_width=True,
                            )

                        finally:
                            if os.path.exists(tmp_path):
                                try:
                                    os.unlink(tmp_path)
                                except PermissionError:
                                    pass

                    except Exception as e:
                        st.error(f"⚠️ Error processing file: {str(e)}")

    else:  # CSV / Excel
        st.markdown(
            "Upload a **CSV** or **Excel (.xlsx)** file containing email text. "
            "Auto-detects the email text column. Results will include all original columns plus the prediction."
        )

        spreadsheet_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "xlsx"],
            help="File should contain a column with email text content",
            key="spreadsheet_uploader",
        )

        if spreadsheet_file is not None:
            try:
                # Load the file
                if spreadsheet_file.name.endswith(".csv"):
                    data_df = pd.read_csv(spreadsheet_file)
                else:
                    data_df = pd.read_excel(spreadsheet_file, engine="openpyxl")

                st.success(f"✅ Loaded: {spreadsheet_file.name} ({len(data_df)} rows, {len(data_df.columns)} columns)")

                with st.expander("📋 Preview Data", expanded=False):
                    st.dataframe(data_df.head(5), use_container_width=True, hide_index=True)

                # Auto-detect text column
                text_candidates = [
                    c for c in data_df.columns
                    if any(kw in c.lower() for kw in ["email", "message", "body", "text", "content", "mail"])
                ]
                if not text_candidates:
                    text_candidates = data_df.select_dtypes(include=["object"]).columns.tolist()

                if text_candidates:
                    default_col = text_candidates[0]
                else:
                    default_col = data_df.columns[0]

                text_column = st.selectbox(
                    "📝 Select email text column",
                    options=data_df.columns.tolist(),
                    index=data_df.columns.tolist().index(default_col) if default_col in data_df.columns else 0,
                )

                if st.button("🚀 Classify All", type="primary", use_container_width=True, key="spreadsheet_classify"):
                    with st.spinner(f"📊 Classifying {len(data_df)} emails..."):
                        try:
                            predictions = []
                            confidences = []
                            spam_count = 0
                            ham_count = 0
                            hm = get_history_manager()

                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            for i, text in enumerate(data_df[text_column].fillna("")):
                                status_text.caption(f"Processing {i + 1}/{len(data_df)}...")
                                if text and str(text).strip():
                                    result = pipeline.predict_single_email(str(text))
                                    pred = result["prediction"]
                                    conf = result.get("confidence")

                                    # URL analysis
                                    url_analysis = analyze_urls_in_text(str(text))

                                    # Save to history
                                    hm.add_entry(
                                        email_text=str(text),
                                        prediction=pred,
                                        confidence=conf,
                                        source="batch",
                                        url_count=url_analysis["total_urls"],
                                        suspicious_urls=url_analysis["suspicious_count"],
                                    )

                                    if pred == "Spam":
                                        spam_count += 1
                                    else:
                                        ham_count += 1

                                    predictions.append(pred)
                                    confidences.append(conf)
                                else:
                                    predictions.append("Unknown")
                                    confidences.append(None)

                                progress_bar.progress((i + 1) / len(data_df))

                            status_text.empty()
                            progress_bar.empty()

                            # Add results to dataframe
                            data_df["Prediction"] = predictions
                            data_df["Confidence"] = confidences

                            # Summary
                            st.subheader("📊 Results Summary")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Total", len(data_df))
                            col2.metric("Spam", spam_count, delta=f"{spam_count/len(data_df)*100:.1f}%" if len(data_df) > 0 else "0%", delta_color="inverse")
                            col3.metric("Ham", ham_count, delta=f"{ham_count/len(data_df)*100:.1f}%" if len(data_df) > 0 else "0%")

                            st.dataframe(data_df.head(10), use_container_width=True, hide_index=True)

                            # Download results
                            output_csv = data_df.to_csv(index=False).encode("utf-8")
                            st.download_button(
                                "📥 Download Results (CSV)",
                                data=output_csv,
                                file_name=f"spreadsheet_results_{int(time.time())}.csv",
                                mime="text/csv",
                                use_container_width=True,
                            )

                            # Download HTML report
                            report_data_list = []
                            for _, row in data_df.iterrows():
                                report_data_list.append({
                                    "prediction": row.get("Prediction", "Unknown"),
                                    "email_subject": "",
                                    "confidence": row.get("Confidence"),
                                    "timestamp": time.time(),
                                    "source": "batch",
                                })
                            report_html = generate_classification_report(
                                report_data_list,
                                title=f"Spreadsheet Results — {spreadsheet_file.name}",
                            )
                            st.download_button(
                                "📄 Download Report (HTML)",
                                data=report_html.encode("utf-8"),
                                file_name=f"spreadsheet_report_{int(time.time())}.html",
                                mime="text/html",
                                use_container_width=True,
                            )

                        except Exception as e:
                            st.error(f"⚠️ Error processing spreadsheet: {str(e)}")

            except Exception as e:
                st.error(f"⚠️ Error loading file: {str(e)}")

# ---------------------------------------------------------------------------
# Tab 3: Model Comparison Dashboard
# ---------------------------------------------------------------------------
with tab3:
    st.header("📊 Model Performance Comparison")
    st.markdown(
        "Compare all trained models side-by-side with radar charts, "
        "confusion matrices, and detailed performance metrics."
    )

    # Cache the ModelComparison instance
    @st.cache_resource(show_spinner="Loading model comparison data...")
    def get_model_comparison():
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

        # --- Summary metrics row ---
        st.subheader("📈 Overall Summary")
        df = mc.get_comparison_df()
        best_row = df[df["Best"] == "⭐"].iloc[0] if not df.empty and "⭐" in df["Best"].values else None

        if best_row is not None:
            cols = st.columns(4)
            cols[0].metric("🏆 Best Model", best_row["Model"])
            cols[1].metric("🎯 Accuracy", f"{best_row['Accuracy']*100:.2f}%")
            cols[2].metric("📐 Precision", f"{best_row['Precision']*100:.2f}%")
            cols[3].metric("📊 F1-Score", f"{best_row['F1-Score']*100:.2f}%")
        else:
            st.caption("No best model selected yet.")

        # --- Radar Chart ---
        st.subheader("🕸️ Radar Chart — Metrics Comparison")
        radar_fig = mc.get_radar_chart()
        if radar_fig:
            # Theme-aware font color
            text_color = "#e8eaed" if st.session_state.theme == "dark" else "#1a1a2e"
            radar_fig.update_layout(
                font=dict(color=text_color),
                polar=dict(
                    radialaxis=dict(gridcolor="#444" if st.session_state.theme == "dark" else "#e0e0e0"),
                    angularaxis=dict(gridcolor="#444" if st.session_state.theme == "dark" else "#e0e0e0"),
                ),
            )
            st.plotly_chart(radar_fig, use_container_width=True)
        else:
            st.caption("Radar chart not available.")

        # --- Model Ranking Table ---
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

        # --- Confusion Matrices ---
        st.subheader("🔢 Confusion Matrices")
        st.markdown(
            "Each cell shows **count** and **percentage** (by row). "
            "Rows = true labels, columns = predictions."
        )

        cm_figs = mc.get_all_confusion_matrices()
        if cm_figs:
            # Arrange in a grid: 3 columns for smaller screens
            cm_names = list(cm_figs.keys())
            cm_chunks = [cm_names[i:i+3] for i in range(0, len(cm_names), 3)]

            for chunk in cm_chunks:
                cols = st.columns(len(chunk))
                for col, name in zip(cols, chunk):
                    with col:
                        fig = cm_figs[name]
                        if fig:
                            # Theme awareness
                            text_color = "#e8eaed" if st.session_state.theme == "dark" else "#1a1a2e"
                            fig.update_layout(
                                font=dict(color=text_color),
                                title=dict(
                                    text=("⭐ " if name == mc.best_model_name else "") + name,
                                    font=dict(size=13),
                                ),
                            )
                            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Confusion matrices not available. Train models to generate them.")

        # --- Run Details ---
        with st.expander("📁 Training Run Details"):
            if mc.run_dir:
                st.markdown(f"**Run directory:** `{mc.run_dir}`")
                # Check for metadata
                meta_path = os.path.join(mc.run_dir, "observations", "model_metadata.json")
                if os.path.exists(meta_path):
                    with open(meta_path) as f:
                        meta = json.load(f)
                    st.json(meta)
                else:
                    # Show directory listing
                    st.code(
                        "\n".join(os.listdir(os.path.join(mc.run_dir, "models")))
                        if os.path.exists(os.path.join(mc.run_dir, "models"))
                        else "No model files found."
                    )
            else:
                st.caption("No run directory discovered.")

        # --- Refresh button ---
        st.divider()
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

# ---------------------------------------------------------------------------
# Tab 4: Classification History
# ---------------------------------------------------------------------------
with tab4:
    st.header("📋 Classification History")
    st.markdown(
        "Browse past classifications, track trends over time, "
        "and search through your prediction history."
    )

    hm = get_history_manager()

    # Stats summary
    stats = hm.get_stats(days_back=30)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Last 30 Days", stats["total"])
    col2.metric("🚨 Spam", stats["spam_count"], delta=f"{stats['spam_pct']:.0f}%", delta_color="inverse")
    col3.metric("✅ Ham", stats["ham_count"])
    col4.metric("🔗 Suspicious URLs", stats["total_suspicious_urls"])

    # Trend chart (using Streamlit's built-in line chart)
    if stats["daily_counts"]:
        st.subheader("📈 Daily Trend")
        trend_df = pd.DataFrame(stats["daily_counts"])
        if not trend_df.empty:
            trend_df = trend_df.set_index("date")
            st.line_chart(trend_df, height=200)
    else:
        st.caption("No classification data yet. Classify some emails to see trends!")

    # Filters
    st.subheader("🔍 Search History")
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    with filter_col1:
        search_text = st.text_input("Search in email text or subject", placeholder="Type to search...", label_visibility="collapsed")
    with filter_col2:
        pred_filter = st.selectbox("Prediction", ["All", "Spam", "Ham"], label_visibility="collapsed")
    with filter_col3:
        source_filter = st.selectbox("Source", ["All", "manual", "batch", "live", "api"], label_visibility="collapsed")

    # Map filters
    pred_value = pred_filter if pred_filter != "All" else None
    source_value = source_filter if source_filter != "All" else None
    search_value = search_text if search_text else None

    # Pagination
    page_size = 25
    total_count = hm.get_total_count(
        prediction_filter=pred_value,
        source_filter=source_value,
        search_text=search_value,
    )
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    if "history_page" not in st.session_state:
        st.session_state.history_page = 1

    page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
    with page_col2:
        st.caption(f"Page {st.session_state.history_page} of {total_pages} ({total_count} records)")

    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([1, 1, 2, 1, 1])
    with nav_col1:
        if st.button("◀ Prev", use_container_width=True, disabled=st.session_state.history_page <= 1):
            st.session_state.history_page = max(1, st.session_state.history_page - 1)
            st.rerun()
    with nav_col4:
        if st.button("Next ▶", use_container_width=True, disabled=st.session_state.history_page >= total_pages):
            st.session_state.history_page = min(total_pages, st.session_state.history_page + 1)
            st.rerun()
    with nav_col5:
        if st.button("🗑 Clear", use_container_width=True):
            hm.clear_history()
            st.rerun()

    # Fetch records
    records = hm.get_history(
        limit=page_size,
        offset=(st.session_state.history_page - 1) * page_size,
        prediction_filter=pred_value,
        source_filter=source_value,
        search_text=search_value,
    )

    if records:
        # Display as DataFrame
        display_data = []
        for r in records:
            display_data.append({
                "Time": r.get("datetime", ""),
                "Prediction": r.get("prediction", ""),
                "Confidence": f"{r.get('confidence', 0):.1f}%" if r.get("confidence") else "N/A",
                "Source": r.get("source", ""),
                "URLs": f"{r.get('suspicious_urls', 0)} susp." if r.get('suspicious_urls', 0) > 0 else str(r.get('url_count', 0)),
                "Subject": r.get("email_subject", "")[:80] if r.get("email_subject") else r.get("email_text", "")[:80],
            })

        df_history = pd.DataFrame(display_data)
        st.dataframe(
            df_history,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Time": st.column_config.TextColumn("Time", width="small"),
                "Prediction": st.column_config.TextColumn("📊 Prediction", width="small"),
                "Confidence": st.column_config.TextColumn("Confidence", width="small"),
                "Source": st.column_config.TextColumn("Source", width="small"),
                "URLs": st.column_config.TextColumn("🔗 URLs", width="small"),
                "Subject": st.column_config.TextColumn("Subject / Preview", width="large"),
            },
        )

        # Download all history as CSV
        all_records = hm.get_history(limit=10000, search_text=search_value)
        if all_records:
            export_data = []
            for r in all_records:
                export_data.append({
                    "Time": r.get("datetime", ""),
                    "Prediction": r.get("prediction", ""),
                    "Confidence": r.get("confidence"),
                    "Spam Risk": r.get("spam_risk"),
                    "Source": r.get("source", ""),
                    "URL Count": r.get("url_count", 0),
                    "Suspicious URLs": r.get("suspicious_urls", 0),
                    "Subject/Text": r.get("email_subject", "") or r.get("email_text", ""),
                })
            export_df = pd.DataFrame(export_data)
            csv_export = export_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download History (CSV)",
                data=csv_export,
                file_name=f"classification_history_{int(time.time())}.csv",
                mime="text/csv",
                use_container_width=True,
            )

            # Download history as HTML report
            report_html = generate_classification_report(
                export_data,
                title="Classification History Report",
            )
            st.download_button(
                "📄 Download Report (HTML)",
                data=report_html.encode("utf-8"),
                file_name=f"history_report_{int(time.time())}.html",
                mime="text/html",
                use_container_width=True,
            )
    else:
        st.info("📭 No classification history found. Classify some emails to see them here!")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    f"""
    <footer>
        Spam Email Classifier • Built with scikit-learn, Streamlit & SHAP
        • <span id="theme-indicator">{'🌙 Dark Mode' if st.session_state.theme == 'dark' else '☀️ Light Mode'}</span>
    </footer>
    """,
    unsafe_allow_html=True,
)
