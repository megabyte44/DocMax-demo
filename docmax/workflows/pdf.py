"""
docmax-demo PDF Workflows — all PDF tool workflows in one file.
Each function is self-contained and calls operations from docmax-demo.operations.
"""

from pathlib import Path

import questionary
from rich.console import Console

from docmax-demo.operations import (
    merge,
    split,
    compress,
    rotate,
    extract_pages,
    watermark,
    encrypt,
    decrypt,
)
from docmax-demo.workflows.common import (
    select_multiple_pdfs,
    select_single_pdf,
    show_file_info,
    get_output_name,
    success_screen,
    failure_screen,
)

console = Console()


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def merge_workflow():
    console.print("\n[bold cyan]Merge PDFs[/bold cyan]\n")

    folder, selected = select_multiple_pdfs()
    if not folder or not selected:
        return

    for pdf in selected:
        show_file_info(folder / pdf)

    if len(selected) < 2:
        console.print("[red]Select at least 2 PDFs.[/red]")
        return

    console.print("\n[bold cyan]Selected PDFs[/bold cyan]\n")
    for i, pdf in enumerate(selected, start=1):
        console.print(f"{i}. {pdf}")
    console.print(f"\n[green]Total PDFs:[/green] {len(selected)}\n")

    if not questionary.confirm("Continue?", default=True).ask():
        return

    sort_mode = questionary.select(
        "Sort PDFs before merging?",
        choices=["Keep Current Order", "Alphabetical", "Reverse Alphabetical"],
    ).ask()

    if sort_mode == "Alphabetical":
        selected.sort()
    elif sort_mode == "Reverse Alphabetical":
        selected.sort(reverse=True)

    output = get_output_name(f"merged_{len(selected)}_files.pdf")
    if not output:
        return

    output_path = Path(output)

    if output_path.exists():
        if not questionary.confirm(
            f"{output} already exists. Overwrite?", default=False
        ).ask():
            return

    console.print("\n[bold cyan]Merging PDFs...[/bold cyan]\n")
    inputs = [folder / pdf for pdf in selected]

    try:
        merge(inputs, output_path)
        success_screen(
            "Merge Complete",
            output_file=output_path.name,
            extra_lines=[
                f"Input Files : {len(selected)}",
                f"Location    : {output_path.resolve()}",
            ],
        )
    except Exception as e:
        failure_screen("Merge Failed", str(e))
        return

    next_action = questionary.select(
        "What next?",
        choices=["Merge More PDFs", "Back to PDF Tools"],
    ).ask()

    if next_action == "Merge More PDFs":
        merge_workflow()


# ---------------------------------------------------------------------------
# Split
# ---------------------------------------------------------------------------

def split_workflow():
    console.print("\n[bold cyan]Split PDF[/bold cyan]\n")

    pdf = select_single_pdf()
    if not pdf:
        return

    console.print("\n[bold cyan]Splitting PDF...[/bold cyan]\n")

    try:
        split(pdf)
        success_screen(
            "Split Complete",
            extra_lines=[f"Source : {pdf.name}"],
        )
    except Exception as e:
        failure_screen("Split Failed", str(e))


# ---------------------------------------------------------------------------
# Compress
# ---------------------------------------------------------------------------

def compress_workflow():
    console.print("\n[bold cyan]Compress PDF[/bold cyan]\n")

    input_file = select_single_pdf()
    if not input_file:
        return

    show_file_info(input_file)

    preset = questionary.select(
        "Compression Quality",
        choices=[
            "ebook    - 📚 Recommended (~150 DPI)",
            "screen   - 📱 Smallest file (~72 DPI)",
            "printer  - 🖨 High quality (~300 DPI)",
            "prepress - 🏢 Professional print (~300+ DPI)",
            "default  - ⚖ Balanced",
        ],
    ).ask().split()[0]

    output = get_output_name(f"{input_file.stem}_compressed.pdf")
    if not output:
        return

    output_path = Path(output)
    console.print("\n[bold cyan]Compressing PDF...[/bold cyan]\n")

    try:
        compress(input_file, output_path, preset)
        success_screen(
            "Compression Complete",
            output_file=output_path.name,
            extra_lines=[
                f"Preset     : {preset}",
                f"Location   : {output_path.resolve()}",
            ],
        )
    except Exception as e:
        failure_screen("Compression Failed", str(e))
        return

    next_action = questionary.select(
        "What next?",
        choices=["Compress Another PDF", "Back to PDF Tools"],
    ).ask()

    if next_action == "Compress Another PDF":
        compress_workflow()


