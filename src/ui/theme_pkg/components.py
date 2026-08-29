"""Streamlit component style overrides for the Spam Email Classifier.

All CSS rules targeting Streamlit widgets (``stButton``, ``stTabs``,
``stDataFrame``, etc.) and custom UI elements live here.  The module
exports a single ``COMPONENTS_CSS`` string that is assembled into the
full ``THEME_CSS`` by ``light.py``.
"""

COMPONENTS_CSS = """\
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

    .explanation-box {
        background: var(--explanation-bg);
        border: 1px solid var(--explanation-border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: background var(--theme-transition), border-color var(--theme-transition);
    }

    .explanation-box h3 {
        color: var(--text-primary);
        font-size: 1.1rem;
        margin-bottom: 0.8rem;
        transition: color var(--theme-transition);
    }

    .explanation-box p {
        color: var(--text-secondary);
        line-height: 1.6;
        transition: color var(--theme-transition);
    }

    /* ================================================================
       History Table
       ================================================================ */

    .history-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 4px;
    }

    .history-row {
        background-color: var(--card-bg);
        border-radius: 8px;
        transition: background-color var(--theme-transition);
    }

    .history-row:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* ================================================================
       Feature Importance
       ================================================================ */

    .feature-bar-container {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 4px 0;
    }

    .feature-bar-track {
        flex: 1;
        height: 6px;
        background: var(--bar-track);
        border-radius: 3px;
        overflow: hidden;
        transition: background var(--theme-transition);
    }

    .feature-bar-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.3s ease;
    }

    /* ================================================================
       Metrics Row
       ================================================================ */

    .metrics-row {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin: 1rem 0;
    }

    .metric-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        background-color: var(--metric-bg);
        transition: background-color var(--theme-transition), color var(--theme-transition);
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

    @keyframes slideRight {
        from { opacity: 0; transform: translateX(-20px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    /* ================================================================
       Email Stats Bar
       ================================================================ */

    .email-stats {
        display: flex;
        gap: 16px;
        padding: 10px 16px;
        border-radius: 10px;
        background-color: var(--card-bg);
        margin: 0.8rem 0;
        transition: background-color var(--theme-transition);
    }

    .email-stats .stat {
        font-size: 0.85rem;
        color: var(--text-secondary);
        transition: color var(--theme-transition);
    }

    /* ================================================================
       Toast / Notification
       ================================================================ */

    .toast-container {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .toast {
        padding: 12px 20px;
        border-radius: 10px;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        animation: slideRight 0.3s ease;
        transition: background-color var(--theme-transition), color var(--theme-transition);
    }

    .toast-success {
        background-color: var(--accent-green-light);
        color: var(--accent-green);
        border-left: 4px solid var(--accent-green);
    }

    .toast-error {
        background-color: var(--accent-red-light);
        color: var(--accent-red);
        border-left: 4px solid var(--accent-red);
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

    footer a {
        color: #4a90d9 !important;
        text-decoration: none;
        font-weight: 500;
    }

    footer a:hover {
        text-decoration: underline;
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
"""
