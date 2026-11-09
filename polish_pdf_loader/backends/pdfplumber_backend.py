from __future__ import annotations

from pathlib import Path
from typing import Any

from polish_pdf_loader.encoding import detect_and_repair


def load_pdf_pdfplumber(
    path: str | Path,
    *,
    repair: bool = True,
    pages: list[int] | None = None,
) -> list[dict[str, Any]]:
    """Load a PDF with pdfplumber, repairing Polish CP1250→CP1252 garbling."""
    try:
        import pdfplumber  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "pdfplumber is required for this backend. "
            "Install it with: pip install polish-pdf-loader[pdfplumber]"
        ) from exc

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    result = []
    with pdfplumber.open(str(path)) as pdf:
        meta = pdf.metadata or {}
        total_pages = len(pdf.pages)
        for page_num, page in enumerate(pdf.pages):
            if pages is not None and page_num not in pages:
                continue
            text = page.extract_text() or ""
            if repair:
                text = detect_and_repair(text)
            result.append(
                {
                    "page": page_num,
                    "text": text,
                    "metadata": {
                        "source": str(path),
                        "page": page_num,
                        "total_pages": total_pages,
                        "title": meta.get("Title", ""),
                        "author": meta.get("Author", ""),
                    },
                }
            )
    return result
