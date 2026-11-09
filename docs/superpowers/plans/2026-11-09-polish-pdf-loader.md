# PolishPDFLoader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Python library that wraps PyMuPDF, pdfplumber, and pypdf backends to correctly decode Polish-language PDFs — including CP1250 misread as Latin-1 — and exposes drop-in LangChain-compatible document loaders.

**Architecture:** A thin encoding-repair layer sits between each PDF backend and the caller; a unified `PolishPDFLoader` picks a backend via a `backend=` kwarg and returns `langchain_core.documents.Document` objects with correct Unicode text. Each backend is a small adapter module; shared post-processing (hyphenation, whitespace) is a separate pipeline step applied after any backend produces raw text.

**Tech Stack:** Python 3.9+, PyMuPDF (`pymupdf`), pdfplumber, pypdf, langchain-core (for `Document` / `BaseLoader`), chardet (encoding detection fallback), pytest, ruff (lint/format).

**Spec:** This plan is the spec; the reference script is `/home/jan/projects/tokenizer/tadeusz_pdf_txt.py`.

## Global Constraints

- Python 3.9+ (no walrus-only or 3.10+ match patterns in public API)
- Package name: `polish-pdf-loader`; import name: `polish_pdf_loader`
- All public loaders must be `langchain_core.document_loaders.BaseLoader` subclasses
- No mandatory dependency on a specific backend: each backend is an optional extra (`pip install polish-pdf-loader[pymupdf]`)
- `langchain-core` is the only mandatory LangChain dependency (no `langchain_community`)
- Encoding repair must be lossless for already-correct UTF-8 text

## Review Focus

- **Mixed-encoding pages**: a PDF where most pages are UTF-8 but a scanned insert is CP1250 — per-page repair must not corrupt the UTF-8 pages.
- **Type3/custom-encoded fonts**: glyphs mapped via PDF `/Encoding` dicts that are neither CP1250 nor Latin-1 — the library must pass text through unchanged rather than silently corrupt it.
- **Already-correct Polish UTF-8**: running repair on clean UTF-8 must return the identical string — test with the full Pan Tadeusz opening.
- **Ligatures and fi/fl glyphs**: common in typeset PDFs; `ﬁ→fi`, `ﬂ→fl` should be normalised in post-processing.
- **Soft-hyphen / end-of-line hyphen**: `słowo-\n` should optionally be joined to `słowo` without corrupting genuine compound words.

---

### Task 1: Project scaffold and packaging

**Files:**
- Create: `pyproject.toml`
- Create: `polish_pdf_loader/__init__.py`
- Create: `polish_pdf_loader/py.typed`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

**Interfaces:**
- Produces: installable package; `from polish_pdf_loader import __version__` returns a string

- [ ] **Step 1: Write the failing test**

```python
# tests/test_package.py
import polish_pdf_loader

def test_version_is_string():
    assert isinstance(polish_pdf_loader.__version__, str)
    assert polish_pdf_loader.__version__ != ""
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_package.py -v
```
Expected: ImportError or AttributeError.

- [ ] **Step 3: Create `pyproject.toml`**

Use `[build-system] requires = ["hatchling"]`. Define extras:
```
[project.optional-dependencies]
pymupdf    = ["pymupdf>=1.23"]
pdfplumber = ["pdfplumber>=0.10"]
pypdf      = ["pypdf>=4.0"]
all        = ["pymupdf>=1.23", "pdfplumber>=0.10", "pypdf>=4.0", "chardet>=5.0"]
dev        = ["pytest>=8", "ruff>=0.4", "pymupdf>=1.23", "pdfplumber>=0.10", "pypdf>=4.0", "chardet>=5.0"]
```
Mandatory dep: `langchain-core>=0.2`.

- [ ] **Step 4: Create `polish_pdf_loader/__init__.py`** exporting `__version__ = "0.1.0"` and (after later tasks) the loader classes.

- [ ] **Step 5: Run test to verify it passes**

```bash
pip install -e ".[dev]" && pytest tests/test_package.py -v
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml polish_pdf_loader/ tests/
git commit -m "feat: project scaffold and packaging"
```

---

### Task 2: Encoding detection and repair

**Files:**
- Create: `polish_pdf_loader/encoding.py`
- Create: `tests/test_encoding.py`

**Interfaces:**
- Produces:
  - `detect_and_repair(text: str) -> str` — repairs CP1250-as-Latin1 when detected; passes UTF-8 through unchanged
  - `repair_cp1250_as_latin1(text: str) -> str` — unconditional repair
  - `is_polish_garbled(text: str) -> bool` — heuristic: returns True when text contains typical misread sequences

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_encoding.py
from polish_pdf_loader.encoding import repair_cp1250_as_latin1, detect_and_repair, is_polish_garbled

