"""Integration tests — require tests/data/sample_polish.pdf (auto-generated)."""
from pathlib import Path

import pytest

from polish_pdf_loader import PolishPDFLoader

FIXTURE = Path(__file__).parent / "data" / "sample_polish.pdf"
PAN_TADEUSZ_SNIP = "Litwo! Ojczyzno moja!"


@pytest.mark.integration
@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_pymupdf_loads_polish():
    pytest.importorskip("pymupdf")
    docs = PolishPDFLoader(FIXTURE, backend="pymupdf").load()
    full = " ".join(d.page_content for d in docs)
    assert any(ch in full for ch in "ąćęłńóśźż"), "PyMuPDF garbled text"


@pytest.mark.integration
@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_pdfplumber_loads_polish():
    pytest.importorskip("pdfplumber")
    docs = PolishPDFLoader(FIXTURE, backend="pdfplumber").load()
    full = " ".join(d.page_content for d in docs)
    assert any(ch in full for ch in "ąćęłńóśźż"), "pdfplumber garbled text"


@pytest.mark.integration
@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_pypdf_loads_polish():
    pytest.importorskip("pypdf")
    docs = PolishPDFLoader(FIXTURE, backend="pypdf").load()
    full = " ".join(d.page_content for d in docs)
    assert any(ch in full for ch in "ąćęłńóśźż"), "pypdf garbled text"


@pytest.mark.integration
@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_repair_matches_known_text():
    pytest.importorskip("pymupdf")
    docs = PolishPDFLoader(FIXTURE, backend="pymupdf").load()
    full = " ".join(d.page_content for d in docs)
    assert PAN_TADEUSZ_SNIP in full
