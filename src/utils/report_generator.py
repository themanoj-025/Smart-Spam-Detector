"""Report generator for downloadable classification reports.

Generates self-contained HTML reports with embedded CSS styling,
statistics summaries, distribution charts (using SVG/CSS instead of
Plotly for self-containment), and full results tables.
"""

from html import escape
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


def _bar_chart_svg(
    data: List[Dict[str, Any]],
    value_key: str,
    label_key: str,
    title: str,
    bar_color: str = "#4a90d9",
    width: int = 600,
    height: int = 200,
) -> str:
    """Generate an inline SVG bar chart.

    Uses simple rect elements with labels — no external dependencies.
    """
    if not data:
        return "<p>No data available</p>"

    max_val = max(d.get(value_key, 0) for d in data) or 1
    bar_count = len(data)
    bar_width = max(20, (width - 60) // bar_count - 8)
    spacing = 12
    start_x = 50
    chart_height = height - 40

    bars = []
    labels = []
    for i, d in enumerate(data):
        val = d.get(value_key, 0)
        bar_h = (val / max_val) * (chart_height - 20)
        x = start_x + i * (bar_width + spacing)
        y = chart_height - bar_h + 10
        bars.append(
            f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_h}" '
            f'fill="{bar_color}" rx="3">'
            f'<title>{escape(str(d.get(label_key, "")))}: {val}</title>'
            f'</rect>'
        )
        labels.append(
            f'<text x="{x + bar_width / 2}" y="{chart_height + 25}" '
            f'text-anchor="middle" font-size="10" fill="#666">'
            f'{escape(str(d.get(label_key, "")))}</text>'
        )

    joined_bars = ''.join(bars)
    joined_labels = ''.join(labels)
    mid = width / 2
    return (
        f'<svg width="{width}" height="{height}"'
        f' xmlns="http://www.w3.org/2000/svg">'
        f'<text x="{mid}" y="18" text-anchor="middle"'
        f' font-size="13" font-weight="600" fill="#333">'
        f'{title}</text>'
        f'{joined_bars}{joined_labels}</svg>'
    )


