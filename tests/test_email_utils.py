"""Tests for email utility functions."""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.utils.email_utils import clean_text, extract_body


class TestCleanText:
    """Tests for clean_text function."""

    def test_clean_normal_text(self) -> None:
        """Test that normal text is unchanged."""
        text = "Hello, this is a normal email."
        assert clean_text(text) == text

    def test_clean_special_chars(self) -> None:
        """Test removal of special characters."""
        text = "Hello\u200bworld"  # zero-width space
        result = clean_text(text)
        assert "\u200b" not in result

    def test_clean_excel_injection(self) -> None:
        """Test Excel injection prevention."""
        assert clean_text("=CMD") == "'=CMD"
        assert clean_text("+FORMULA") == "'+FORMULA"
        assert clean_text("-DANGER") == "'-DANGER"

    def test_clean_non_string(self) -> None:
        """Test non-string input returns as-is."""
        assert clean_text(123) == 123
        assert clean_text(None) is None


class TestExtractBody:
    """Tests for extract_body function."""

    def test_extract_plain_text(self) -> None:
        """Test extracting body from plain text email."""
        msg = MIMEText("Hello, this is a test email.")
        body = extract_body(msg)
        assert "Hello, this is a test email." in body

    def test_extract_html(self) -> None:
        """Test extracting body from HTML email."""
        html = "<html><body><p>Hello <b>World</b></p></body></html>"
        msg = MIMEText(html, "html")
        body = extract_body(msg)
        assert "Hello" in body
        assert "World" in body

    def test_extract_multipart(self) -> None:
        """Test extracting body from multipart email."""
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText("Plain text version", "plain"))
        msg.attach(MIMEText("<p>HTML version</p>", "html"))

        body = extract_body(msg)
        # Should extract at least one of the parts
        assert body
