from __future__ import annotations

from pathlib import Path
from typing import Iterator

from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document

from polish_pdf_loader.postprocess import PostprocessConfig, postprocess

_BACKENDS = {
    "pymupdf": "polish_pdf_loader.backends.pymupdf_backend.load_pdf_pymupdf",
    "pdfplumber": "polish_pdf_loader.backends.pdfplumber_backend.load_pdf_pdfplumber",
    "pypdf": "polish_pdf_loader.backends.pypdf_backend.load_pdf_pypdf",
}


def _get_backend_fn(name: str):
    if name not in _BACKENDS:
        raise ValueError(
            f"Unsupported backend: {name!r}. "
            f"Choose from: {sorted(_BACKENDS)}"
        )
    module_path, fn_name = _BACKENDS[name].rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, fn_name)


class PolishPDFLoader(BaseLoader):
    """LangChain BaseLoader that correctly decodes Polish PDF text.

    Wraps PyMuPDF, pdfplumber or pypdf and applies CP1250→CP1252 encoding
    repair plus optional post-processing before returning Documents.
    """

    def __init__(
        self,
        file_path: str | Path,
        *,
        backend: str = "pymupdf",
        repair: bool = True,
        pages: list[int] | None = None,
        postprocess_config: PostprocessConfig | None = None,
    ) -> None:
        self.file_path = Path(file_path)
        self.backend = backend
        self.repair = repair
        self.pages = pages
        self.postprocess_config = postprocess_config

    def lazy_load(self) -> Iterator[Document]:
        load_fn = _get_backend_fn(self.backend)
        raw_pages = load_fn(self.file_path, repair=self.repair, pages=self.pages)
        for page in raw_pages:
            text = postprocess(page["text"], self.postprocess_config)
            yield Document(page_content=text, metadata=page["metadata"])


class PolishPyMuPDFLoader(PolishPDFLoader):
    """Drop-in replacement for langchain_community PyMuPDFLoader with Polish support."""

    def __init__(self, file_path: str | Path, **kwargs) -> None:
        kwargs.setdefault("backend", "pymupdf")
        super().__init__(file_path, **kwargs)


class PolishPdfPlumberLoader(PolishPDFLoader):
    """Drop-in replacement for langchain_community PDFPlumberLoader with Polish support."""

    def __init__(self, file_path: str | Path, **kwargs) -> None:
        kwargs.setdefault("backend", "pdfplumber")
        super().__init__(file_path, **kwargs)


class PolishPyPDFLoader(PolishPDFLoader):
    """Drop-in replacement for langchain_community PyPDFLoader with Polish support."""

    def __init__(self, file_path: str | Path, **kwargs) -> None:
        kwargs.setdefault("backend", "pypdf")
        super().__init__(file_path, **kwargs)