def generate_classification_report(
    results: List[Dict[str, Any]],
    title: str = "Email Classification Report",
    include_charts: bool = True,
    include_details: bool = True,
) -> str:
    """Generate a self-contained HTML report string.

    Args:
        results: List of classification result dicts. Each should have
                 at least 'prediction' and optionally 'email_text',
                 'confidence', 'spam_risk', 'timestamp', 'url_count',
                 'suspicious_urls', 'email_subject'.
        title: Report title.
        include_charts: Whether to include SVG charts.
        include_details: Whether to include the full results table.

    Returns:
        Complete HTML string ready for download/browser viewing.
    """
    total = len(results)
    spam_count = sum(1 for r in results if r.get("prediction") == "Spam")
    ham_count = sum(1 for r in results if r.get("prediction") == "Ham")
    unknown_count = total - spam_count - ham_count
    spam_pct = round(spam_count / max(total, 1) * 100, 1)
    ham_pct = round(ham_count / max(total, 1) * 100, 1)

    avg_confidence = 0.0
    confidences = [r.get("confidence") for r in results if r.get("confidence") is not None]
    if confidences:
        avg_confidence = round(sum(confidences) / len(confidences), 1)

    total_urls = sum(r.get("url_count", 0) for r in results)
    suspicious_urls = sum(r.get("suspicious_urls", 0) for r in results)

    # Build charts
    charts_html = ""
    if include_charts and total > 0:
        dist_data = [
            {"label": "Spam", "value": spam_count},
            {"label": "Ham", "value": ham_count},
        ]
        if unknown_count:
            dist_data.append({"label": "Unknown", "value": unknown_count})

        charts_html = f"""
        <div class="charts-section">
            <div class="chart-container">
                {_bar_chart_svg(
                    dist_data, "value", "label",
                    "Prediction Distribution",
                    bar_color="#4a90d9",
                    width=400, height=200,
                )}
            </div>
        </div>
        """

    # Build results table
    table_html = ""
    if include_details and results:
        rows = []
        for i, r in enumerate(results[:200]):  # Limit to 200 rows for file size
            pred = r.get("prediction", "Unknown")
            pred_class = "spam-row" if pred == "Spam" else "ham-row"
            confidence = r.get("confidence", "")
            timestamp = r.get("datetime") or (
                datetime.fromtimestamp(r["timestamp"]).strftime("%Y-%m-%d %H:%M")
                if r.get("timestamp") else ""
            )
            subject = escape(r.get("email_subject", ""))
            urls_info = ""
            if r.get("suspicious_urls", 0) > 0:
                n = r["suspicious_urls"]
                urls_info = (
                    f'<span class="badge badge-danger">'
                    f'{n} susp.</span>'
                )
            elif r.get("url_count", 0) > 0:
                n = r["url_count"]
                urls_info = (
                    f'<span class="badge badge-ok">'
                    f'{n} urls</span>'
                )

            rows.append(f"""
            <tr class="{pred_class}">
                <td>{i + 1}</td>
                <td>{timestamp}</td>
                <td>{subject[:60]}</td>
                <td><strong>{pred}</strong></td>
                <td>{f"{confidence:.1f}%" if isinstance(confidence, (int, float)) else confidence}</td>
                <td>{urls_info}</td>
                <td>{escape(str(r.get("source", "")))}</td>
            </tr>
            """)

        table_html = f"""
        <div class="table-section">
            <h2>Results Table ({min(len(results), 200)} of {len(results)} shown)</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Time</th>
                        <th>Subject</th>
                        <th>Prediction</th>
                        <th>Confidence</th>
                        <th>URLs</th>
                        <th>Source</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1a1a2e;
        background: #f8f9fa;
        padding: 20px;
    }}
    .report-header {{
        text-align: center;
        padding: 30px 20px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: #fff;
        border-radius: 12px;
        margin-bottom: 24px;
    }}
    .report-header h1 {{ font-size: 1.8rem; margin-bottom: 6px; }}
    .report-header p {{ opacity: 0.85; font-size: 0.9rem; }}

    .summary-cards {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px;
        margin-bottom: 24px;
    }}
    .card {{
        background: #fff;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }}
    .card .value {{ font-size: 1.6rem; font-weight: 700; }}
    .card .label {{ font-size: 0.8rem; color: #888; margin-top: 4px; }}
    .card.spam .value {{ color: #e53935; }}
    .card.ham .value {{ color: #43a047; }}

    .charts-section {{
        background: #fff;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 24px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }}

    .table-section {{
        background: #fff;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }}
    .table-section h2 {{ font-size: 1.1rem; margin-bottom: 12px; color: #333; }}

    table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
    th {{ background: #f0f2f6; padding: 10px 8px; text-align: left; font-weight: 600; }}
    td {{ padding: 8px; border-bottom: 1px solid #eee; }}
    .spam-row {{ background: #fff5f5; }}
    .ham-row {{ background: #f0faf0; }}

    .badge {{
        display: inline-block;
        padding: 1px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    .badge-danger {{ background: #ffebee; color: #c62828; }}
    .badge-ok {{ background: #e8f5e9; color: #2e7d32; }}

    .report-footer {{
        text-align: center;
        padding: 20px;
        color: #999;
        font-size: 0.8rem;
    }}

    @media print {{
        body {{ padding: 0; background: #fff; }}
        .report-header {{ border-radius: 0; }}
        .summary-cards {{ break-inside: avoid; }}
        table {{ font-size: 0.75rem; }}
    }}
</style>
</head>
<body>
    <div class="report-header">
        <h1>📧 {escape(title)}</h1>
        <p>Generated on {datetime.now().strftime("%B %d, %Y at %H:%M")}
         &middot; {total} emails classified</p>
    </div>

    <div class="summary-cards">
        <div class="card"><div class="value">{total}</div><div class="label">Total Emails</div></div>
        <div class="card spam">
            <div class="value">{spam_count}</div>
            <div class="label">Spam ({spam_pct}%)</div>
        </div>
        <div class="card ham"><div class="value">{ham_count}</div><div class="label">Ham ({ham_pct}%)</div></div>
        <div class="card"><div class="value">{avg_confidence}%</div><div class="label">Avg Confidence</div></div>
        <div class="card"><div class="value">{total_urls}</div><div class="label">Total URLs</div></div>
        <div class="card spam"><div class="value">{suspicious_urls}</div><div class="label">Suspicious URLs</div></div>
    </div>

    {charts_html}
    {table_html}

    <div class="report-footer">
        Generated by Spam Email Classifier
         &middot; Built with scikit-learn
         &middot; {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
</body>
</html>"""

    return html


