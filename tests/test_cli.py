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
