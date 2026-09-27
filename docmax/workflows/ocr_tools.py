"""
docmax-demo OCR Workflows — all OCR tool workflows in one file.
"""

from pathlib import Path

import questionary
from rich.console import Console

from docmax-demo.loading import Loader
from docmax-demo.dependencies import has_poppler, check_poppler, check_tesseract
from docmax-demo.workflows.common import (
    select_single_pdf,
    select_folder,
    get_output_name,
    success_screen,
    failure_screen,
)

console = Console()


# ---------------------------------------------------------------------------
# OCR Image / PDF
# ---------------------------------------------------------------------------

def ocr_workflow():
    if not check_tesseract():
        return

    input_file = questionary.path("Image or PDF file:").ask()
    if not input_file:
        return

    input_file = Path(input_file)

    if input_file.suffix.lower() == ".pdf":
        if not check_poppler():
            return

    console.print("\n[bold cyan]OCR Image / PDF[/bold cyan]\n")

    lang = questionary.text("OCR Language(s)", default="eng").ask()
    fmt = questionary.select("Output Format", choices=["txt", "json", "md"]).ask()

    output = get_output_name(f"{input_file.stem}_ocr.{fmt}")
    if not output:
        return

    output_path = Path(output)

    try:
        with Loader("Running OCR..."):
            if input_file.suffix.lower() == ".pdf":
                from docmax-demo.engine import ocr_pdf
                ocr_pdf(input_file, output_path, lang, fmt)
            else:
                from docmax-demo.engine import ocr_image
                ocr_image(input_file, output_path, lang, fmt)

        success_screen(
            "OCR Complete",
            output_file=output_path.name,
            extra_lines=[
                f"Format : {fmt}",
                f"Lang   : {lang}",
            ],
        )
    except Exception as e:
        failure_screen("OCR Failed", str(e))


# ---------------------------------------------------------------------------
# Searchable PDF
# ---------------------------------------------------------------------------

def searchable_workflow():
    console.print("\n[bold cyan]Searchable PDF[/bold cyan]\n")

    pdf = select_single_pdf()
    if not pdf:
        return

    lang = questionary.text("OCR Language(s)", default="eng").ask()

    output = get_output_name(f"{pdf.stem}_searchable.pdf")
    if not output:
        return

    output_path = Path(output)

    try:
        with Loader("Creating searchable PDF..."):
            from docmax-demo.engine import make_searchable_pdf
            make_searchable_pdf(pdf, output_path, lang, 300)

        success_screen("Searchable PDF Created", output_file=output_path.name)
    except Exception as e:
        failure_screen("Searchable PDF Failed", str(e))


# ---------------------------------------------------------------------------
# Batch OCR
# ---------------------------------------------------------------------------

def batch_ocr_workflow():
    console.print("\n[bold cyan]Batch OCR[/bold cyan]\n")

    folder = select_folder()
    if not folder:
        return

    lang = questionary.text("OCR Language(s)", default="eng").ask()
    fmt = questionary.select("Output Format", choices=["txt", "json", "md"]).ask()
    workers = int(questionary.text("Workers", default="4").ask())

    try:
        with Loader("Processing batch OCR..."):
            from docmax-demo.batch import batch_with_ocr
            batch_with_ocr(Path(folder), lang, fmt, True, workers)

        success_screen(
            "Batch OCR Complete",
            extra_lines=[
                f"Folder  : {folder}",
                f"Workers : {workers}",
            ],
        )
    except Exception as e:
        failure_screen("Batch OCR Failed", str(e))


# ---------------------------------------------------------------------------
# Extract Tables
# ---------------------------------------------------------------------------

def tables_workflow():
    console.print("\n[bold cyan]Extract Tables[/bold cyan]\n")

    pdf = select_single_pdf()
    if not pdf:
        return

    fmt = questionary.select(
        "Output format",
        choices=["xlsx", "csv", "json"],
    ).ask()

    output = Path(f"{pdf.stem}_tables.{fmt}")

    try:
        from docmax-demo.extractor import extract_tables
        extract_tables(pdf, output)
        success_screen("Table Extraction Complete", output_file=output.name)
    except Exception as e:
        failure_screen("Table Extraction Failed", str(e))


# ---------------------------------------------------------------------------
# OCR Settings  (delegates to settings workflow)
# ---------------------------------------------------------------------------

def ocr_settings_workflow():
    from docmax-demo.workflows.settings import settings_workflow
    settings_workflow()
