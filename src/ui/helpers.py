"""UI helper functions for prediction display."""

import streamlit as st

from src.utils.email_utils import clean_text

# ---------------------------------------------------------------------------

# Helper: Animated Circular Confidence Gauge (SVG)

# ---------------------------------------------------------------------------


def show_confidence_gauge(confidence: float, prediction: str, is_live: bool = False) -> None:
    """Render an animated circular gauge showing the spam confidence score."""

    spam_risk = confidence if prediction == "Spam" else 100.0 - confidence

    spam_risk = max(0, min(100, spam_risk))

    radius = 70 if not is_live else 55

    circumference = 2 * 3.14159 * radius

    arc_length = circumference * (spam_risk / 100)

    offset = circumference - arc_length

    if spam_risk < 50:
        ratio = spam_risk / 50

        r = int(76 + (255 - 76) * ratio)

        g = int(175 + (167 - 175) * ratio)

        b = int(80 + (38 - 80) * ratio)

    else:
        ratio = (spam_risk - 50) / 50

        r = int(255 + (244 - 255) * ratio)

        g = int(167 + (67 - 167) * ratio)

        b = int(38 + (54 - 38) * ratio)

    color = f"rgb({r},{g},{b})"

    size = 180 if not is_live else 140

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

            <path d="M 10 {size // 2 + 5}

                     A {(size - 20) / 2} {(size - 20) / 2} 0 0 1 {size - 10} {size // 2 + 5}"

                  fill="none"

                  stroke="var(--gauge-bg)"

                  stroke-width="{12 if not is_live else 10}"

                  stroke-linecap="round" />

            <path d="M 10 {size // 2 + 5}

                     A {(size - 20) / 2} {(size - 20) / 2} 0 0 1 {size - 10} {size // 2 + 5}"

                  fill="none"

                  stroke="{color}"

                  stroke-width="{12 if not is_live else 10}"

                  stroke-linecap="round"

                  stroke-dasharray="{circumference}"

                  stroke-dashoffset="{offset}"

                  style="transition: stroke-dashoffset 0.6s ease, stroke 0.4s ease;" />

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

            {"Updates as you type" if is_live else f"Spam probability: {spam_risk:.1f}%"}

        </div>

    </div>

    """

    st.markdown(gauge_html, unsafe_allow_html=True)


def show_confidence_bar(confidence: float, prediction: str) -> None:
    """Legacy horizontal confidence bar (used as secondary indicator)."""

    bar_color = "#ef5350" if prediction == "Spam" else "#66bb6a"

    st.markdown(
        f"""

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

    """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------

# Helper: Lightweight real-time analysis

# ---------------------------------------------------------------------------


def compute_live_prediction(text: str, pipeline: object) -> None:
    """Run a lightweight prediction for real-time analysis (no SHAP)."""

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

    except (ValueError, KeyError, TypeError):
        return None, None, None


# ---------------------------------------------------------------------------

# Helper: Show explanation UI

# ---------------------------------------------------------------------------


def show_explanation(explanation: dict, prediction: str) -> None:
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

                st.markdown(
                    f"""

                <div class="word-bar-container">

                    <span class="word-label" style="color:var(--spam-text);">{w["word"]}</span>

                    <div class="bar-track">

                        <div class="bar-fill spam-bar" style="width:{pct}%;"></div>

                    </div>

                    <span class="bar-value">{w["contribution"]:+.3f}</span>

                </div>

                """,
                    unsafe_allow_html=True,
                )

        else:
            st.caption("No spam-indicative words found")

    with ham_col:
        st.markdown("##### ✅ Pushes toward Ham")

        if top_ham:
            max_val = max(abs(w["contribution"]) for w in top_ham) or 1

            for w in top_ham:
                pct = abs(w["contribution"]) / max_val * 100

                st.markdown(
                    f"""

                <div class="word-bar-container">

                    <span class="word-label" style="color:var(--ham-text);">{w["word"]}</span>

                    <div class="bar-track">

                        <div class="bar-fill ham-bar" style="width:{pct}%;"></div>

                    </div>

                    <span class="bar-value">{w["contribution"]:+.3f}</span>

                </div>

                """,
                    unsafe_allow_html=True,
                )

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
        "Explanations are computed using <strong>SHAP</strong> "
        "(SHapley Additive exPlanations) — a game-theoretic approach "
        "to model interpretability."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)



