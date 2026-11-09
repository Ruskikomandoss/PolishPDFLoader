from __future__ import annotations

from pathlib import Path
from typing import Any

from polish_pdf_loader.encoding import detect_and_repair


def load_pdf_pymupdf(
    path: str | Path,
    *,
    repair: bool = True,
    pages: list[int] | None = None,
) -> list[dict[str, Any]]:
    """Load a PDF with PyMuPDF, repairing Polish CP1250→CP1252 garbling."""
    try:
        import pymupdf  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "PyMuPDF is required for this backend. "
            "Install it with: pip install polish-pdf-loader[pymupdf]"
        ) from exc

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    doc = pymupdf.open(str(path))
    meta = doc.metadata or {}
    total_pages = doc.page_count

    result = []
    for page_num in range(total_pages):
        if pages is not None and page_num not in pages:
            continue
        page = doc[page_num]
        text = page.get_text("text") or ""
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
                    "title": meta.get("title", ""),
                    "author": meta.get("author", ""),
                },
            }
        )
    doc.close()
    return result