GARBLED  = "Litwo! ty jesteœ jak zdrowie. Ile ciê trzeba ceniæ, kto ciê straci³."
CORRECT  = "Litwo! ty jesteś jak zdrowie. Ile cię trzeba cenić, kto cię stracił."
CLEAN_UTF8 = "Już w samo południe słońce praży mocno."

def test_repair_cp1250_as_latin1():
    assert repair_cp1250_as_latin1(GARBLED) == CORRECT

def test_detect_and_repair_fixes_garbled():
    assert detect_and_repair(GARBLED) == CORRECT

def test_detect_and_repair_preserves_utf8():
    assert detect_and_repair(CLEAN_UTF8) == CLEAN_UTF8

def test_is_polish_garbled_true():
    assert is_polish_garbled(GARBLED) is True

def test_is_polish_garbled_false():
    assert is_polish_garbled(CLEAN_UTF8) is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_encoding.py -v
```
Expected: ImportError.

- [ ] **Step 3: Implement `polish_pdf_loader/encoding.py`**

`repair_cp1250_as_latin1`: encode the string to `'latin-1'` bytes (errors=`'replace'`), decode as `'cp1250'` (errors=`'replace'`).

`is_polish_garbled`: count occurrences of the five highest-frequency misread sequences (`œ`, `³`, `¹`, `ê` before vowel, `æ` after consonant); return True when density > 0.002 (2 per 1000 chars) and at least 2 distinct sequences appear.

`detect_and_repair`: call `is_polish_garbled`, repair only when True.

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_encoding.py -v
```
Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add polish_pdf_loader/encoding.py tests/test_encoding.py
git commit -m "feat: encoding detection and CP1250-as-Latin1 repair"
```

---

### Task 3: PyMuPDF backend

**Files:**
- Create: `polish_pdf_loader/backends/pymupdf_backend.py`
- Create: `tests/backends/test_pymupdf_backend.py`
- Create: `tests/data/README.md` (note about test fixtures)

**Interfaces:**
- Consumes: `detect_and_repair(text: str) -> str` from `polish_pdf_loader.encoding`
- Produces:
  - `load_pdf_pymupdf(path: str | Path, *, repair: bool = True, pages: list[int] | None = None) -> list[dict]`
    — returns list of `{"page": int, "text": str, "metadata": dict}` dicts

- [ ] **Step 1: Write the failing tests**

```python
# tests/backends/test_pymupdf_backend.py
import pytest
pytest.importorskip("pymupdf")
from pathlib import Path
from polish_pdf_loader.backends.pymupdf_backend import load_pdf_pymupdf

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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/backends/test_pymupdf_backend.py -v
```
Expected: ImportError or FileNotFoundError on the missing module.

- [ ] **Step 3: Implement `load_pdf_pymupdf`**

Open the document with `pymupdf.open(path)`. For each page (filtered by `pages` list when given), call `page.get_text("text")`, apply `detect_and_repair` when `repair=True`, build the result dict with `metadata` including `source`, `page`, `total_pages`, `author`, `title` from PDF metadata.

- [ ] **Step 4: Run tests** (skip-guarded tests pass or skip cleanly)

```bash
pytest tests/backends/test_pymupdf_backend.py -v
```

- [ ] **Step 5: Commit**

```bash
git add polish_pdf_loader/backends/ tests/backends/ tests/data/README.md
git commit -m "feat: PyMuPDF backend with Polish encoding repair"
```

---

### Task 4: pdfplumber backend

**Files:**
- Create: `polish_pdf_loader/backends/pdfplumber_backend.py`
- Create: `tests/backends/test_pdfplumber_backend.py`

**Interfaces:**
- Consumes: `detect_and_repair` from `polish_pdf_loader.encoding`
- Produces:
  - `load_pdf_pdfplumber(path: str | Path, *, repair: bool = True, pages: list[int] | None = None) -> list[dict]`
    — same dict shape as `load_pdf_pymupdf`

- [ ] **Step 1: Write the failing tests**

```python
# tests/backends/test_pdfplumber_backend.py
import pytest
pytest.importorskip("pdfplumber")
from pathlib import Path
from polish_pdf_loader.backends.pdfplumber_backend import load_pdf_pdfplumber

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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/backends/test_pdfplumber_backend.py -v
```

- [ ] **Step 3: Implement `load_pdf_pdfplumber`**

Use `pdfplumber.open(path)`. For each page, call `page.extract_text()` (returns `None` for image-only pages — replace with `""`), apply `detect_and_repair`, build same metadata dict shape as the PyMuPDF backend.

- [ ] **Step 4: Run tests**

```bash
pytest tests/backends/test_pdfplumber_backend.py -v
```

- [ ] **Step 5: Commit**

```bash
git add polish_pdf_loader/backends/pdfplumber_backend.py tests/backends/test_pdfplumber_backend.py
git commit -m "feat: pdfplumber backend with Polish encoding repair"
```

---

### Task 5: pypdf backend

**Files:**
- Create: `polish_pdf_loader/backends/pypdf_backend.py`
- Create: `tests/backends/test_pypdf_backend.py`

**Interfaces:**
- Consumes: `detect_and_repair` from `polish_pdf_loader.encoding`
- Produces:
  - `load_pdf_pypdf(path: str | Path, *, repair: bool = True, pages: list[int] | None = None) -> list[dict]`
    — same dict shape as other backends

- [ ] **Step 1: Write the failing tests** (same shape as Task 4 tests, s/pdfplumber/pypdf/)

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/backends/test_pypdf_backend.py -v
```

