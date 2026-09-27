"""
docmax-demo CLI - Forge your documents from your terminal.
All interactive menus use dict-driven dispatch via the menu module's *_MENU dicts.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from docmax-demo import __version__
from docmax-demo.theme import docmax-demo_THEME
from docmax-demo.config import DEFAULT_OCR_LANG, DEFAULT_COMPRESS_PRESET, DEFAULT_BATCH_WORKERS
from docmax-demo.banner import show_banner
from docmax-demo.setup import setup_dependencies
from docmax-demo.dependencies import doctor as run_doctor
from docmax-demo.help import show_install_help
from docmax-demo.watcher import watch

# ── Menu functions + dicts ───────────────────────────────────────────────────
from docmax-demo.menu import (
    main_menu,
    pdf_menu,   PDF_MENU,
    ocr_menu,   OCR_MENU,
    conversion_menu, CONVERSION_MENU,
    extract_menu,    EXTRACT_MENU,
    batch_menu,      BATCH_MENU,
    image_menu,      IMAGE_MENU,
    automation_menu, AUTOMATION_MENU,
    settings_menu,   SETTINGS_MENU,
)

# ── PDF workflows (all in one file) ─────────────────────────────────────────
from docmax-demo.workflows.pdf import (
    merge_workflow,
    split_workflow,
    compress_workflow,
    rotate_workflow,
    pages_workflow,
    watermark_workflow,
    encrypt_workflow,
    decrypt_workflow,
)

# ── OCR workflows (all in one file) ─────────────────────────────────────────
from docmax-demo.workflows.ocr_tools import (
    ocr_workflow,
    searchable_workflow,
    batch_ocr_workflow,
    tables_workflow,
    ocr_settings_workflow,
)

# ── Other workflows ──────────────────────────────────────────────────────────
from docmax-demo.workflows.convert import (
    markdown_to_pdf_workflow,
    markdown_to_docx_workflow,
    docx_to_pdf_workflow,
    docx_to_markdown_workflow,
    images_to_pdf_workflow,
    pdf_to_images_workflow,
)
from docmax-demo.workflows.extract import extract_text_workflow, extract_images_workflow, extract_metadata_workflow
from docmax-demo.workflows.batch import batch_convert_workflow, batch_compress_workflow, batch_ocr_folder_workflow
from docmax-demo.workflows.automation import auto_ocr_workflow, auto_searchable_workflow, auto_compress_workflow, auto_preprocess_workflow
from docmax-demo.workflows.image import (
    resize_workflow,
    convert_format_workflow,
    compress_image_workflow,
    rotate_image_workflow,
    crop_workflow,
    flip_h_workflow,
    flip_v_workflow,
    watermark_image_workflow,
    remove_bg_workflow,
)
from docmax-demo.workflows.settings import (
    settings_ocr_workflow,
    doctor_workflow,
    setup_workflow,
    show_paths_workflow,
)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = typer.Typer(
    name="docmax-demo",
    help="docmax-demo - Unified Document Processing CLI. Forge your documents from your terminal.",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=False,
)

console = Console(theme=docmax-demo_THEME)


def _version_callback(value: bool):
    if value:
        console.print(
            Panel(
                Text(f"docmax-demo v{__version__}", justify="center", style="bold green"),
                subtitle="[dim]Forge your documents from your terminal[/dim]",
                border_style="green",
            )
        )
        raise typer.Exit()


# ---------------------------------------------------------------------------
# Action maps  (action_key → callable)
# These mirror the values in the *_MENU dicts.
# ---------------------------------------------------------------------------

PDF_ACTIONS = {
    "merge":    merge_workflow,
    "split":    split_workflow,
    "compress": compress_workflow,
    "rotate":   rotate_workflow,
    "pages":    pages_workflow,
    "watermark": watermark_workflow,
    "encrypt":  encrypt_workflow,
    "decrypt":  decrypt_workflow,
}

OCR_ACTIONS = {
    "ocr":        ocr_workflow,
    "searchable": searchable_workflow,
    "batch_ocr":  batch_ocr_workflow,
    "tables":     tables_workflow,
    "settings":   ocr_settings_workflow,
}

CONVERSION_ACTIONS = {
    "md2pdf":   markdown_to_pdf_workflow,
    "md2docx":  markdown_to_docx_workflow,
    "docx2pdf": docx_to_pdf_workflow,
    "docx2md":  docx_to_markdown_workflow,
    "img2pdf":  images_to_pdf_workflow,
    "pdf2img":  pdf_to_images_workflow,
}

EXTRACT_ACTIONS = {
    "text":     extract_text_workflow,
    "images":   extract_images_workflow,
    "metadata": extract_metadata_workflow,
}

BATCH_ACTIONS = {
    "convert":  batch_convert_workflow,
    "compress": batch_compress_workflow,
    "ocr":      batch_ocr_folder_workflow,
}

IMAGE_ACTIONS = {
    "resize":    resize_workflow,
    "convert":   convert_format_workflow,
    "compress":  compress_image_workflow,
    "rotate":    rotate_image_workflow,
    "crop":      crop_workflow,
    "flip_h":    flip_h_workflow,
    "flip_v":    flip_v_workflow,
    "watermark": watermark_image_workflow,
    "remove_bg": remove_bg_workflow,
}

AUTOMATION_ACTIONS = {
    "ocr":        auto_ocr_workflow,
    "searchable": auto_searchable_workflow,
    "compress":   auto_compress_workflow,
    "preprocess": auto_preprocess_workflow,
}

SETTINGS_ACTIONS = {
    "ocr_settings": settings_ocr_workflow,
    "doctor":        doctor_workflow,
    "setup":         setup_workflow,
    "paths":         show_paths_workflow,
}


# ---------------------------------------------------------------------------
# Generic submenu runner
# ---------------------------------------------------------------------------

def _run_submenu(menu_fn, menu_dict: dict, action_map: dict):
    """
    Loop a submenu until Back is chosen.

    menu_fn()    → returns the display string the user picked
    menu_dict    → maps display string → action key (None = Back)
    action_map   → maps action key → callable
    """
    while True:
        choice = menu_fn()
        action_key = menu_dict.get(choice)
        if action_key is None:          # "⬅ Back" or unknown
            break
        action = action_map.get(action_key)
        if action:
            action()
        else:
            console.print(f"[yellow]{choice} not implemented yet[/yellow]")


# ---------------------------------------------------------------------------
# Main interactive entry point
# ---------------------------------------------------------------------------

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show docmax-demo version.",
    ),
):
    if ctx.invoked_subcommand:
        return

    show_banner()

    try:
        while True:
            choice = main_menu()

            if choice is None or choice == "❌ Exit":
                raise typer.Exit()

            elif choice == "📄 PDF Tools":
                _run_submenu(pdf_menu, PDF_MENU, PDF_ACTIONS)

            elif choice == "🔍 OCR":
                _run_submenu(ocr_menu, OCR_MENU, OCR_ACTIONS)

            elif choice == "🔄 Conversion":
                _run_submenu(conversion_menu, CONVERSION_MENU, CONVERSION_ACTIONS)

            elif choice == "📂 Extract":
                _run_submenu(extract_menu, EXTRACT_MENU, EXTRACT_ACTIONS)

            elif choice == "⚡ Batch Processing":
                _run_submenu(batch_menu, BATCH_MENU, BATCH_ACTIONS)

            elif choice == "🖼 Image Processing":
                _run_submenu(image_menu, IMAGE_MENU, IMAGE_ACTIONS)

            elif choice == "👀 Watch Folder":
                _run_submenu(automation_menu, AUTOMATION_MENU, AUTOMATION_ACTIONS)

            elif choice == "⚙ Settings":
                _run_submenu(settings_menu, SETTINGS_MENU, SETTINGS_ACTIONS)

            elif choice == "📦 Install Guide":
                show_install_help()

    except KeyboardInterrupt:
        console.print("\n[red]Exiting...[/red]")


# ===========================================================================
# Helper Commands
# ===========================================================================

@app.command("doctor")
def cmd_doctor():
    """Check external dependencies."""
    run_doctor()


@app.command("setup")
def cmd_setup():
    """Install external dependencies."""
    setup_dependencies()


# ===========================================================================
# PDF Commands
# ===========================================================================

@app.command("merge")
def cmd_merge(
    inputs: List[Path] = typer.Argument(..., help="PDF files to merge (at least 2)."),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Output file path."),
):
    """[bold]Merge[/bold] multiple PDF files into one."""
    if len(inputs) < 2:
        typer.echo("Error: Provide at least 2 PDF files to merge.", err=True)
        raise typer.Exit(1)
    from docmax-demo.operations import merge
    out_path = Path(output) if output else Path(inputs[0]).with_name("merged.pdf")
    merge(inputs, out_path)


@app.command("split")
def cmd_split(
    input_file: Path = typer.Argument(..., help="PDF file to split."),
    output_dir: Optional[Path] = typer.Option(None, "-o", "--output-dir"),
):
    """[bold]Split[/bold] a PDF into individual page files."""
    from docmax-demo.operations import split
    split(input_file, output_dir)


@app.command("compress")
def cmd_compress(
    input_file: Path = typer.Argument(..., help="PDF file to compress."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
    preset: str = typer.Option(DEFAULT_COMPRESS_PRESET, "--preset"),
):
    """[bold]Compress[/bold] a PDF using Ghostscript."""
    from docmax-demo.operations import compress
    compress(input_file, output, preset)


@app.command("rotate")
def cmd_rotate(
    input_file: Path = typer.Argument(..., help="PDF file to rotate."),
    degrees: int = typer.Argument(..., help="Degrees: 90, 180, or 270."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
):
    """[bold]Rotate[/bold] all pages of a PDF."""
    from docmax-demo.operations import rotate
    rotate(input_file, degrees, output)


@app.command("pages")
def cmd_pages(
    input_file: Path = typer.Argument(..., help="PDF file."),
    page_range: str = typer.Argument(..., help='Page range e.g. "1-5", "3", "1,3,5".'),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
):
    """[bold]Extract[/bold] a range of pages from a PDF."""
    from docmax-demo.operations import extract_pages
    extract_pages(input_file, page_range, output)


@app.command("watermark")
def cmd_watermark(
    input_file: Path = typer.Argument(..., help="PDF file to watermark."),
    watermark_file: Path = typer.Argument(..., help="Watermark file (PDF or image)."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
):
    """[bold]Watermark[/bold] a PDF with an image or PDF overlay."""
    from docmax-demo.operations import watermark
    watermark(input_file, watermark_file, output)


@app.command("encrypt")
def cmd_encrypt(
    input_file: Path = typer.Argument(..., help="PDF file to encrypt."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
    password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True),
):
    """[bold]Encrypt[/bold] a PDF with a password."""
    from docmax-demo.operations import encrypt
    encrypt(input_file, password, output)


@app.command("decrypt")
def cmd_decrypt(
    input_file: Path = typer.Argument(..., help="Encrypted PDF file."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
    password: str = typer.Option(..., prompt=True, hide_input=True),
):
    """[bold]Decrypt[/bold] a password-protected PDF."""
    from docmax-demo.operations import decrypt
    decrypt(input_file, password, output)


# ===========================================================================
# OCR Commands
# ===========================================================================

@app.command("ocr")
def cmd_ocr(
    input_file: Path = typer.Argument(..., help="Image or PDF file."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
    lang: str = typer.Option(DEFAULT_OCR_LANG, "--lang"),
    fmt: str = typer.Option("txt", "--fmt", help="txt | json | md"),
):
    """[bold]Run OCR[/bold] on an image or PDF file."""
    if input_file.suffix.lower() == ".pdf":
        from docmax-demo.engine import ocr_pdf
        ocr_pdf(input_file, output, lang, fmt)
    else:
        from docmax-demo.engine import ocr_image
        ocr_image(input_file, output, lang, fmt)


@app.command("searchable")
def cmd_searchable(
    input_file: Path = typer.Argument(..., help="Scanned PDF to make searchable."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
    lang: str = typer.Option(DEFAULT_OCR_LANG, "--lang"),
    dpi: int = typer.Option(300, "--dpi"),
):
    """[bold]Create a searchable PDF[/bold] from a scanned PDF."""
    from docmax-demo.engine import make_searchable_pdf
    make_searchable_pdf(input_file, output, lang, dpi)


@app.command("batch-ocr")
def cmd_batch_ocr(
    directory: Path = typer.Argument(..., help="Directory to scan."),
    lang: str = typer.Option(DEFAULT_OCR_LANG, "--lang"),
    fmt: str = typer.Option("txt", "--fmt"),
    workers: int = typer.Option(DEFAULT_BATCH_WORKERS, "--workers"),
    no_recursive: bool = typer.Option(False, "--no-recursive"),
):
    """[bold]Batch OCR[/bold] all images and PDFs in a directory."""
    from docmax-demo.batch import batch_with_ocr
    batch_with_ocr(directory, lang, fmt, not no_recursive, workers)


# ===========================================================================
# Conversion Commands
# ===========================================================================

@app.command("convert")
def cmd_convert(
    input_file: Path = typer.Argument(..., help="Input document."),
    target_format: str = typer.Argument(..., help="pdf | docx | md | html | txt | rst | odt | epub"),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
):
    """[bold]Convert[/bold] a document to another format using Pandoc."""
    from docmax-demo.converter import convert
    convert(input_file, target_format, output)


@app.command("img2pdf")
def cmd_img2pdf(
    source: Path = typer.Argument(..., help="Image file or directory of images."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
):
    """[bold]Combine images[/bold] into a single PDF."""
    from docmax-demo.converter import images_to_pdf
    images_to_pdf(source, output)


@app.command("pdf2img")
def cmd_pdf2img(
    input_file: Path = typer.Argument(..., help="PDF file to convert."),
    output_dir: Optional[Path] = typer.Option(None, "-o", "--output-dir"),
    dpi: int = typer.Option(200, "--dpi"),
    fmt: str = typer.Option("png", "--fmt", help="png | jpeg | tiff"),
):
    """[bold]Convert PDF pages[/bold] to image files."""
    from docmax-demo.converter import pdf_to_images
    pdf_to_images(input_file, output_dir, dpi, fmt)


# ===========================================================================
# Extraction Commands
# ===========================================================================

@app.command("text")
def cmd_text(
    input_file: Path = typer.Argument(..., help="PDF file."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
):
    """[bold]Extract text[/bold] from a PDF."""
    from docmax-demo.extractor import extract_text
    extract_text(input_file, output)


@app.command("images")
def cmd_images(
    input_file: Path = typer.Argument(..., help="PDF file."),
    output_dir: Optional[Path] = typer.Option(None, "-o", "--output-dir"),
):
    """[bold]Extract embedded images[/bold] from a PDF."""
    from docmax-demo.extractor import extract_images
    extract_images(input_file, output_dir)


@app.command("metadata")
def cmd_metadata(
    input_file: Path = typer.Argument(..., help="PDF file."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
):
    """[bold]Display metadata[/bold] from a PDF."""
    from docmax-demo.extractor import extract_metadata
    extract_metadata(input_file, output)


@app.command("tables")
def cmd_tables(
    input_file: Path = typer.Argument(..., help="PDF file."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
    fmt: str = typer.Option("csv", "--fmt", help="csv | xlsx | json"),
):
    """[bold]Extract tables[/bold] from a PDF."""
    from docmax-demo.extractor import extract_tables
    extract_tables(input_file, output, fmt)


# ===========================================================================
# Image Processing Commands
# ===========================================================================

@app.command("enhance")
def cmd_enhance(
    input_file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
):
    """[bold]Enhance[/bold] image contrast, brightness, and sharpness."""
    from docmax-demo.processor import enhance
    enhance(input_file, output)


@app.command("deskew")
def cmd_deskew(
    input_file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
):
    """[bold]Correct the skew angle[/bold] of a scanned image."""
    from docmax-demo.processor import deskew
    deskew(input_file, output)


@app.command("denoise")
def cmd_denoise(
    input_file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
):
    """[bold]Remove noise[/bold] from an image."""
    from docmax-demo.processor import denoise
    denoise(input_file, output)


@app.command("resize")
def cmd_resize(
    input_file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
    width: Optional[int] = typer.Option(None, "--width"),
    height: Optional[int] = typer.Option(None, "--height"),
    scale: Optional[float] = typer.Option(None, "--scale"),
):
    """[bold]Resize[/bold] an image by width, height, or scale factor."""
    from docmax-demo.processor import resize
    resize(input_file, width, height, scale, output)


@app.command("preprocess")
def cmd_preprocess(
    input_file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
):
    """[bold]OCR preprocessing pipeline[/bold]: orientation → contrast → denoise → binarize."""
    from docmax-demo.processor import preprocess_for_ocr
    preprocess_for_ocr(input_file, output)


# ===========================================================================
# Batch Command
# ===========================================================================

@app.command("batch")
def cmd_batch(
    directory: Path = typer.Argument(...),
    ocr: bool = typer.Option(False, "--ocr"),
    compress: bool = typer.Option(False, "--compress"),
    convert_to: Optional[str] = typer.Option(None, "--convert"),
    lang: str = typer.Option(DEFAULT_OCR_LANG, "--lang"),
    fmt: str = typer.Option("txt", "--fmt"),
    workers: int = typer.Option(DEFAULT_BATCH_WORKERS, "--workers"),
    no_recursive: bool = typer.Option(False, "--no-recursive"),
):
    """[bold]Batch process[/bold] a directory of files."""
    from docmax-demo.batch import batch_with_ocr, batch_compress, batch_convert
    if ocr:
        batch_with_ocr(directory, lang, fmt, not no_recursive, workers)
    elif compress:
        batch_compress(directory, recursive=not no_recursive, workers=workers)
    elif convert_to:
        batch_convert(directory, convert_to, recursive=not no_recursive, workers=workers)
    else:
        console.print("[yellow]Specify an action: --ocr, --compress, or --convert <format>[/yellow]")
        raise typer.Exit(1)


# ===========================================================================
# Watch Command
# ===========================================================================

@app.command("watch")
def cmd_watch(
    directory: Path = typer.Argument(...),
    ocr: bool = typer.Option(False, "--ocr"),
    searchable: bool = typer.Option(False, "--searchable"),
    compress: bool = typer.Option(False, "--compress"),
    preprocess: bool = typer.Option(False, "--preprocess"),
    lang: str = typer.Option(DEFAULT_OCR_LANG, "--lang"),
    fmt: str = typer.Option("txt", "--fmt"),
):
    """[bold]Watch[/bold] a directory and auto-process new files."""
    if ocr:
        action = "ocr"
    elif searchable:
        action = "searchable"
    elif compress:
        action = "compress"
    elif preprocess:
        action = "preprocess"
    else:
        console.print("[yellow]Specify: --ocr, --searchable, --compress, or --preprocess[/yellow]")
        raise typer.Exit(1)
    watch(directory, action, lang, fmt)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    app()
