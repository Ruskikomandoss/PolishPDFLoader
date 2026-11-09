import pytest
from pathlib import Path

pymupdf = pytest.importorskip("pymupdf")
from polish_pdf_loader.backends.pymupdf_backend import load_pdf_pymupdf  # noqa: E402

FIXTURE = Path(__file__).parent.parent / "data" / "sample_polish.pdf"


@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_loads_pages_as_list():
    pages = load_pdf_pymupdf(FIXTURE)
    assert isinstance(pages, list)
    assert all("text" in p and "page" in p for p in pages)


@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_polish_chars_present():
    pages = load_pdf_pymupdf(FIXTURE)
    full = " ".join(p["text"] for p in pages)
    assert any(ch in full for ch in "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")


@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_page_subset():
    pages = load_pdf_pymupdf(FIXTURE, pages=[0])
    assert len(pages) == 1
    assert pages[0]["page"] == 0


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_pdf_pymupdf("nonexistent.pdf")
