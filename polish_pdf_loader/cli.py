from __future__ import annotations

import sys
from pathlib import Path

import click

from polish_pdf_loader.loaders import PolishPDFLoader
from polish_pdf_loader.postprocess import PostprocessConfig


@click.command()
@click.argument("file", type=click.Path(exists=False))
@click.option(
    "--backend",
    default="pymupdf",
    show_default=True,
    type=click.Choice(["pymupdf", "pdfplumber", "pypdf"], case_sensitive=False),
    help="PDF extraction backend to use.",
)
@click.option(
    "--pages",
    default=None,
    help="Comma-separated page indices to extract (0-based), e.g. 0,1,2.",
)
@click.option(
    "--out",
    default=None,
    type=click.Path(),
    help="Output file path. Defaults to stdout.",
)
@click.option("--no-repair", is_flag=True, default=False, help="Disable encoding repair.")
@click.option("--join-hyphens", is_flag=True, default=False, help="Join end-of-line hyphens.")
def main(
    file: str,
    backend: str,
    pages: str | None,
    out: str | None,
    no_repair: bool,
    join_hyphens: bool,
) -> None:
    """Extract text from a Polish PDF file.

    FILE is the path to the PDF to process.
    """
    path = Path(file)
    if not path.exists():
        click.echo(f"Error: file not found: {file}", err=True)
        sys.exit(1)

    page_list: list[int] | None = None
    if pages:
        try:
            page_list = [int(p.strip()) for p in pages.split(",")]
        except ValueError:
            click.echo("Error: --pages must be comma-separated integers.", err=True)
            sys.exit(1)

    cfg = PostprocessConfig(join_hyphens=join_hyphens)
    loader = PolishPDFLoader(
        path,
        backend=backend,
        repair=not no_repair,
        pages=page_list,
        postprocess_config=cfg,
    )

    text_parts = [doc.page_content for doc in loader.load()]
    output = "\n\n".join(text_parts)

    if out:
        Path(out).write_text(output, encoding="utf-8")
        click.echo(f"Written to {out}")
    else:
        click.echo(output)
