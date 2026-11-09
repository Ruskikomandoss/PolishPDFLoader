# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PolishPDFLoader is a Python library for loading and processing Polish-language PDF documents. The repository is in early development; source code has not yet been added.

## Expected Stack (inferred from .gitignore)

- **Language**: Python
- **Testing**: pytest
- **Docs**: Sphinx
- **UI (optional)**: Streamlit or Marimo

## Setup

Once a `pyproject.toml` or `requirements.txt` is added, set up the environment with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Development Commands

Add commands here as the project grows (build, lint, test, etc.). For example:

```bash
pytest                  # run all tests
pytest tests/test_x.py  # run a single test file
```
