"""Tests for single prediction tab."""

import pytest
from unittest.mock import MagicMock, patch

from src.ui.tab_single import SinglePredictionTab


class TestSinglePredictionTab:
    """Tests for SinglePredictionTab."""

    def test_init(self):
        tab = SinglePredictionTab()
        assert tab is not None
