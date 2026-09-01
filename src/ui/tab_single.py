"""Tab 1: Single email classification."""

from __future__ import annotations

import time
from typing import Any

import pandas as pd
import streamlit as st

from src.ui.helpers import compute_live_prediction, show_confidence_bar, show_confidence_gauge, show_explanation
from src.utils.report_generator import generate_email_report
from src.utils.url_analyzer import analyze_urls_in_text


def render_single_email(
    pipeline: Any,
    model_name: str,
    enable_explanation: bool,
    enable_live: bool,
    history_manager: Any,
) -> None:
    """Render the single email classification tab."""


st.header("Check a Single Email")

st.markdown(
    "Paste the email content below. The **live gauge** updates as you type — "
    "click **Classify** for a full analysis with SHAP explanation."
)

# --- Quick Example Buttons ---

st.markdown(
    "<div style='margin-bottom:0.5rem;'><span style='font-size:0.85rem;color:var(--text-muted);font-weight:500;'>"
    "⚡ Quick test:</span></div>",
    unsafe_allow_html=True,
)

ex_col1, ex_col2, ex_col3, ex_col4 = st.columns(4)

EXAMPLE_EMAILS = {
    "spam": "Congratulations! You have won a $1000 Walmart gift card. Click here to claim your prize now! Act fast, this offer expires in 24 hours!",
    "ham": "Hey, are we still meeting for lunch tomorrow at the cafe? Let me know what time works for you.",
    "phish": "URGENT: Your account has been compromised. Please verify your identity immediately at http://secure-bank-login.xyz/verify to avoid suspension.",
    "scam": "Dear friend, I am a prince from Nigeria and I have $15,000,000 USD that I need to transfer to your bank account. Please send your bank details.",
}

with ex_col1:
    if st.button("🚨 Spam", use_container_width=True, key="ex_spam"):
        st.session_state.email_input = EXAMPLE_EMAILS["spam"]

        st.rerun()

with ex_col2:
    if st.button("✅ Ham", use_container_width=True, key="ex_ham"):
        st.session_state.email_input = EXAMPLE_EMAILS["ham"]

        st.rerun()

with ex_col3:
    if st.button("🔗 Phishing", use_container_width=True, key="ex_phish"):
        st.session_state.email_input = EXAMPLE_EMAILS["phish"]

        st.rerun()

with ex_col4:
    if st.button("💰 Scam", use_container_width=True, key="ex_scam"):
        st.session_state.email_input = EXAMPLE_EMAILS["scam"]

        st.rerun()

# Text input

email_text = st.text_area(
    "Email Content",
    height=200,
    placeholder="Paste email content here... e.g., 'Dear friend, I have a business proposal...'",
    label_visibility="collapsed",
    key="email_input",
)

# --- Email Stats Bar ---

if email_text and email_text.strip():
    words = len(email_text.split())

    chars = len(email_text)

    sentences = email_text.count(".") + email_text.count("!") + email_text.count("?")

    st.markdown(
        f"<div class='email-stats'>"
        f"<div class='email-stat-item'>📝 <span class='stat-val'>{words}</span> words</div>"
        f"<div class='email-stat-item'>🔤 <span class='stat-val'>{chars}</span> chars</div>"
        f"<div class='email-stat-item'>📑 <span class='stat-val'>{sentences}</span> sentences</div>"
        f"<div class='email-stat-item'>⏱️ ~{max(1, -(-words // 200))} min read</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

# Real-time typing analysis

if enable_live and email_text and email_text.strip():
    live_label, live_conf, live_risk = compute_live_prediction(email_text, pipeline)

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

                # Save to history                    hm = history_manager

                spam_risk_val = (
                    confidence
                    if prediction == "Spam"
                    else (100.0 - confidence)
                    if confidence
                    else None
                )

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

                # Toast notification

                toast_class = "toast-danger" if prediction == "Spam" else "toast-success"

                toast_icon = "🚨" if prediction == "Spam" else "✅"

                toast_msg = f"{toast_icon} Classified as <strong>{prediction}</strong>"

                if confidence:
                    toast_msg += f" with <strong>{confidence:.1f}%</strong> confidence"

                st.markdown(
                    f"<div class='toast-notification {toast_class}'>{toast_msg}</div>",
                    unsafe_allow_html=True,
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
                    show_confidence_gauge(confidence, prediction, is_live=False)

                    with st.expander("📊 Show confidence bar"):
                        show_confidence_bar(confidence, prediction)

                # --- URL Analysis Section ---

                if url_analysis["total_urls"] > 0:
                    with st.expander(
                        f"🔗 URL Analysis — {url_analysis['total_urls']} URL(s) found, {url_analysis['suspicious_count']} suspicious",
                        expanded=url_analysis["suspicious_count"] > 0,
                    ):
                        risk_level = url_analysis["risk_level"]

                        risk_icon = {
                            "low": "🟢",
                            "medium": "🟡",
                            "high": "🔴",
                            "none": "⚪",
                        }.get(risk_level, "⚪")

                        st.markdown(
                            f"**{risk_icon} Overall URL Risk: {url_analysis['overall_risk_score']:.0f}% — {risk_level.upper()}**"
                        )

                        url_df = pd.DataFrame(
                            [
                                {
                                    "URL": u["url"][:80],
                                    "Host": u["hostname"],
                                    "Risk": f"{u['risk_score']:.0f}%",
                                    "Flags": ", ".join(u["flags"]),
                                }
                                for u in url_analysis["urls"]
                            ]
                        )

                        st.dataframe(url_df, use_container_width=True, hide_index=True)

            except (RuntimeError, ValueError, KeyError) as e:
                st.error(f"⚠️ Error analyzing email: {e!s}")

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

                except (RuntimeError, ValueError, KeyError) as e:
                    st.warning(f"⚠️ Explanation not available: {e!s}")

        # --- Report Download ---

        if confidence:
            explanation_summary = None

            if (
                enable_explanation
                and "explanation" in locals()
                and isinstance(explanation, dict)
                and explanation.get("status") == "available"
            ):
                top_spam = explanation.get("top_spam_words", [])

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




