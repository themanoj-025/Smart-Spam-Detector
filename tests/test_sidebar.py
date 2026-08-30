"""Tests for sidebar component."""


from src.ui.sidebar import SidebarRenderer


class TestSidebarRenderer:
    """Tests for SidebarRenderer."""

    def test_init(self) -> None:
        renderer = SidebarRenderer()
        assert renderer is not None
