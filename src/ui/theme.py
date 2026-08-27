"""Theme CSS for the Spam Email Classifier."""


THEME_CSS = '''

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



    /* Transition timing — fast for snappy feel */

    --theme-transition: 0.2s ease;

    --hover-transition: 0.15s cubic-bezier(0.4, 0, 0.2, 1);



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

        background: var(--metric-bg);

        border-radius: 10px;

        margin: 0.5rem 0;

        animation: fadeIn 0.3s ease;

        transition: background-color var(--theme-transition);

    }

    .email-stat-item {

        display: flex;

        align-items: center;

        gap: 5px;

        font-size: 0.8rem;

        color: var(--text-muted);

        transition: color var(--theme-transition);

    }

    .email-stat-item span.stat-val {

        font-weight: 600;

        color: var(--text-primary);

        transition: color var(--theme-transition);

    }



    /* ================================================================

       Toast / Notification

       ================================================================ */

    .toast-notification {

        padding: 12px 20px;

        border-radius: 12px;

        margin: 0.5rem 0;

        animation: slideRight 0.3s ease;

        font-size: 0.9rem;

        display: flex;

        align-items: center;

        gap: 10px;

        transition: all var(--hover-transition);

    }

    .toast-success {

        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);

        border-left: 4px solid var(--accent-green);

        color: #2e7d32;

    }

    .toast-warning {

        background: linear-gradient(135deg, #fff3e0, #ffe0b2);

        border-left: 4px solid var(--accent-yellow);

        color: #e65100;

    }

    .toast-danger {

        background: linear-gradient(135deg, #ffebee, #ffcdd2);

        border-left: 4px solid var(--accent-red);

        color: #c62828;

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

</style>

'''


DARK_THEME_CSS = '''
<style>

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

</style>
'''
