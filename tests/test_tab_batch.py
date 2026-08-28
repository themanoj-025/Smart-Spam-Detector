"""Tests for batch prediction tab."""

import pytest
from unittest.mock import MagicMock, patch

from src.ui.tab_batch import BatchPredictionTab


class TestBatchPredictionTab:
    """Tests for BatchPredictionTab."""

    def test_init(self):
        tab = BatchPredictionTab()
        assert tab is not None
