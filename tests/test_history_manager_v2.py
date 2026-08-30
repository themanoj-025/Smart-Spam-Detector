"""Tests for history manager with SQLite storage."""

import os
import tempfile
import time

import pytest

from src.utils.history_manager import HistoryManager


@pytest.fixture
def history_db() -> None:
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_history.db")
        hm = HistoryManager(db_path)
        yield hm


class TestHistoryManager:
    """Tests for HistoryManager CRUD operations."""

    def test_add_and_get_entry(self, history_db) -> None:
        record_id = history_db.add_entry(
            email_text="Test email content",
            prediction="Spam",
            confidence=95.0,
            spam_risk=80.0,
            model_used="test_model",
            source="manual",
        )
        assert record_id > 0
        entry = history_db.get_entry_by_id(record_id)
        assert entry is not None
        assert entry["prediction"] == "Spam"
        assert entry["confidence"] == 95.0

    def test_get_history(self, history_db) -> None:
        history_db.add_entry("email1", "Spam", 90.0)
        history_db.add_entry("email2", "Ham", 85.0)
        history_db.add_entry("email3", "Spam", 92.0)
        history = history_db.get_history()
        assert len(history) == 3

    def test_get_history_with_filter(self, history_db) -> None:
        history_db.add_entry("email1", "Spam", 90.0)
        history_db.add_entry("email2", "Ham", 85.0)
        spam_only = history_db.get_history(prediction_filter="Spam")
        assert len(spam_only) == 1
        assert spam_only[0]["prediction"] == "Spam"

    def test_get_total_count(self, history_db) -> None:
        history_db.add_entry("email1", "Spam")
        history_db.add_entry("email2", "Ham")
        assert history_db.get_total_count() == 2
        assert history_db.get_total_count(prediction_filter="Spam") == 1

    def test_get_stats(self, history_db) -> None:
        history_db.add_entry("email1", "Spam", 90.0, 80.0)
        history_db.add_entry("email2", "Ham", 85.0, 20.0)
        stats = history_db.get_stats(days_back=365)
        assert stats["total"] == 2
        assert stats["spam_count"] == 1
        assert stats["ham_count"] == 1

    def test_clear_history(self, history_db) -> None:
        history_db.add_entry("email1", "Spam")
        history_db.add_entry("email2", "Ham")
        deleted = history_db.clear_history()
        assert deleted == 2
        assert history_db.get_total_count() == 0

    def test_get_entry_nonexistent(self, history_db) -> None:
        assert history_db.get_entry_by_id(99999) is None

    def test_search_text(self, history_db) -> None:
        history_db.add_entry("Buy cheap pills now", "Spam", email_subject="Special Offer")
        history_db.add_entry("Meeting tomorrow at 10", "Ham", email_subject="Re: Meeting")
        results = history_db.get_history(search_text="pills")
        assert len(results) == 1
        assert "pills" in results[0]["email_text"]

    def test_days_back_filter(self, history_db) -> None:
        history_db.add_entry("recent email", "Spam")
        old_id = history_db.add_entry("old email", "Ham")
        # Mark as old by updating timestamp
        import sqlite3
        conn = sqlite3.connect(history_db.db_path)
        conn.execute("UPDATE classifications SET timestamp = ? WHERE id = ?",
                     (time.time() - 30 * 86400, old_id))
        conn.commit()
        conn.close()
        recent = history_db.get_history(days_back=1)
        assert len(recent) == 1
