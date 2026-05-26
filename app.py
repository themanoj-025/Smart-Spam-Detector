"""Spam Email Classifier - Streamlit Web Application

A production-grade machine learning system for classifying emails as Spam or Ham.
Features include single email classification and MBOX batch processing.
"""

import os
import time
import tempfile
from pathlib import Path

import streamlit as st
import pandas as pd

from src.pipeline.prediction_pipeline import PredictionPipeline

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
# Custom CSS for better styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .stButton > button {
        width: 100%;
    }
    .prediction-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .spam-box {
        background-color: #ffebee;
        border: 2px solid #ef5350;
    }
    .ham-box {
        background-color: #e8f5e9;
        border: 2px solid #66bb6a;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    footer {
        text-align: center;
        color: #9e9e9e;
        font-size: 0.8rem;
        padding: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Model Loading
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading trained models...")
def get_pipeline():
    """Initialize and load the prediction pipeline (cached)."""
    return PredictionPipeline(load_models=True)


# Try to load models, show helpful error if not found
try:
    pipeline = get_pipeline()
    model_loaded = True
    model_name = Path(pipeline.config.model_path).name if pipeline.config.model_path else "Unknown"
except FileNotFoundError as e:
    st.error(f"""
        ### 🚫 Models Not Found
        
        No trained models were found. You need to train the models first:
        
        ```bash
        python -m src.pipeline.training_pipeline
        ```
        
        Or place trained model files in the `outputs/` directory.
        
        **Error:** {str(e)}
    """)
    st.stop()
except Exception as e:
    st.error(f"⚠️ Unexpected error loading models: {str(e)}")
    st.stop()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("📧 Spam Email Classifier")
st.markdown(
    "Classify emails as **Spam** 🚨 or **Ham** ✅ (Safe) using "
    "Machine Learning with **scikit-learn**."
)
st.markdown("</div>", unsafe_allow_html=True)

# Sidebar - Model Info
with st.sidebar:
    st.header("📊 Model Info")
    st.metric("Status", "✅ Loaded" if model_loaded else "❌ Not loaded")
    if model_loaded and pipeline.config.model_path:
        st.caption(f"Model: `{Path(pipeline.config.model_path).name}`")
    
    st.divider()
    st.header("ℹ️ About")
    st.markdown("""
    This application uses a **TF-IDF Vectorizer** and a trained classifier
    to detect spam emails with high accuracy.
    
    **Supported features:**
    - ✉️ Single email classification
    - 📂 Batch MBOX file processing
    - 📊 Downloadable results
    """)
    
    st.divider()
    st.caption("Built with ❤️ using Streamlit & scikit-learn")

# ---------------------------------------------------------------------------
# Main Content - Tabs
# ---------------------------------------------------------------------------
tab1, tab2 = st.tabs(["🔍 Single Email", "📂 Batch MBOX Processing"])

# --- Tab 1: Single Email Classification ---
with tab1:
    st.header("Check a Single Email")
    st.markdown("Paste the email content below to get an instant Spam/Ham prediction.")
    
    email_text = st.text_area(
        "Email Content",
        height=200,
        placeholder="Paste email content here... e.g., 'Dear friend, I have a business proposal...'",
        label_visibility="collapsed",
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        classify_clicked = st.button("🔍 Classify Email", type="primary", use_container_width=True)
    
    if classify_clicked:
        if email_text and email_text.strip():
            with st.spinner("🤖 Analyzing email content..."):
                try:
                    result = pipeline.predict_single_email(email_text)
                    prediction = result['prediction']
                    confidence = result.get('confidence')
                    
                    # Display result with styling
                    if prediction == "Spam":
                        st.markdown(
                            f"""
                            <div class="prediction-box spam-box">
                                <h2 style="color: #c62828; margin: 0;">🚨 SPAM DETECTED</h2>
                                <p style="font-size: 1.2rem; margin: 0.5rem 0 0 0;">
                                    This email is likely <strong>Spam</strong>
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div class="prediction-box ham-box">
                                <h2 style="color: #2e7d32; margin: 0;">✅ SAFE - HAM</h2>
                                <p style="font-size: 1.2rem; margin: 0.5rem 0 0 0;">
                                    This email appears to be <strong>Safe (Ham)</strong>
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    if confidence:
                        st.info(f"**Confidence Score:** {confidence:.1f}%")
                        
                        # Mini confidence bar
                        bar_color = "#ef5350" if prediction == "Spam" else "#66bb6a"
                        st.markdown(
                            f"""
                            <div style="background-color: #e0e0e0; border-radius: 10px; height: 10px; margin: 10px 0;">
                                <div style="background-color: {bar_color}; 
                                            width: {confidence}%; 
                                            height: 10px; 
                                            border-radius: 10px;
                                            transition: width 0.5s;">
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                except Exception as e:
                    st.error(f"⚠️ Error analyzing email: {str(e)}")
        else:
            st.warning("⚠️ Please enter some text to classify.")

# --- Tab 2: Batch MBOX Processing ---
with tab2:
    st.header("Process MBOX File")
    st.markdown(
        "Upload an MBOX file (exported from Gmail, Thunderbird, etc.) "
        "to classify all emails at once. Results can be downloaded as CSV."
    )
    
    uploaded_file = st.file_uploader(
        "Choose an MBOX file",
        type=['mbox', 'txt'],
        help="Upload an MBOX file exported from your email client",
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name} "
                   f"({uploaded_file.size / 1024:.1f} KB)")
        
        if st.button("🚀 Process File", type="primary", use_container_width=True):
            with st.spinner("📂 Processing file... this may take a moment"):
                try:
                    # Save uploaded file to temp location
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mbox') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    try:
                        # Process file
                        df = pipeline.predict_mbox_file(tmp_path)
                        
                        # Show summary metrics in columns
                        st.subheader("📊 Processing Results")
                        col1, col2, col3 = st.columns(3)
                        
                        spam_count = len(df[df['Prediction'] == 'Spam'])
                        ham_count = len(df[df['Prediction'] == 'Ham'])
                        
                        col1.metric(
                            "Total Emails",
                            len(df),
                            delta=None,
                        )
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
                        preview_cols = ['Time', 'Subject', 'Prediction']
                        available_cols = [c for c in preview_cols if c in df.columns]
                        st.dataframe(
                            df[available_cols].head(10),
                            use_container_width=True,
                            hide_index=True,
                        )
                        
                        # Download button
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Full Results (CSV)",
                            data=csv,
                            file_name=f"spam_predictions_{int(time.time())}.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )
                        
                    finally:
                        # Cleanup temp file
                        if os.path.exists(tmp_path):
                            try:
                                os.unlink(tmp_path)
                            except PermissionError:
                                pass  # Windows sometimes locks temp files
                                
                except Exception as e:
                    st.error(f"⚠️ Error processing file: {str(e)}")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <footer>
        Spam Email Classifier • Built with scikit-learn & Streamlit
    </footer>
    """,
    unsafe_allow_html=True,
)