def generate_email_report(
    email_text: str,
    prediction: str,
    confidence: Optional[float] = None,
    spam_risk: Optional[float] = None,
    url_analysis: Optional[Dict[str, Any]] = None,
    explanation_summary: Optional[str] = None,
) -> str:
    """Generate a single-email detailed HTML report.

    Args:
        email_text: The classified email text.
        prediction: 'Spam' or 'Ham'.
        confidence: Confidence percentage.
        spam_risk: Spam risk percentage.
        url_analysis: Result from url_analyzer.analyze_urls_in_text().
        explanation_summary: Brief SHAP explanation text.

    Returns:
        Complete HTML string.
    """

    urls_html = ""
    if url_analysis and url_analysis.get("total_urls", 0) > 0:
        url_rows = []
        for u in url_analysis.get("urls", []):
            risk = u.get("risk_score", 0)
            risk_label = (
                "High" if risk >= 50
                else "Medium" if risk >= 20
                else "Low"
            )
            risk_bg = (
                "#f44336" if risk >= 50
                else "#ffa726" if risk >= 20
                else "#66bb6a"
            )
            flags = ", ".join(u.get("flags", []))
            url_rows.append(f"""
            <tr>
                <td style="word-break:break-all;max-width:300px;">
                    {escape(str(u.get("url", "")))}</td>
                <td>{escape(str(u.get("hostname", "")))}</td>
                <td><span style="background:{risk_bg};color:#fff;padding:1px 8px;border-radius:8px;">
                    {risk_label}</span></td>
                <td style="font-size:0.8rem;color:#888;">{escape(flags)}</td>
            </tr>
            """)

        urls_html = f"""
        <h3 style="margin:20px 0 10px;">🔗 URL Analysis</h3>
        <p>Found {url_analysis['total_urls']} URL(s),
         {url_analysis['suspicious_count']} suspicious.
        Overall URL risk: <strong>{url_analysis['overall_risk_score']:.0f}%
         ({url_analysis['risk_level'].upper()})</strong></p>
        <table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
            <thead>
                <tr style="background:#f0f2f6;">
                <th style="padding:6px;text-align:left;">URL</th>
                <th style="padding:6px;text-align:left;">Host</th>
                <th style="padding:6px;text-align:left;">Risk</th>
                <th style="padding:6px;text-align:left;">Flags</th>
            </tr></thead>
            <tbody>{''.join(url_rows)}</tbody>
        </table>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Email Classification Report</title>
<style>
    body {{ font-family: -apple-system, sans-serif;
        color: #1a1a2e; background: #f8f9fa; padding: 20px; }}
    .header {{ text-align:center; padding:30px; border-radius:12px; margin-bottom:20px;
               background: linear-gradient(135deg, #1a1a2e, #0f3460); color:#fff; }}
    .prediction-badge {{
        display:inline-block; padding:6px 20px;
        border-radius:20px; font-weight:700; font-size:1.2rem;
        {("background:#ffebee;color:#c62828" if prediction == "Spam"
          else "background:#e8f5e9;color:#2e7d32")}
    }}
    .section {{ background:#fff; border-radius:10px; padding:16px; margin-bottom:16px; box-shadow:0 1px 6px rgba(0,0,0,0.06); }}
    .section h3 {{ margin-bottom:8px; color:#333; }}
    .email-content {{
        background:#f5f5f5; border-radius:8px; padding:12px;
        font-size:0.9rem; line-height:1.5; max-height:300px;
        overflow-y:auto; white-space:pre-wrap; word-break:break-word;
    }}
    table {{ width:100%; border-collapse:collapse; }}
    th, td {{ padding:6px; text-align:left; border-bottom:1px solid #eee; }}
    th {{ background:#f0f2f6; font-weight:600; }}
    .footer {{ text-align:center; padding:20px; color:#999; font-size:0.8rem; }}
</style></head>
<body>
    <div class="header">
        <h1>📧 Email Classification Report</h1>
        <p>Generated on {datetime.now().strftime("%B %d, %Y at %H:%M")}</p>
        <div style="margin-top:16px;">
            <span class="prediction-badge">{prediction}</span>
        </div>
        <p style="margin-top:8px;opacity:0.85;">
            Confidence:
             <strong>{f"{confidence:.1f}%" if confidence else "N/A"}</strong>
            &middot; Spam Risk:
             <strong>{f"{spam_risk:.1f}%" if spam_risk else "N/A"}</strong>
        </p>
    </div>

    <div class="section">
        <h3>📝 Email Content</h3>
        <div class="email-content">{escape(email_text[:2000])}</div>
    </div>

    {f'<div class="section">{urls_html}</div>' if urls_html else ""}

    {('<div class="section"><h3>🧠 Explanation</h3>'
     '<p>{}</p></div>'.format(
      escape(explanation_summary))
     if explanation_summary else "")}

    <div class="footer">
        Generated by Spam Email Classifier
         &middot; {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
</body>
</html>"""

    return html
