"""Tab 2: Batch file processing (MBOX + CSV/Excel)."""

from __future__ import annotations

import contextlib
import os
import tempfile
import time
from typing import Any

import pandas as pd
import streamlit as st

from src.utils.report_generator import generate_classification_report
from src.utils.url_analyzer import analyze_urls_in_text


def render_batch_processing(
    pipeline: Any,
    history_manager: Any,
) -> None -> None:
    """Render the batch processing tab."""
"""Tab 2: Batch file processing (MBOX + CSV/Excel)."""




st.header("Batch File Processing")

st.markdown(
    "Upload email files for bulk classification. Supports "
    "**MBOX** files, **CSV** files, and **Excel (.xlsx)** files."
)

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
        st.success(
            f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)"
        )

        if st.button(
            "🚀 Process File",
            type="primary",
            use_container_width=True,
            key="mbox_process",
        ):
            with st.spinner("📂 Processing file... this may take a moment"):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mbox") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())

                        tmp_path = tmp_file.name

                    try:
                        df = pipeline.predict_mbox_file(tmp_path)

                        hm = history_manager

                        for _, row in df.iterrows():
                            hm.add_entry(
                                email_text=row.get("Body", ""),
                                prediction=row.get("Prediction", "Unknown"),
                                source="batch",
                                email_subject=row.get("Subject", ""),
                            )

                        st.subheader("📊 Processing Results")

                        col1, col2, col3 = st.columns(3)

                        spam_count = len(df[df["Prediction"] == "Spam"])

                        ham_count = len(df[df["Prediction"] == "Ham"])

                        col1.metric("Total Emails", len(df))

                        col2.metric(
                            "Spam Found",
                            spam_count,
                            delta=f"{spam_count / len(df) * 100:.1f}%" if len(df) > 0 else "0%",
                            delta_color="inverse",
                        )

                        col3.metric(
                            "Ham (Safe)",
                            ham_count,
                            delta=f"{ham_count / len(df) * 100:.1f}%" if len(df) > 0 else "0%",
                        )

                        st.subheader("📋 Results Preview")

                        preview_cols = ["Time", "Subject", "Prediction"]

                        available_cols = [c for c in preview_cols if c in df.columns]

                        st.dataframe(
                            df[available_cols].head(10),
                            use_container_width=True,
                            hide_index=True,
                        )

                        csv = df.to_csv(index=False).encode("utf-8")

                        st.download_button(
                            label="📥 Download Full Results (CSV)",
                            data=csv,
                            file_name=f"spam_predictions_{int(time.time())}.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )

                        report_data = []

                        for _, row in df.iterrows():
                            report_data.append(
                                {
                                    "prediction": row.get("Prediction", "Unknown"),
                                    "email_subject": row.get("Subject", ""),
                                    "timestamp": time.time(),
                                    "source": "batch",
                                }
                            )

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
                            with contextlib.suppress(PermissionError):
                                os.unlink(tmp_path)


                except (OSError, ValueError, KeyError) as e:
                    st.error(f"⚠️ Error processing file: {e!s}")

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
            if spreadsheet_file.name.endswith(".csv"):
                data_df = pd.read_csv(spreadsheet_file)

            else:
                data_df = pd.read_excel(spreadsheet_file, engine="openpyxl")

            st.success(
                f"✅ Loaded: {spreadsheet_file.name} ({len(data_df)} rows, {len(data_df.columns)} columns)"
            )

            with st.expander("📋 Preview Data", expanded=False):
                st.dataframe(data_df.head(5), use_container_width=True, hide_index=True)

            text_candidates = [
                c
                for c in data_df.columns
                if any(
                    kw in c.lower()
                    for kw in [
                        "email",
                        "message",
                        "body",
                        "text",
                        "content",
                        "mail",
                    ]
                )
            ]

            if not text_candidates:
                text_candidates = data_df.select_dtypes(include=["object"]).columns.tolist()

            default_col = text_candidates[0] if text_candidates else data_df.columns[0]

            text_column = st.selectbox(
                "📝 Select email text column",
                options=data_df.columns.tolist(),
                index=data_df.columns.tolist().index(default_col)
                if default_col in data_df.columns
                else 0,
            )

            if st.button(
                "🚀 Classify All",
                type="primary",
                use_container_width=True,
                key="spreadsheet_classify",
            ):
                with st.spinner(f"📊 Classifying {len(data_df)} emails..."):
                    try:
                        predictions = []

                        confidences = []

                        spam_count = 0

                        ham_count = 0

                        hm = history_manager

                        progress_bar = st.progress(0)

                        status_text = st.empty()

                        for i, text in enumerate(data_df[text_column].fillna("")):
                            status_text.caption(f"Processing {i + 1}/{len(data_df)}...")

                            if text and str(text).strip():
                                result = pipeline.predict_single_email(str(text))

                                pred = result["prediction"]

                                conf = result.get("confidence")

                                url_analysis = analyze_urls_in_text(str(text))

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

                        data_df["Prediction"] = predictions

                        data_df["Confidence"] = confidences

                        st.subheader("📊 Results Summary")

                        col1, col2, col3 = st.columns(3)

                        col1.metric("Total", len(data_df))

                        col2.metric(
                            "Spam",
                            spam_count,
                            delta=f"{spam_count / len(data_df) * 100:.1f}%"
                            if len(data_df) > 0
                            else "0%",
                            delta_color="inverse",
                        )

                        col3.metric(
                            "Ham",
                            ham_count,
                            delta=f"{ham_count / len(data_df) * 100:.1f}%"
                            if len(data_df) > 0
                            else "0%",
                        )

                        st.dataframe(
                            data_df.head(10),
                            use_container_width=True,
                            hide_index=True,
                        )

                        output_csv = data_df.to_csv(index=False).encode("utf-8")

                        st.download_button(
                            "📥 Download Results (CSV)",
                            data=output_csv,
                            file_name=f"spreadsheet_results_{int(time.time())}.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )

                        report_data_list = []

                        for _, row in data_df.iterrows():
                            report_data_list.append(
                                {
                                    "prediction": row.get("Prediction", "Unknown"),
                                    "email_subject": "",
                                    "confidence": row.get("Confidence"),
                                    "timestamp": time.time(),
                                    "source": "batch",
                                }
                            )

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

                    except (OSError, ValueError, KeyError) as e:
                        st.error(f"⚠️ Error processing spreadsheet: {e!s}")

        except (OSError, ValueError, KeyError) as e:
            st.error(f"⚠️ Error loading file: {e!s}")




