"""URL analysis module for extracting and scoring suspicious links in emails.

Extracts all URLs from email text, checks them against known spam patterns,
suspicious TLDs, shortened URLs, and IP-address hosts. Provides a risk score
per URL and an overall email risk level.
"""

import re
import socket
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Known suspicious TLDs and patterns
# ---------------------------------------------------------------------------
SUSPICIOUS_TLDS = {
    ".tk", ".ml", ".ga", ".cf", ".gq",  # Free/abused TLDs
    ".xyz", ".top", ".club", ".work", ".date", ".men", ".loan",
    ".download", ".review", ".stream", ".bid", ".trade", ".webcam",
    ".science", ".party", ".racing", ".win", ".vip",
}

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "confirm",
    "password", "credential", "banking", "paypal", "refund",
    "prize", "winner", "lottery", "inheritance", "cryptocurrency",
    "bitcoin", "wallet", "investment", "bonus", "free-money",
    "claim", "urgent", "action-required", "suspended",
]

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "is.gd", "buff.ly", "tiny.cc", "lc.chat", "bl.ink",
    "shorturl.at", "cutt.ly", "rb.gy", "short.link",
    "click", "shortcm.xyz", "shorte.st", "3e8.eu",
}

# ---------------------------------------------------------------------------
# Regex for URL extraction
# ---------------------------------------------------------------------------
URL_PATTERN = re.compile(
    r'(?:https?://|www\d?\.|(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}/)'
    r'(?:[^\s()<>\[\]{}|\\^`"]+|(?:\([^\s()<>]+\)))',
    re.IGNORECASE
)


def extract_urls(text: str) -> List[str]:
    """Extract all unique URLs from the given text.

    Args:
        text: Email body text to scan.

    Returns:
        List of unique normalized URLs found in the text.
    """
    if not text:
        return []
    matches = URL_PATTERN.findall(text)
    seen = set()
    urls = []
    for url in matches:
        normalized = url.strip().rstrip(".,;:!?")
        if not normalized.startswith(("http://", "https://")):
            normalized = "https://" + normalized
        if normalized not in seen:
            seen.add(normalized)
            urls.append(normalized)
    return urls


def analyze_url(url: str) -> Dict[str, Any]:
    """Analyze a single URL for suspicious characteristics.

    Args:
        url: The URL to analyze.

    Returns:
        Dict with keys: url, parsed, is_suspicious_tld, is_shortened,
        has_suspicious_keywords, is_ip_host, risk_score, flags.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    path = parsed.path + " " + parsed.query
    flags = []
    risk_score = 0.0

    # Check TLD
    tld = None
    for suspected in SUSPICIOUS_TLDS:
        if hostname.endswith(suspected) or hostname.endswith(suspected.lower()):
            tld = suspected
            flags.append(f"suspicious TLD: {suspected}")
            risk_score += 25.0
            break

    # Check shortened URLs
    is_shortened = hostname.lower() in SHORTENER_DOMAINS
    if is_shortened:
        flags.append("shortened URL")
        risk_score += 20.0

    # Check IP address as hostname
    is_ip_host = _is_ip_address(hostname)
    if is_ip_host:
        flags.append("IP address host")
        risk_score += 30.0

    # Check suspicious keywords
    found_keywords = []
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in path.lower() or kw in hostname.lower():
            found_keywords.append(kw)
            risk_score += 8.0
    if found_keywords:
        flags.append(f"suspicious keywords: {', '.join(found_keywords[:5])}")

    # Check excessive subdomains
    subdomain_count = hostname.count(".") - 1  # subtract the TLD
    if subdomain_count >= 3:
        flags.append(f"excessive subdomains ({subdomain_count})")
        risk_score += 10.0

    # Check for non-https
    if parsed.scheme and parsed.scheme != "https":
        flags.append("non-HTTPS")
        risk_score += 5.0

    # Check for unusual port
    if parsed.port and parsed.port not in (80, 443):
        flags.append(f"unusual port: {parsed.port}")
        risk_score += 15.0

    # Clamp risk score
    risk_score = min(risk_score, 100.0)

    return {
        "url": url,
        "parsed": parsed.geturl(),
        "hostname": hostname,
        "tld": tld,
        "is_suspicious_tld": tld is not None,
        "is_shortened": is_shortened,
        "is_ip_host": is_ip_host,
        "has_suspicious_keywords": len(found_keywords) > 0,
        "suspicious_keywords": found_keywords,
        "flags": flags,
        "risk_score": round(risk_score, 1),
        "subdomain_count": subdomain_count,
    }


def analyze_urls_in_text(text: str) -> Dict[str, Any]:
    """Extract and analyze all URLs in an email text.

    Args:
        text: Email body text to scan.

    Returns:
        Dict with keys: total_urls, suspicious_count, risk_level
        (low/medium/high), urls (list of analysis results), and
        overall_risk_score (0-100).
    """
    urls = extract_urls(text)
    if not urls:
        return {
            "total_urls": 0,
            "suspicious_count": 0,
            "risk_level": "none",
            "overall_risk_score": 0.0,
            "urls": [],
        }

    analyzed = [analyze_url(url) for url in urls]
    suspicious = [a for a in analyzed if a["risk_score"] >= 15]

    # Overall email risk from URLs
    if not analyzed:
        overall_score = 0.0
    else:
        # Average of top 3 highest risk scores
        sorted_scores = sorted(a["risk_score"] for a in analyzed)[:3]
        overall_score = sum(sorted_scores) / len(sorted_scores)

    # Determine risk level
    if overall_score >= 50:
        risk_level = "high"
    elif overall_score >= 20:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "total_urls": len(urls),
        "suspicious_count": len(suspicious),
        "risk_level": risk_level,
        "overall_risk_score": round(overall_score, 1),
        "urls": analyzed,
    }


def _is_ip_address(hostname: str) -> bool:
    """Check if a hostname is an IP address."""
    try:
        socket.inet_aton(hostname)
        return True
    except (socket.error, OSError):
        # Also check for IPv6
        try:
            socket.inet_pton(socket.AF_INET6, hostname)
            return True
        except (socket.error, OSError):
            return False


def get_url_risk_badge(risk_score: float) -> str:
    """Get an HTML badge string for a URL risk score."""
    if risk_score >= 50:
        return f'<span style="background:#f44336;color:#fff;padding:2px 8px;border-radius:10px;font-size:0.75rem;font-weight:600">{risk_score:.0f}% High</span>'
    elif risk_score >= 20:
        return f'<span style="background:#ffa726;color:#fff;padding:2px 8px;border-radius:10px;font-size:0.75rem;font-weight:600">{risk_score:.0f}% Medium</span>'
    elif risk_score > 0:
        return f'<span style="background:#66bb6a;color:#fff;padding:2px 8px;border-radius:10px;font-size:0.75rem;font-weight:600">{risk_score:.0f}% Low</span>'
    return ""
