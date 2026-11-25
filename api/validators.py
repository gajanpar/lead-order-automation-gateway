import re

_ALLOWED_CHARS_RE = re.compile(r"^[+\d\s().-]+$")
_E164_RE = re.compile(r"^\+[1-9]\d{7,14}$")
_ID_LOCAL_RE = re.compile(r"^\+62[1-9]\d{7,12}$")


def normalize_whatsapp_number(raw_number: str) -> str:
    """Normalize Indonesian and E.164 WhatsApp numbers into canonical +<country><digits> format.

    Rejects numbers with unexpected characters, ambiguous local formats, or invalid lengths
    instead of silently mangling them.
    """
    cleaned = raw_number.strip()
    if not cleaned:
        raise ValueError("WhatsApp number cannot be empty.")

    if not _ALLOWED_CHARS_RE.match(cleaned):
        raise ValueError("WhatsApp number contains invalid characters.")

    # Remove common visual separators while keeping '+' only if it is leading
    compact = re.sub(r"[\s().-]", "", cleaned)
    if "+" in compact[1:]:
        raise ValueError("Plus sign '+' may only appear at the beginning of the number.")

    if compact.startswith("00"):
        compact = "+" + compact[2:]

    if compact.startswith("+620"):
        normalized = "+62" + compact[4:]
    elif compact.startswith("+62"):
        normalized = compact
    elif compact.startswith("620"):
        normalized = "+62" + compact[3:]
    elif compact.startswith("62"):
        normalized = "+" + compact
    elif compact.startswith("0"):
        normalized = "+62" + compact[1:]
    elif compact.startswith("+"):
        normalized = compact
    else:
        raise ValueError(
            "Ambiguous phone number format. Use Indonesian '08...' or international '+...' format."
        )

    if normalized.startswith("+62"):
        if not _ID_LOCAL_RE.match(normalized):
            raise ValueError("Invalid Indonesian WhatsApp number length or prefix.")
    elif not _E164_RE.match(normalized):
        raise ValueError("Invalid international E.164 WhatsApp number format.")

    return normalized
