"""
Encoding detection and repair for Polish PDF text.

Background: PDF extraction tools (PyMuPDF, pdfplumber) sometimes decode
CP1250-encoded text using CP1252 instead, producing garbled Polish
characters:  ś→œ  ł→³  ą→¹  ć→æ  ę→ê  ź→Ÿ  Ś→Œ

The repair: re-encode the string to its original CP1252 bytes, then
decode those bytes as CP1250.
"""

# Characters that only appear when CP1250 bytes were decoded as CP1252.
# They are extremely rare in legitimate Polish prose.
_GARBLED_MARKERS = frozenset("œ³¹ŸŒ")  # œ ³ ¹ Ÿ Œ

_CLEAN_POLISH = frozenset("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")


def repair_cp1250_as_latin1(text: str) -> str:
    """Re-encode CP1252 → bytes → decode as CP1250, restoring Polish chars."""
    return text.encode("cp1252", errors="replace").decode("cp1250", errors="replace")


def is_polish_garbled(text: str) -> bool:
    """Return True when text shows the CP1250-decoded-as-CP1252 pattern."""
    if not text:
        return False
    if any(c in _CLEAN_POLISH for c in text):
        return False
    marker_count = sum(1 for c in text if c in _GARBLED_MARKERS)
    return marker_count >= 2 and (marker_count / len(text)) > 0.001


def detect_and_repair(text: str) -> str:
    """Repair CP1250-as-CP1252 garbling when detected; pass UTF-8 through unchanged."""
    if is_polish_garbled(text):
        return repair_cp1250_as_latin1(text)
    return text