- [ ] **Step 3: Implement `load_pdf_pypdf`**

Use `pypdf.PdfReader(path)`. Iterate `reader.pages`, call `page.extract_text()`, apply `detect_and_repair`, build metadata from `reader.metadata`.

- [ ] **Step 4: Run tests**

```bash
pytest tests/backends/test_pypdf_backend.py -v
```

- [ ] **Step 5: Commit**

```bash
git add polish_pdf_loader/backends/pypdf_backend.py tests/backends/test_pypdf_backend.py
git commit -m "feat: pypdf backend with Polish encoding repair"
```

---

### Task 6: Text post-processing pipeline

**Files:**
- Create: `polish_pdf_loader/postprocess.py`
- Create: `tests/test_postprocess.py`

**Interfaces:**
- Produces:
  - `PostprocessConfig` dataclass: fields `fix_ligatures: bool = True`, `join_hyphens: bool = False`, `normalize_whitespace: bool = True`
  - `postprocess(text: str, config: PostprocessConfig | None = None) -> str`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_postprocess.py
from polish_pdf_loader.postprocess import postprocess, PostprocessConfig

def test_ligature_fi():
    assert postprocess("ﬁlm") == "film"

def test_ligature_fl():
    assert postprocess("ﬂaga") == "flaga"

def test_normalize_whitespace():
    assert postprocess("słowo  następne") == "słowo następne"

def test_join_hyphens_enabled():
    cfg = PostprocessConfig(join_hyphens=True)
    assert postprocess("słow-\nne zdanie", cfg) == "słowne zdanie"

def test_join_hyphens_disabled_by_default():
    result = postprocess("słow-\nne zdanie")
    assert "słow-\n" in result  # hyphen preserved

def test_no_mutation_of_clean_text():
    text = "Już w samo południe słońce praży mocno."
    assert postprocess(text) == text
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_postprocess.py -v
```

- [ ] **Step 3: Implement `postprocess`**

Apply transformations in order: ligature replacement (`str.replace` for `ﬁ→fi`, `ﬂ→fl`, `ﬀ→ff`, `ﬃ→ffi`, `ﬄ→ffl`); whitespace normalisation (`re.sub(r'[ \t]+', ' ', text)`); soft-hyphen removal (`text.replace('­', '')`); hyphen-join when enabled (`re.sub(r'-\n(\S)', r'\1', text)`).

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_postprocess.py -v
```

- [ ] **Step 5: Commit**

```bash
git add polish_pdf_loader/postprocess.py tests/test_postprocess.py
git commit -m "feat: text post-processing pipeline (ligatures, whitespace, hyphens)"
```

---

### Task 7: LangChain-compatible loaders

**Files:**
- Create: `polish_pdf_loader/loaders.py`
- Create: `tests/test_loaders.py`
- Modify: `polish_pdf_loader/__init__.py` — re-export `PolishPDFLoader`, `PolishPyMuPDFLoader`, `PolishPdfPlumberLoader`, `PolishPyPDFLoader`

**Interfaces:**
- Consumes: `load_pdf_pymupdf`, `load_pdf_pdfplumber`, `load_pdf_pypdf` from their backends; `postprocess`, `PostprocessConfig` from `polish_pdf_loader.postprocess`
- Produces:
  - `PolishPDFLoader(file_path: str | Path, backend: str = "pymupdf", repair: bool = True, pages: list[int] | None = None, postprocess_config: PostprocessConfig | None = None)` — `BaseLoader` subclass; `.load() -> list[Document]`; `.lazy_load() -> Iterator[Document]`
  - `PolishPyMuPDFLoader` — same init sig minus `backend`; delegates to `PolishPDFLoader(backend="pymupdf")`
  - `PolishPdfPlumberLoader` — same, `backend="pdfplumber"`
  - `PolishPyPDFLoader` — same, `backend="pypdf"`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_loaders.py
