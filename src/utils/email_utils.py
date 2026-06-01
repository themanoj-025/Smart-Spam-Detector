import re
from html import unescape
from email.message import Message
from email.utils import getaddresses
from typing import Union
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------------
# Function to extract email body content
# ----------------------------------------------------------------------------


def extract_body(msg: Message) -> str:
    """Extract the readable text body from an email message.

    Handles both multipart and single-part emails. Strips HTML tags and
    normalizes whitespace.

    Args:
        msg: An email.message.Message object.

    Returns:
        Cleaned text body of the email.
    """
    texts: list[str] = []

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() in ("text/plain", "text/html"):
                payload = part.get_payload(decode=True)
                if payload:
                    text = payload.decode(errors="ignore")
                    text = unescape(text)
                    text = BeautifulSoup(text, "html.parser").get_text(" ")
                    texts.append(text)
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            text = unescape(payload.decode(errors="ignore"))
            text = BeautifulSoup(text, "html.parser").get_text(" ")
            texts.append(text)

    clean = " ".join(texts)
    clean = re.sub(r'\\+', ' ', clean)
    clean = re.sub(r'[\r\n\t]+', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()

# ----------------------------------------------------------------------------
# Function to extract all recipients from email headers
# ----------------------------------------------------------------------------


def all_recipients(msg: Message) -> str:
    """Extract all unique recipient email addresses from an email message.

    Args:
        msg: An email.message.Message object.

    Returns:
        Comma-separated string of unique email addresses.
    """
    fields: list[str] = []
    for h in ["From", "To", "Cc", "Bcc"]:
        fields.extend(getaddresses([msg.get(h, "")]))
    return ", ".join(sorted(set(addr for _, addr in fields if addr)))

# ----------------------------------------------------------------------------
# Function to clean text for Excel compatibility and model input
# ----------------------------------------------------------------------------


def clean_text(text: Union[str, None]) -> Union[str, None]:
    """Clean text for model input and Excel compatibility.

    Removes control characters, zero-width spaces, and truncates to
    Excel's cell limit. Also escapes characters that trigger formula
    injection in spreadsheets.

    Args:
        text: The text to clean. If not a string, returned as-is.

    Returns:
        Cleaned string, or the original value if not a string.
    """
    if not isinstance(text, str):
        return text
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\u200B\u200C\u200D\u200E\u200F\uFEFF]', '', text)
    text = text.encode("utf-16", "surrogatepass").decode("utf-16", "ignore")
    text = text[:32767]
    if text.startswith(("=", "+", "-", "@")):
        text = "'" + text
    return text
