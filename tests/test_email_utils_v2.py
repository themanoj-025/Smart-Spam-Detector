"""Tests for email utility functions."""

import pytest
from email.message import Message

from src.utils.email_utils import extract_body, all_recipients, clean_text


class TestExtractBody:
    """Tests for extract_body."""

    def test_plain_text(self):
        msg = Message()
        msg.set_type("text/plain")
        msg.set_payload("Hello, this is a test email body.")
        body = extract_body(msg)
        assert "test email body" in body

    def test_html_body(self):
        msg = Message()
        msg.set_type("text/html")
        msg.set_payload("<p>Hello <b>world</b></p>")
        body = extract_body(msg)
        assert "Hello" in body
        assert "world" in body
        assert "<b>" not in body

    def test_empty_message(self):
        msg = Message()
        body = extract_body(msg)
        assert body == ""


class TestAllRecipients:
    """Tests for all_recipients."""

    def test_from_and_to(self):
        msg = Message()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        recipients = all_recipients(msg)
        assert "sender@example.com" in recipients
        assert "recipient@example.com" in recipients

    def test_cc(self):
        msg = Message()
        msg["From"] = "a@x.com"
        msg["To"] = "b@x.com"
        msg["Cc"] = "c@x.com"
        recipients = all_recipients(msg)
        assert "c@x.com" in recipients

    def test_deduplication(self):
        msg = Message()
        msg["From"] = "a@x.com"
        msg["To"] = "a@x.com"
        recipients = all_recipients(msg)
        # Should be deduplicated
        assert recipients.count("a@x.com") == 1


class TestCleanText:
    """Tests for clean_text."""

    def test_none_passthrough(self):
        assert clean_text(None) is None

    def test_integer_passthrough(self):
        assert clean_text(42) == 42

    def test_formula_injection_escape(self):
        result = clean_text("=SUM(A1:A10)")
        assert result.startswith("'")

    def test_control_char_removal(self):
        result = clean_text("hello\x00world")
        assert "\x00" not in result

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_long_text_truncated(self):
        long_text = "a" * 40000
        result = clean_text(long_text)
        assert len(result) <= 32767

    def test_plus_prefix_escaped(self):
        result = clean_text("+cmd")
        assert result.startswith("'")

    def test_minus_prefix_escaped(self):
        result = clean_text("-cmd")
        assert result.startswith("'")

    def test_at_prefix_escaped(self):
        result = clean_text("@cmd")
        assert result.startswith("'")