import pytest
pytest.importorskip("pymupdf")
from pathlib import Path
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_loaders.py -v
```

- [ ] **Step 3: Implement `PolishPDFLoader` in `loaders.py`**

Subclass `langchain_core.document_loaders.BaseLoader`. In `lazy_load`: dispatch to the matching `load_pdf_*` function based on `self.backend` (raise `ValueError` for unknown values), apply `postprocess` to each page's text, yield `Document(page_content=text, metadata=metadata)`.

Alias classes: `PolishPyMuPDFLoader = functools.partial`-style thin subclass that hard-codes `backend=`.

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_loaders.py -v
```

- [ ] **Step 5: Update `__init__.py`** exports and commit

```bash
git add polish_pdf_loader/loaders.py polish_pdf_loader/__init__.py tests/test_loaders.py
git commit -m "feat: LangChain-compatible PolishPDFLoader and backend aliases"
```

---

### Task 8: CLI tool

**Files:**
- Create: `polish_pdf_loader/cli.py`
- Modify: `pyproject.toml` — add `[project.scripts] polish-pdf = "polish_pdf_loader.cli:main"`
- Create: `tests/test_cli.py`

**Interfaces:**
- Consumes: `PolishPDFLoader` from `polish_pdf_loader.loaders`
- Produces: `main()` entry point; CLI: `polish-pdf <file> [--backend pymupdf|pdfplumber|pypdf] [--pages 0,1,2] [--out FILE] [--no-repair] [--join-hyphens]`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_cli.py
from click.testing import CliRunner
from polish_pdf_loader.cli import main

def test_help_exits_zero():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "backend" in result.output

def test_missing_file_exits_nonzero():
    runner = CliRunner()
    result = runner.invoke(main, ["nonexistent.pdf"])
    assert result.exit_code != 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_cli.py -v
```

- [ ] **Step 3: Implement `cli.py`** using `click`. Add `click` to `pyproject.toml` mandatory deps.

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_cli.py -v
```

- [ ] **Step 5: Commit**

```bash
git add polish_pdf_loader/cli.py tests/test_cli.py pyproject.toml
git commit -m "feat: CLI tool polish-pdf"
```

---

### Task 9: Integration test with real fixture

**Files:**
- Create: `tests/data/generate_fixture.py` — script that generates `sample_polish.pdf` using `reportlab` or `fpdf2` with known Polish text
- Modify: `tests/conftest.py` — auto-generate the fixture if absent
- Create: `tests/test_integration.py`

**Interfaces:**
- Consumes: all three backends and `PolishPDFLoader`
- Produces: green integration suite that runs without an external PDF

- [ ] **Step 1: Write the failing integration tests**

```python
# tests/test_integration.py
import pytest
from pathlib import Path
from polish_pdf_loader import PolishPDFLoader

FIXTURE = Path(__file__).parent / "data" / "sample_polish.pdf"
PAN_TADEUSZ_SNIP = "Litwo! Ojczyzno moja!"

@pytest.mark.integration
def test_all_backends_agree_on_polish(tmp_path):
    """All backends return correctly decoded Polish chars from the same fixture."""
    for backend in ("pymupdf", "pdfplumber", "pypdf"):
        pytest.importorskip(backend if backend != "pymupdf" else "pymupdf")
        docs = PolishPDFLoader(FIXTURE, backend=backend).load()
        full = " ".join(d.page_content for d in docs)
        assert any(ch in full for ch in "ąćęłńóśźż"), f"{backend} garbled text"

@pytest.mark.integration
def test_repair_matches_known_text():
    docs = PolishPDFLoader(FIXTURE, backend="pymupdf").load()
    full = " ".join(d.page_content for d in docs)
    assert PAN_TADEUSZ_SNIP in full
```

- [ ] **Step 2: Implement `generate_fixture.py`**

Use `fpdf2` (add as dev dep) to write a one-page PDF containing the Pan Tadeusz opening in UTF-8 with a TTF font that embeds Polish glyphs, and a second page whose text bytes are CP1250 (simulated via `fpdf2`'s raw encoding). The conftest calls this if `sample_polish.pdf` is missing.

- [ ] **Step 3: Run integration tests**

```bash
pytest tests/test_integration.py -v -m integration
```
Expected: PASS for available backends.

- [ ] **Step 4: Run full suite**

```bash
pytest -v
```
Expected: all tests PASS or skip cleanly.

- [ ] **Step 5: Commit**

```bash
git add tests/data/ tests/conftest.py tests/test_integration.py
git commit -m "test: integration suite with generated Polish PDF fixture"
```
