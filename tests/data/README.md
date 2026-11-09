# Test fixtures

`sample_polish.pdf` is generated automatically by `tests/data/generate_fixture.py`
when the integration tests run (see `tests/conftest.py`).

The fixture contains two pages:
1. Pan Tadeusz opening — clean UTF-8 Polish text
2. Same text simulated as CP1250-encoded (for repair testing)
