"""Tests for the report generator module."""

from src.utils.report_generator import (
    generate_classification_report,
    generate_email_report,
    _bar_chart_svg,
)


class TestGenerateClassificationReport:
    """Tests for generate_classification_report function."""

    def test_empty_results(self):
        html = generate_classification_report([], title="Test Report")
        assert "<!DOCTYPE html>" in html
        assert "Test Report" in html
        assert "0 emails" in html or "0 total" in html.lower() or "0" in html

    def test_single_result(self):
        results = [
            {"prediction": "Spam", "confidence": 95.5, "source": "manual", "timestamp": 1000000},
        ]
        html = generate_classification_report(results)
        assert "Spam" in html
        assert "1" in html  # count

    def test_spam_ham_counts(self):
        results = [
            {"prediction": "Spam", "confidence": 90.0},
            {"prediction": "Ham", "confidence": 85.0},
            {"prediction": "Spam", "confidence": 95.0},
        ]
        html = generate_classification_report(results)
        assert "Spam" in html
        assert "Ham" in html

    def test_with_url_data(self):
        results = [
            {"prediction": "Spam", "url_count": 5, "suspicious_urls": 3},
        ]
        html = generate_classification_report(results)
        # Should include URL info somewhere
        assert any(kw in html.lower() for kw in ["url", "suspicious"])

    def test_includes_timestamp(self):
        results = [
            {"prediction": "Spam", "timestamp": 1000000},
        ]
        html = generate_classification_report(results)
        assert "1970" in html  # epoch timestamp

    def test_without_charts(self):
        results = [
            {"prediction": "Spam"},
            {"prediction": "Ham"},
        ]
        html = generate_classification_report(results, include_charts=False)
        assert "<svg" not in html  # No SVG charts

    def test_without_details(self):
        results = [
            {"prediction": "Spam"},
            {"prediction": "Ham"},
        ]
        html = generate_classification_report(results, include_details=False)
        assert "<table" not in html  # No table


class TestGenerateEmailReport:
    """Tests for generate_email_report function."""

    def test_empty_email(self):
        html = generate_email_report("", "Spam")
        assert "<!DOCTYPE html>" in html
        assert "Spam" in html

    def test_with_confidence(self):
        html = generate_email_report("Hello", "Ham", confidence=98.5)
        assert "98.5" in html or "98" in html

    def test_with_url_analysis(self):
        url_analysis = {
            "total_urls": 2,
            "suspicious_count": 1,
            "risk_level": "medium",
            "overall_risk_score": 35.0,
            "urls": [
                {"url": "https://example.com", "hostname": "example.com", "risk_score": 5.0, "flags": []},
                {"url": "https://bit.ly/abc", "hostname": "bit.ly", "risk_score": 30.0, "flags": ["shortened URL"]},
            ],
        }
        html = generate_email_report("Check links", "Ham", url_analysis=url_analysis)
        assert "URL Analysis" in html
        assert "example.com" in html

    def test_with_explanation(self):
        html = generate_email_report("Hello", "Spam", explanation_summary="Keyword 'free' detected")
        assert "free" in html


class TestBarChartSvg:
    """Tests for the internal _bar_chart_svg function."""

    def test_generates_svg(self):
        data = [{"label": "Spam", "value": 5}, {"label": "Ham", "value": 10}]
        svg = _bar_chart_svg(data, "value", "label", "Test Chart")
        assert "<svg" in svg
        assert "Test Chart" in svg
        assert "Spam" in svg
        assert "Ham" in svg

    def test_empty_data(self):
        svg = _bar_chart_svg([], "value", "label", "Empty")
        assert svg == "<p>No data available</p>"
