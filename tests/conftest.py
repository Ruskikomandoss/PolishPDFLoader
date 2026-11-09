from pathlib import Path
import pytest

FIXTURE_PDF = Path(__file__).parent / "data" / "sample_polish.pdf"


def pytest_configure(config):
    """Auto-generate the test fixture PDF if it doesn't exist."""
    if not FIXTURE_PDF.exists():
        try:
            from tests.data.generate_fixture import generate
            generate()
        except Exception:
            pass  # fixture-dependent tests will skip cleanly
