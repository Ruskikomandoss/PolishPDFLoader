# polish-pdf-loader

A Python library for extracting text from Polish-language PDFs — correctly.

Most PDF extraction tools (`PyMuPDFLoader`, `PDFPlumberLoader`, etc.) silently garble Polish characters when the PDF uses CP1250 encoding, producing output like:

```
Litwo! Ojczyzno moja! ty jesteœ jak zdrowie.
Ile ciê trzeba ceniæ, ten tylko siê dowie,
Kto ciê straci³. Dziœ piêknoœæ tw¹ w ca³ej ozdobie
```

`polish-pdf-loader` detects and fixes this automatically:

```
Litwo! Ojczyzno moja! ty jesteś jak zdrowie.
Ile cię trzeba cenić, ten tylko się dowie,
Kto cię stracił. Dziś piękność twą w całej ozdobie
```

It wraps **PyMuPDF**, **pdfplumber**, and **pypdf** as optional backends and exposes drop-in [LangChain](https://python.langchain.com/)-compatible document loaders.

---

## Installation

```bash
pip install polish-pdf-loader            # core only (pick a backend below)
pip install "polish-pdf-loader[pymupdf]"      # + PyMuPDF (recommended)
pip install "polish-pdf-loader[pdfplumber]"   # + pdfplumber
pip install "polish-pdf-loader[pypdf]"        # + pypdf
pip install "polish-pdf-loader[all]"          # all three backends
```

---

## Quick start

### Drop-in LangChain loader

```python
from polish_pdf_loader import PolishPyMuPDFLoader

loader = PolishPyMuPDFLoader("pan_tadeusz.pdf")
docs = loader.load()

print(docs[0].page_content[:120])
# Litwo! Ojczyzno moja! ty jesteś jak zdrowie.
# Ile cię trzeba cenić, ten tylko się dowie,
```

### Generic loader with backend choice

```python
from polish_pdf_loader import PolishPDFLoader

# switch backend without changing anything else
docs = PolishPDFLoader("document.pdf", backend="pdfplumber").load()
docs = PolishPDFLoader("document.pdf", backend="pypdf").load()
```

### Load specific pages

```python
docs = PolishPDFLoader("book.pdf", pages=[0, 1, 2]).load()
```

### Post-processing options

```python
from polish_pdf_loader import PolishPDFLoader
from polish_pdf_loader.postprocess import PostprocessConfig

cfg = PostprocessConfig(
    fix_ligatures=True,       # ﬁ→fi, ﬂ→fl  (default: True)
    normalize_whitespace=True, # collapse double spaces (default: True)
    join_hyphens=True,        # join "słow-\nne" → "słowne" (default: False)
)
docs = PolishPDFLoader("book.pdf", postprocess_config=cfg).load()
```

### Disable encoding repair

```python
# If your PDF is already UTF-8 and you want raw extraction:
docs = PolishPDFLoader("document.pdf", repair=False).load()
```

### Low-level encoding utilities

```python
from polish_pdf_loader.encoding import (
    detect_and_repair,       # auto-detects and fixes garbled text
    repair_cp1250_as_latin1, # always applies CP1252→CP1250 repair
    is_polish_garbled,       # heuristic: True when garbled pattern found
)

text = "Litwo! ty jesteœ jak zdrowie. Ile ciê trzeba ceniæ, kto ciê straci³."
print(detect_and_repair(text))
# Litwo! ty jesteś jak zdrowie. Ile cię trzeba cenić, kto cię stracił.
```

---

## CLI

```bash
polish-pdf document.pdf
polish-pdf document.pdf --backend pdfplumber
polish-pdf document.pdf --pages 0,1,2 --out output.txt
polish-pdf document.pdf --join-hyphens
polish-pdf document.pdf --no-repair          # skip encoding fix
```

---

## Available loaders

| Class | Backend | Drop-in for |
|---|---|---|
| `PolishPDFLoader` | configurable | — |
| `PolishPyMuPDFLoader` | PyMuPDF | `PyMuPDFLoader` |
| `PolishPdfPlumberLoader` | pdfplumber | `PDFPlumberLoader` |
| `PolishPyPDFLoader` | pypdf | `PyPDFLoader` |

All are `langchain_core.document_loaders.BaseLoader` subclasses and return `langchain_core.documents.Document` objects.

---

## How it works

PDF tools extract text as bytes and interpret them using a codec. When a Polish PDF was created with a CP1250-encoded font and the tool assumes CP1252 (Windows Western European), every Polish diacritic maps to the wrong character:

| CP1250 byte | CP1250 char | Misread as CP1252 |
|:-----------:|:-----------:|:-----------------:|
| `0x9C` | ś | œ |
| `0xB3` | ł | ³ |
| `0xB9` | ą | ¹ |
| `0xE6` | ć | æ |
| `0xEA` | ę | ê |

The fix is deterministic: re-encode the garbled string back to CP1252 bytes, then decode as CP1250.

```python
repaired = garbled.encode("cp1252", errors="replace").decode("cp1250", errors="replace")
```

`detect_and_repair` only applies this when it detects the garbled pattern (presence of anchor markers `œ`, `Ÿ`, or `Œ` without any clean Polish diacritics), so already-correct UTF-8 text is passed through unchanged.

---

## Requirements

- Python 3.9+
- `langchain-core >= 0.2`
- At least one backend: `pymupdf >= 1.23`, `pdfplumber >= 0.10`, or `pypdf >= 4.0`

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
