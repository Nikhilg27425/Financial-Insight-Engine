import re
from typing import Optional, Tuple

UNIT_SCALES = {
    "crore": 1e7,
    "cr": 1e7,
    "cr.": 1e7,
    "lakh": 1e5,
    "lac": 1e5,
    "lacs": 1e5,
    "thousand": 1e3,
    "million": 1e6,
    "mn": 1e6,
    "billion": 1e9,
    "bn": 1e9,
}

def detect_scale_from_text(text: str) -> float:
    """
    Detect scale keyword in text (crore, lakh, million, etc.) and return corresponding multiplier.
    Defaults to crore.
    """
    if not text:
        return UNIT_SCALES["crore"]
    lowered = text.lower()
    if "crore" in lowered or "` crore" in lowered or "₹ crore" in lowered:
        return UNIT_SCALES["crore"]
    if "lakh" in lowered or " lac " in lowered or "lacs" in lowered:
        return UNIT_SCALES["lakh"]
    if "million" in lowered or "mn" in lowered:
        return UNIT_SCALES["million"]
    if "billion" in lowered or "bn" in lowered:
        return UNIT_SCALES["billion"]
    return UNIT_SCALES["crore"]

def _strip_brackets_and_signs(s: str) -> Tuple[str, bool]:
    """
    Remove parentheses or leading minus, and return cleaned string and negative flag.
    """
    negative = False
    s = s.strip()
    if not s:
        return "", False
    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1].strip()
    if s.startswith("-"):
        negative = True
        s = s[1:].strip()
    return s, negative

def parse_number_string_to_crore(raw: Optional[str]) -> Optional[float]:
    """
    Convert raw numeric string to float in report's scale units (crore/lakh).
    Returns None if it cannot parse.
    """
    if not raw or not isinstance(raw, str):
        return None
    s = raw.strip()
    # known non-numeric markers
    if s in ("-", "—", "–", "nil", "na", "n/a", "*", ""):
        return None
    # remove trailing non-numeric characters
    s = re.sub(r"[^\d\(\)\.\,\-]+$", "", s)
    s, negative = _strip_brackets_and_signs(s)
    s = s.replace(",", "").replace("₹", "").replace("`", "").strip()
    s = s.replace("O", "0").replace("l", "1") #this line
    if s.count(".") > 1:
        parts = s.split(".")
        s = parts[0] + "." + "".join(parts[1:])
    s = re.sub(r"[a-zA-Z]+$", "", s).strip()
    if not re.search(r"\d", s): #this line
        return None
    try:
        val = float(s)
    except ValueError:
        return None
    return -val if negative else val

def scale_crore_to_rupees(value_crore: Optional[float], scale: float) -> Optional[int]:
    """
    Convert value in crores/lakhs to absolute rupees (int).
    """
    if value_crore is None:
        return None
    try:
        return int(round(value_crore * scale))
    except Exception:
        return None

def find_first_number_in_line(line: str) -> Optional[float]:
    """
    Find first numeric token in line and parse it (in scale units).
    """
    if not line:
        return None
    matches = re.findall(r"[+\-]?\(?[0-9][0-9\.,]*\)?", line)
    for token in matches:
        num = parse_number_string_to_crore(token)
        if num is not None:
            return num
    return None