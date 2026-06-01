"""Tests for email utility functions."""

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.utils.email_utils import extract_body, clean_text


class TestCleanText:
    """Tests for clean_text function."""

    def test_clean_normal_text(self):
        """Test that normal text is unchanged."""
        text = "Hello, this is a normal email."
        assert clean_text(text) == text

    def test_clean_special_chars(self):
        """Test removal of special characters."""
        text = "Hello\u200Bworld"  # zero-width space
        result = clean_text(text)
        assert "\u200B" not in result

    def test_clean_excel_injection(self):
        """Test Excel injection prevention."""
        assert clean_text("=CMD") == "'=CMD"
        assert clean_text("+FORMULA") == "'+FORMULA"
        assert clean_text("-DANGER") == "'-DANGER"

    def test_clean_non_string(self):
        """Test non-string input returns as-is."""
        assert clean_text(123) == 123
        assert clean_text(None) is None


class TestExtractBody:
    """Tests for extract_body function."""

    def test_extract_plain_text(self):
        """Test extracting body from plain text email."""
        msg = MIMEText("Hello, this is a test email.")
        body = extract_body(msg)
        assert "Hello, this is a test email." in body

    def test_extract_html(self):
        """Test extracting body from HTML email."""
        html = "<html><body><p>Hello <b>World</b></p></body></html>"
        msg = MIMEText(html, 'html')
        body = extract_body(msg)
        assert "Hello" in body
        assert "World" in body

    def test_extract_multipart(self):
        """Test extracting body from multipart email."""
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText("Plain text version", 'plain'))
        msg.attach(MIMEText("<p>HTML version</p>", 'html'))
        
        body = extract_body(msg)
        # Should extract at least one of the parts
        assert body
