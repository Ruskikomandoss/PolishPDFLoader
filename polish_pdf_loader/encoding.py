"""
Encoding detection and repair for Polish PDF text.

Background: PDF extraction tools (PyMuPDF, pdfplumber) sometimes decode
CP1250-encoded text using CP1252 instead, producing garbled Polish
characters:  ś→œ  ł→³  ą→¹  ć→æ  ę→ê  ź→Ÿ  Ś→Œ

The repair: re-encode the string to its original CP1252 bytes, then
decode those bytes as CP1250.
"""

# Unambiguous indicators of CP1250→CP1252 garbling.
# _ANCHOR_MARKERS (œ Ÿ Œ) are essentially absent from normal prose and
# MUST be present before any repair fires — this prevents false positives
# on academic PDFs with superscript footnotes (¹) or exponents (³).
# _GARBLED_MARKERS includes ¹ and ³ as supporting density evidence once
# an anchor is confirmed; æ and ê are intentionally excluded because they
# appear legitimately in French/Latin loanwords common in Polish text.
_ANCHOR_MARKERS = frozenset("œŸŒ")  # œ Ÿ Œ
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
    # Require at least one unambiguous anchor marker to avoid false positives
    # on texts that happen to contain superscript digits (¹ ³) only.
    if not any(c in _ANCHOR_MARKERS for c in text):
        return False
    marker_count = sum(1 for c in text if c in _GARBLED_MARKERS)
    return marker_count >= 2 and (marker_count / len(text)) > 0.002


def detect_and_repair(text: str) -> str:
    """Repair CP1250-as-CP1252 garbling when detected; pass UTF-8 through unchanged."""
    if is_polish_garbled(text):
        return repair_cp1250_as_latin1(text)
    return text
