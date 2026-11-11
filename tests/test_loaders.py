from pathlib import Path

import pytest

pytest.importorskip("pymupdf")
from langchain_core.documents import Document

from polish_pdf_loader import PolishPDFLoader, PolishPyMuPDFLoader

FIXTURE = Path(__file__).parent / "data" / "sample_polish.pdf"


@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_load_returns_documents():
    loader = PolishPDFLoader(FIXTURE)
    docs = loader.load()
    assert all(isinstance(d, Document) for d in docs)


@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_metadata_has_source():
    docs = PolishPDFLoader(FIXTURE).load()
    assert all("source" in d.metadata for d in docs)


@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_lazy_load_yields_documents():
    loader = PolishPDFLoader(FIXTURE)
    docs = list(loader.lazy_load())
    assert len(docs) > 0


@pytest.mark.skipif(not FIXTURE.exists(), reason="test fixture not present")
def test_pymupdfloader_alias():
    docs = PolishPyMuPDFLoader(FIXTURE).load()
    assert len(docs) > 0


def test_unsupported_backend_raises():
    with pytest.raises(ValueError, match="Unsupported backend"):
        PolishPDFLoader("x.pdf", backend="ghostscript").load()
