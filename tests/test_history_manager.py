"""Tests for the history manager module."""

import os
import tempfile

import pytest

from src.utils.history_manager import HistoryManager


@pytest.fixture
def hm():
    """Create a HistoryManager with a temporary database path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_history.db")
        manager = HistoryManager(db_path)
        yield manager


class TestHistoryManager:
    """Tests for HistoryManager CRUD operations."""

    def test_add_entry(self, hm):
        entry_id = hm.add_entry(
            email_text="Test email",
            prediction="Spam",
            confidence=95.5,
            spam_risk=95.5,
            model_used="SVM",
            source="manual",
            url_count=2,
            suspicious_urls=1,
        )
        assert entry_id > 0

    def test_get_history_empty(self, hm):
        records = hm.get_history(limit=10)
        assert records == []

    def test_add_and_retrieve(self, hm):
        hm.add_entry(
            email_text="Win a free prize",
            prediction="Spam",
            confidence=99.0,
            source="manual",
        )
        records = hm.get_history(limit=10)
        assert len(records) == 1
        assert records[0]["prediction"] == "Spam"
        assert records[0]["email_text"] == "Win a free prize"

    def test_multiple_entries(self, hm):
        hm.add_entry(email_text="Email 1", prediction="Spam", source="manual")
        hm.add_entry(email_text="Email 2", prediction="Ham", source="batch")
        hm.add_entry(email_text="Email 3", prediction="Spam", source="api")

        records = hm.get_history(limit=10)
        assert len(records) == 3

    def test_prediction_filter(self, hm):
        hm.add_entry(email_text="A", prediction="Spam", source="manual")
        hm.add_entry(email_text="B", prediction="Ham", source="manual")
        hm.add_entry(email_text="C", prediction="Spam", source="manual")

        spam_records = hm.get_history(limit=10, prediction_filter="Spam")
        assert len(spam_records) == 2

        ham_records = hm.get_history(limit=10, prediction_filter="Ham")
        assert len(ham_records) == 1

    def test_source_filter(self, hm):
        hm.add_entry(email_text="A", prediction="Spam", source="manual")
        hm.add_entry(email_text="B", prediction="Ham", source="batch")
        hm.add_entry(email_text="C", prediction="Spam", source="api")

        manual = hm.get_history(limit=10, source_filter="manual")
        assert len(manual) == 1

    def test_search_text(self, hm):
        hm.add_entry(email_text="Free money now", prediction="Spam", source="manual", email_subject="")
        hm.add_entry(email_text="Meeting at 3pm", prediction="Ham", source="manual", email_subject="Meeting")

        results = hm.get_history(limit=10, search_text="money")
        assert len(results) == 1

        results = hm.get_history(limit=10, search_text="Meeting")
        assert len(results) == 1

    def test_days_back_filter(self, hm):
        hm.add_entry(email_text="Old email", prediction="Spam", source="manual")

        # Records from last 1 day should find it
        recent = hm.get_history(limit=10, days_back=1)
        assert len(recent) == 1

    def test_total_count(self, hm):
        assert hm.get_total_count() == 0
        hm.add_entry(email_text="A", prediction="Spam", source="manual")
        hm.add_entry(email_text="B", prediction="Ham", source="manual")
        assert hm.get_total_count() == 2
        assert hm.get_total_count(prediction_filter="Spam") == 1

    def test_get_stats(self, hm):
        hm.add_entry(email_text="A", prediction="Spam", confidence=90.0, spam_risk=90.0, source="manual", url_count=3, suspicious_urls=2)
        hm.add_entry(email_text="B", prediction="Ham", confidence=85.0, spam_risk=15.0, source="manual")

        stats = hm.get_stats(days_back=30)
        assert stats["total"] == 2
        assert stats["spam_count"] == 1
        assert stats["ham_count"] == 1
        assert stats["avg_confidence"] == 87.5  # (90 + 85) / 2
        assert stats["total_urls"] == 3
        assert stats["total_suspicious_urls"] == 2

    def test_clear_history(self, hm):
        hm.add_entry(email_text="A", prediction="Spam", source="manual")
        hm.add_entry(email_text="B", prediction="Ham", source="manual")

        assert hm.get_total_count() == 2
        hm.clear_history()
        assert hm.get_total_count() == 0

    def test_get_entry_by_id(self, hm):
        entry_id = hm.add_entry(email_text="Find me", prediction="Spam", source="manual")
        entry = hm.get_entry_by_id(entry_id)
        assert entry is not None
        assert entry["prediction"] == "Spam"

        missing = hm.get_entry_by_id(99999)
        assert missing is None

    def test_custom_metadata(self, hm):
        meta = {"explanation": "keyword triggered", "top_word": "free"}
        hm.add_entry(
            email_text="Test",
            prediction="Spam",
            source="manual",
            metadata=meta,
        )
        records = hm.get_history(limit=10)
        assert records[0]["metadata"] == meta

    def test_pagination(self, hm):
        for i in range(10):
            hm.add_entry(email_text=f"Email {i}", prediction="Spam" if i % 2 == 0 else "Ham", source="manual")

        page1 = hm.get_history(limit=3, offset=0)
        assert len(page1) == 3

        page2 = hm.get_history(limit=3, offset=3)
        assert len(page2) == 3
        # Should not overlap
        assert page1[0]["id"] != page2[0]["id"]
