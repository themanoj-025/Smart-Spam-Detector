"""Spam Email Classifier - Streamlit Web Application

A production-grade machine learning system for classifying emails as Spam or Ham.

Features include single email classification, MBOX batch processing,
SHAP-based explainable AI, dark/light theme, and real-time typing analysis.
"""

import streamlit as st

from src.ui.model_loader import load_model
from src.ui.sidebar import render_sidebar
from src.ui.tab_batch import render_batch_processing
from src.ui.tab_history import render_history
from src.ui.tab_models import render_model_comparison
from src.ui.tab_single import render_single_email
from src.ui.theme import DARK_THEME_CSS, THEME_CSS
from src.utils.history_manager import HistoryManager

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

# ---------------------------------------------------------------------------
# Theme CSS
# ---------------------------------------------------------------------------

st.markdown(THEME_CSS, unsafe_allow_html=True)

if st.session_state.theme == "dark":
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load Model
# ---------------------------------------------------------------------------

pipeline, model_loaded, model_name = load_model()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

enable_explanation, enable_live = render_sidebar(pipeline, model_loaded)

# ---------------------------------------------------------------------------
# History Manager
# ---------------------------------------------------------------------------


@st.cache_resource(show_spinner=False)
def get_history_manager() -> HistoryManager:
    return HistoryManager()


hm = get_history_manager()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown("<h1>📧 Spam Email Classifier</h1>", unsafe_allow_html=True)
st.markdown(
    "Classify emails as **Spam** 🚨 or **Ham** ✅ (Safe) using "
    "Machine Learning with **scikit-learn** & **SHAP** explainability."
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Main Content - Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    ["🔍 Single Email", "📂 Batch Processing", "📊 Model Comparison", "📋 History"]
)

with tab1:
    render_single_email(pipeline, model_name, enable_explanation, enable_live, hm)

with tab2:
    render_batch_processing(pipeline, hm)

with tab3:
    render_model_comparison()

with tab4:
    render_history(hm)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <footer>
        Spam Email Classifier • Using scikit-learn, Streamlit & SHAP
        • <span id="theme-indicator">{"🌙 Dark Mode" if st.session_state.theme == "dark" else "☀️ Light Mode"}</span>
        <br>
        <a href="https://github.com/themanoj-025" target="_blank" style="
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-top: 10px;
            padding: 8px 18px;
            background-color: #24292e;
            color: #ffffff !important;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.88rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            transition: background-color 0.2s ease, transform 0.15s ease;
        "
        onmouseover="this.style.backgroundColor='#444d56'; this.style.transform='translateY(-2px)'"
        onmouseout="this.style.backgroundColor='#24292e'; this.style.transform='translateY(0)'"
        >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="white">
                <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
            </svg>
            themanoj-025
        </a>
    </footer>
    """,
    unsafe_allow_html=True,
)
