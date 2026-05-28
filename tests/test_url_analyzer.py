"""Tests for the URL analyzer module."""

import pytest
from src.utils.url_analyzer import (
    extract_urls,
    analyze_url,
    analyze_urls_in_text,
    _is_ip_address,
)


class TestExtractUrls:
    """Tests for extract_urls function."""

    def test_no_urls(self):
        assert extract_urls("Hello, this is a normal email.") == []

    def test_empty_text(self):
        assert extract_urls("") == []
        assert extract_urls(None) == []

    def test_single_url(self):
        urls = extract_urls("Check this out: https://example.com")
        assert len(urls) == 1
        assert "example.com" in urls[0]

    def test_multiple_urls(self):
        text = "Visit https://example.com and http://test.org for info"
        urls = extract_urls(text)
        assert len(urls) == 2

    def test_url_without_scheme(self):
        urls = extract_urls("Go to www.example.com/page")
        assert len(urls) >= 1

    def test_duplicate_urls(self):
        text = "Link: https://example.com and also https://example.com"
        urls = extract_urls(text)
        assert len(urls) == 1  # Deduplicated

    def test_url_with_path_and_query(self):
        text = "See https://example.com/path?q=1&r=2"
        urls = extract_urls(text)
        assert len(urls) == 1
        assert "path" in urls[0]


class TestIsIpAddress:
    """Tests for _is_ip_address helper."""

    def test_ipv4(self):
        assert _is_ip_address("192.168.1.1") is True

    def test_invalid_ip(self):
        assert _is_ip_address("example.com") is False

    def test_localhost(self):
        assert _is_ip_address("127.0.0.1") is True


class TestAnalyzeUrl:
    """Tests for analyze_url function."""

    def test_normal_url_low_risk(self):
        result = analyze_url("https://example.com/page")
        assert result["risk_score"] < 20
        assert result["is_suspicious_tld"] is False
        assert result["is_shortened"] is False
        assert result["is_ip_host"] is False

    def test_suspicious_tld(self):
        result = analyze_url("https://example.tk/page")
        assert result["is_suspicious_tld"] is True
        assert result["risk_score"] >= 25

    def test_shortened_url(self):
        result = analyze_url("https://bit.ly/abc123")
        assert result["is_shortened"] is True
        assert result["risk_score"] >= 20

    def test_ip_host(self):
        result = analyze_url("http://192.168.1.1/admin")
        assert result["is_ip_host"] is True
        assert result["risk_score"] >= 30

    def test_suspicious_keywords(self):
        result = analyze_url("https://example.com/login/verify/account")
        assert result["has_suspicious_keywords"] is True
        assert "login" in result["suspicious_keywords"]

    def test_non_https(self):
        result = analyze_url("http://example.com")
        # HTTP should add some risk
        risk_no_http = analyze_url("https://example.com")["risk_score"]
        assert result["risk_score"] > risk_no_http


class TestAnalyzeUrlsInText:
    """Tests for analyze_urls_in_text function."""

    def test_no_urls(self):
        result = analyze_urls_in_text("Hello world")
        assert result["total_urls"] == 0
        assert result["risk_level"] == "none"

    def test_safe_urls(self):
        result = analyze_urls_in_text("Check https://github.com and https://docs.python.org")
        assert result["total_urls"] == 2
        assert result["suspicious_count"] == 0

    def test_suspicious_urls(self):
        result = analyze_urls_in_text("Click http://bit.ly/prize and https://suspicious.tk/login")
        assert result["total_urls"] == 2
        assert result["suspicious_count"] >= 1
        assert result["risk_level"] in ("medium", "high")

    def test_overall_structure(self):
        result = analyze_urls_in_text("Visit https://example.com")
        assert "total_urls" in result
        assert "suspicious_count" in result
        assert "risk_level" in result
        assert "overall_risk_score" in result
        assert "urls" in result
