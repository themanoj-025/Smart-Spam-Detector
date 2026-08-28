"""Tests for sidebar component."""

import pytest
from unittest.mock import MagicMock, patch

from src.ui.sidebar import SidebarRenderer


class TestSidebarRenderer:
    """Tests for SidebarRenderer."""

    def test_init(self):
        renderer = SidebarRenderer()
        assert renderer is not None
