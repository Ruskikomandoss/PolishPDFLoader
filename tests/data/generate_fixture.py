"""
Generate tests/data/sample_polish.pdf for integration tests.

Page 1: Pan Tadeusz opening in correct UTF-8 (clean path)
Page 2: Same text with garbled characters simulating CP1250→CP1252 misread
"""
from __future__ import annotations

from pathlib import Path


PAN_TADEUSZ = (
    "Litwo! Ojczyzno moja! ty jesteś jak zdrowie.\n"
    "Ile cię trzeba cenić, ten tylko się dowie,\n"
    "Kto cię stracił. Dziś piękność twą w całej ozdobie\n"
    "Widzę i opisuję, bo tęsknię po tobie."
)

PAN_TADEUSZ_GARBLED = (
    "Litwo! Ojczyzno moja! ty jesteœ jak zdrowie.\n"
    "Ile ciê trzeba ceniæ, ten tylko siê dowie,\n"
    "Kto ciê straci³. Dziœ piêknoœæ tw¹ w ca³ej ozdobie\n"
    "Widzê i opisujê, bo têskniê po tobie."
)

OUT = Path(__file__).parent / "sample_polish.pdf"


def generate(out: Path = OUT) -> None:
    try:
        from fpdf import FPDF  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "fpdf2 is required to generate test fixtures. "
            "Install it with: pip install fpdf2"
        ) from exc

    # Find a system TTF that covers Polish glyphs (DejaVu is standard on Linux)
    _FONT_CANDIDATES = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",  # macOS fallback
    ]
    unicode_font_path = next(
        (p for p in _FONT_CANDIDATES if Path(p).exists()), None
    )

    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)

    # Page 1 — correct UTF-8 Polish text (requires Unicode font)
    pdf.add_page()
    if unicode_font_path:
        pdf.add_font("Unicode", fname=unicode_font_path)
        pdf.set_font("Unicode", size=12)
    else:
        pdf.set_font("Helvetica", size=12)
    pdf.set_xy(10, 10)
    # Encode only Latin-1 safe chars if no Unicode font available
    text1 = (
        PAN_TADEUSZ
        if unicode_font_path
        else PAN_TADEUSZ.encode("latin-1", errors="replace").decode("latin-1")
    )
    pdf.multi_cell(190, 8, text1)

    # Page 2 — garbled text (simulates CP1250 bytes decoded as CP1252)
    # All garbled chars are in Latin-1 range, so Helvetica works fine
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.set_xy(10, 10)
    safe = PAN_TADEUSZ_GARBLED.encode("latin-1", errors="replace").decode("latin-1")
    pdf.multi_cell(190, 8, safe)

    pdf.output(str(out))


if __name__ == "__main__":
    generate()
    print(f"Fixture written to {OUT}")
