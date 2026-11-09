import pytest
from pathlib import Path

pytest.importorskip("pdfplumber")
from polish_pdf_loader.backends.pdfplumber_backend import load_pdf_pdfplumber  # noqa: E402

FIXTURE = Path(__file__).parent.parent / "data" / "sample_polish.pdf"


@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_loads_pages_as_list():
    pages = load_pdf_pdfplumber(FIXTURE)
    assert isinstance(pages, list)
    assert all("text" in p and "page" in p for p in pages)


@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_polish_chars_present():
    pages = load_pdf_pdfplumber(FIXTURE)
    full = " ".join(p["text"] for p in pages)
    assert any(ch in full for ch in "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_pdf_pdfplumber("nonexistent.pdf")
