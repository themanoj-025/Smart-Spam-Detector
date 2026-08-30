"""Tests for UI helper functions."""


from src.ui.helpers import format_confidence, get_risk_color, get_risk_label


class TestFormatConfidence:
    """Tests for format_confidence."""

    def test_formats_percentage(self) -> None:
        result = format_confidence(0.95)
        assert "95" in result

    def test_formats_zero(self) -> None:
        result = format_confidence(0.0)
        assert "0" in result


class TestGetRiskColor:
    """Tests for get_risk_color."""

    def test_low_risk(self) -> None:
        color = get_risk_color(0.1)
        assert isinstance(color, str)

    def test_high_risk(self) -> None:
        color = get_risk_color(0.9)
        assert isinstance(color, str)


class TestGetRiskLabel:
    """Tests for get_risk_label."""

    def test_spam_label(self) -> None:
        label = get_risk_label("Spam")
        assert isinstance(label, str)

    def test_ham_label(self) -> None:
        label = get_risk_label("Ham")
        assert isinstance(label, str)
