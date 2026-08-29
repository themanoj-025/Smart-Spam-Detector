"""CSS custom properties (design tokens) for the Spam Email Classifier.

Light-theme defaults are defined here.  Dark-theme overrides live in
``dark.py`` and are injected at runtime when the user toggles the theme.
"""

LIGHT_VARIABLES = """\
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
"""