# ---------------------------------------------------------------------------
# Rotate
# ---------------------------------------------------------------------------

def rotate_workflow():
    console.print("\n[bold cyan]Rotate PDF[/bold cyan]\n")

    pdf = select_single_pdf()
    if not pdf:
        return

    degrees = int(
        questionary.select("Rotation", choices=["90", "180", "270"]).ask()
    )

    output = get_output_name(f"{pdf.stem}_rotated.pdf")
    if not output:
        return

    output_path = Path(output)

    try:
        rotate(pdf, degrees, output_path)
        success_screen(
            "Rotation Complete",
            output_file=output_path.name,
            extra_lines=[f"Rotation : {degrees}°"],
        )
    except Exception as e:
        failure_screen("Rotation Failed", str(e))


# ---------------------------------------------------------------------------
# Extract Pages
# ---------------------------------------------------------------------------

def pages_workflow():
    console.print("\n[bold cyan]Extract Pages[/bold cyan]\n")

    pdf = select_single_pdf()
    if not pdf:
        return

    page_range = questionary.text(
        "Page range (Examples: 1-5, 3, 1,3,5)"
    ).ask()
    if not page_range:
        return

    output = get_output_name(f"{pdf.stem}_pages.pdf")
    if not output:
        return

    output_path = Path(output)
    console.print("\n[bold cyan]Extracting Pages...[/bold cyan]\n")

    try:
        extract_pages(pdf, page_range, output_path)
        success_screen(
            "Page Extraction Complete",
            output_file=output_path.name,
            extra_lines=[f"Pages : {page_range}"],
        )
    except Exception as e:
        failure_screen("Page Extraction Failed", str(e))


# ---------------------------------------------------------------------------
# Watermark
# ---------------------------------------------------------------------------

def watermark_workflow():
    console.print("\n[bold cyan]Watermark PDF[/bold cyan]\n")

    pdf = select_single_pdf()
    if not pdf:
        return

    watermark_file = questionary.path("Watermark file (PDF/Image):").ask()
    if not watermark_file:
        return

    output = get_output_name(f"{pdf.stem}_watermarked.pdf")
    if not output:
        return

    output_path = Path(output)
    console.print("\n[bold cyan]Applying Watermark...[/bold cyan]\n")

    try:
        watermark(pdf, Path(watermark_file), output_path)
        success_screen("Watermark Complete", output_file=output_path.name)
    except Exception as e:
        failure_screen("Watermark Failed", str(e))


# ---------------------------------------------------------------------------
# Encrypt
# ---------------------------------------------------------------------------

def encrypt_workflow():
    console.print("\n[bold cyan]Encrypt PDF[/bold cyan]\n")

    pdf = select_single_pdf()
    if not pdf:
        return

    password = questionary.password("Password:").ask()
    if not password:
        return

    output = get_output_name(f"{pdf.stem}_encrypted.pdf")
    if not output:
        return

    output_path = Path(output)

    try:
        encrypt(pdf, password, output_path)
        success_screen("Encryption Complete", output_file=output_path.name)
    except Exception as e:
        failure_screen("Encryption Failed", str(e))


# ---------------------------------------------------------------------------
# Decrypt
# ---------------------------------------------------------------------------

def decrypt_workflow():
    console.print("\n[bold cyan]Decrypt PDF[/bold cyan]\n")

    pdf = select_single_pdf()
    if not pdf:
        return

    password = questionary.password("Password:").ask()
    if not password:
        return

    output = get_output_name(f"{pdf.stem}_decrypted.pdf")
    if not output:
        return

    output_path = Path(output)

    try:
        decrypt(pdf, password, output_path)
        success_screen("Decryption Complete", output_file=output_path.name)
    except Exception as e:
        failure_screen("Decryption Failed", str(e))
