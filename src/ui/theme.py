"""Theme CSS constants for the Streamlit dashboard.

Canonical definitions live in ``src/ui/theme_pkg`` (dark/light variants);
this module re-exports them under the import path the app and tests use.
"""

from src.ui.theme_pkg.dark import DARK_THEME_CSS
from src.ui.theme_pkg.light import THEME_CSS

__all__ = ["DARK_THEME_CSS", "THEME_CSS"]
