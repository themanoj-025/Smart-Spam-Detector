"""Tab 4: Classification history."""

from __future__ import annotations

import time
from typing import Any

import pandas as pd
import streamlit as st

from src.utils.report_generator import generate_classification_report


def render_history(history_manager: Any) -> None:
    """Render the classification history tab."""
"""Tab 4: Classification history."""

import time

import pandas as pd
import streamlit as st

from src.utils.report_generator import generate_classification_report

st.header("📋 Classification History")

st.markdown(
    "Browse past classifications, track trends over time, "
    "and search through your prediction history."
)

hm = history_manager

stats = hm.get_stats(days_back=30)

col1, col2, col3, col4 = st.columns(4)

col1.metric("📊 Last 30 Days", stats["total"])

col2.metric(
    "🚨 Spam",
    stats["spam_count"],
    delta=f"{stats['spam_pct']:.0f}%",
    delta_color="inverse",
)

col3.metric("✅ Ham", stats["ham_count"])

col4.metric("🔗 Suspicious URLs", stats["total_suspicious_urls"])

if stats["daily_counts"]:
    st.subheader("📈 Daily Trend")

    trend_df = pd.DataFrame(stats["daily_counts"])

    if not trend_df.empty:
        trend_df = trend_df.set_index("date")

        st.line_chart(trend_df, height=200)

else:
    st.caption("No classification data yet. Classify some emails to see trends!")

st.subheader("🔍 Search History")

filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])

with filter_col1:
    search_text = st.text_input(
        "Search in email text or subject",
        placeholder="Type to search...",
        label_visibility="collapsed",
    )

with filter_col2:
    pred_filter = st.selectbox(
        "Prediction", ["All", "Spam", "Ham"], label_visibility="collapsed"
    )

with filter_col3:
    source_filter = st.selectbox(
        "Source",
        ["All", "manual", "batch", "live", "api"],
        label_visibility="collapsed",
    )

pred_value = pred_filter if pred_filter != "All" else None

source_value = source_filter if source_filter != "All" else None

search_value = search_text if search_text else None

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
    if st.button(
        "◀ Prev",
        use_container_width=True,
        disabled=st.session_state.history_page <= 1,
    ):
        st.session_state.history_page = max(1, st.session_state.history_page - 1)

        st.rerun()

with nav_col4:
    if st.button(
        "Next ▶",
        use_container_width=True,
        disabled=st.session_state.history_page >= total_pages,
    ):
        st.session_state.history_page = min(total_pages, st.session_state.history_page + 1)

        st.rerun()

with nav_col5:
    if st.button("🗑 Clear", use_container_width=True):
        hm.clear_history()

        st.rerun()

records = hm.get_history(
    limit=page_size,
    offset=(st.session_state.history_page - 1) * page_size,
    prediction_filter=pred_value,
    source_filter=source_value,
    search_text=search_value,
)

if records:
    display_data = []

    for r in records:
        display_data.append(
            {
                "Time": r.get("datetime", ""),
                "Prediction": r.get("prediction", ""),
                "Confidence": f"{r.get('confidence', 0):.1f}%"
                if r.get("confidence")
                else "N/A",
                "Source": r.get("source", ""),
                "URLs": f"{r.get('suspicious_urls', 0)} susp."
                if r.get("suspicious_urls", 0) > 0
                else str(r.get("url_count", 0)),
                "Subject": r.get("email_subject", "")[:80]
                if r.get("email_subject")
                else r.get("email_text", "")[:80],
            }
        )

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

    all_records = hm.get_history(limit=10000, search_text=search_value)

    if all_records:
        export_data = []

        for r in all_records:
            export_data.append(
                {
                    "Time": r.get("datetime", ""),
                    "Prediction": r.get("prediction", ""),
                    "Confidence": r.get("confidence"),
                    "Spam Risk": r.get("spam_risk"),
                    "Source": r.get("source", ""),
                    "URL Count": r.get("url_count", 0),
                    "Suspicious URLs": r.get("suspicious_urls", 0),
                    "Subject/Text": r.get("email_subject", "") or r.get("email_text", ""),
                }
            )

        export_df = pd.DataFrame(export_data)

        csv_export = export_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download History (CSV)",
            data=csv_export,
            file_name=f"classification_history_{int(time.time())}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        report_html = generate_classification_report(
            export_data, title="Classification History Report"
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




