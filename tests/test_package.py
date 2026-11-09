import polish_pdf_loader


def test_version_is_string():
    assert isinstance(polish_pdf_loader.__version__, str)
    assert polish_pdf_loader.__version__ != ""
