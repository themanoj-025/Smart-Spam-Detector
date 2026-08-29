"""Theme CSS for the Spam Email Classifier.

Assembles the full ``THEME_CSS`` string from:
- ``variables.py`` — CSS custom properties (light-theme design tokens)
- ``components.py`` — Streamlit widget and custom UI style overrides
"""

from .variables import LIGHT_VARIABLES
from .components import COMPONENTS_CSS

# ─── Assembled Theme ──────────────────────────────────────
# The single string injected into Streamlit via ``st.markdown(…, unsafe_allow_html=True)``.

THEME_CSS = f"""\
<style>

{LIGHT_VARIABLES}

{COMPONENTS_CSS}

</style>

"""
