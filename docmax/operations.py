"""
docmax-demo PDF Operations
Handles: merge, split, compress, rotate, page extraction, watermark, encrypt, decrypt
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from rich.progress import Progress, SpinnerColumn, TextColumn

from docmax-demo.utils import (
    abort, console, ensure_parent, ghostscript_bin,
    info, require_ghostscript, resolve_output, success, warn,
)
from docmax-demo.config import DEFAULT_COMPRESS_PRESET
from PIL import Image, ImageOps, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def merge(inputs: List[Path], output: Path) -> None:
    """Merge multiple PDF files into one."""
    try:
        from pypdf import PdfWriter
    except ImportError:
        abort("pypdf is required. Run: pip install pypdf")

    for f in inputs:
        if not f.exists():
            abort(f"File not found: {f}")

    writer = PdfWriter()
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Merging PDFs...", total=len(inputs))
        for f in inputs:
            from pypdf import PdfReader
            reader = PdfReader(str(f))
            for page in reader.pages:
                writer.add_page(page)
            progress.advance(task)

    ensure_parent(output)
    with open(output, "wb") as fh:
        writer.write(fh)
    success(f"Merged {len(inputs)} files -> [bold]{output}[/bold]")


# ---------------------------------------------------------------------------
# Split
# ---------------------------------------------------------------------------

def split(input_path: Path, output_dir: Optional[Path] = None) -> None:
    """Split a PDF into individual pages."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        abort("pypdf is required. Run: pip install pypdf")

    if not input_path.exists():
        abort(f"File not found: {input_path}")

    dest = output_dir or input_path.parent / (input_path.stem + "_pages")
    dest.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(input_path))
    total = len(reader.pages)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task(f"Splitting {total} pages...", total=total)
        for i, page in enumerate(reader.pages, start=1):
            writer = PdfWriter()
            writer.add_page(page)
            out_file = dest / f"{input_path.stem}_page_{i:04d}.pdf"
            with open(out_file, "wb") as fh:
                writer.write(fh)
            progress.advance(task)

    success(f"Split into {total} pages -> [bold]{dest}/[/bold]")


# ---------------------------------------------------------------------------
# Compress
# ---------------------------------------------------------------------------

def compress(input_path: Path, output: Optional[Path] = None, preset: str = DEFAULT_COMPRESS_PRESET) -> None:
    """Compress a PDF using Ghostscript."""
    require_ghostscript()

    if not input_path.exists():
        abort(f"File not found: {input_path}")

    out = output or resolve_output(input_path, None, "_compressed", ".pdf")
    ensure_parent(out)

    gs = ghostscript_bin()
    cmd = [
        gs,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{preset}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={out}",
        str(input_path),
    ]

    info(f"Compressing with preset '[bold]{preset}[/bold]'...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        abort(f"Ghostscript error:\n{result.stderr}")

    original_kb = input_path.stat().st_size / 1024
    compressed_kb = out.stat().st_size / 1024
    ratio = (1 - compressed_kb / original_kb) * 100 if original_kb > 0 else 0
    success(
        f"Compressed: {original_kb:.1f} KB -> {compressed_kb:.1f} KB "
        f"([green]{ratio:.1f}% reduction[/green]) -> [bold]{out}[/bold]"
    )


# ---------------------------------------------------------------------------
# Rotate
# ---------------------------------------------------------------------------

def rotate(input_path: Path, degrees: int, output: Optional[Path] = None) -> None:
    """Rotate all pages of a PDF by the given degrees (90, 180, 270)."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        abort("pypdf is required.")

    if degrees not in (90, 180, 270):
        abort("Rotation must be 90, 180, or 270 degrees.")

    if not input_path.exists():
        abort(f"File not found: {input_path}")

    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(degrees)
        writer.add_page(page)

    out = output or resolve_output(input_path, None, f"_rotated{degrees}", ".pdf")
    ensure_parent(out)
    with open(out, "wb") as fh:
        writer.write(fh)
    success(f"Rotated {len(reader.pages)} pages by {degrees} deg -> [bold]{out}[/bold]")


# ---------------------------------------------------------------------------
# Extract page range
# ---------------------------------------------------------------------------

def extract_pages(input_path: Path, page_range: str, output: Optional[Path] = None) -> None:
    """
    Extract a page range from a PDF.
    page_range format: "1-5" or "3" or "2,4,6"
    """
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        abort("pypdf is required.")

    if not input_path.exists():
        abort(f"File not found: {input_path}")

    reader = PdfReader(str(input_path))
    total = len(reader.pages)

    # Parse range
    pages: List[int] = []
    for part in page_range.split(","):
        part = part.strip()
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start, end = int(start_s), int(end_s)
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))

    # Validate
    invalid = [p for p in pages if p < 1 or p > total]
    if invalid:
        abort(f"Page(s) out of range (document has {total} pages): {invalid}")

    writer = PdfWriter()
    for p in pages:
        writer.add_page(reader.pages[p - 1])

    out = output or resolve_output(input_path, None, f"_pages_{page_range.replace(',', '-')}", ".pdf")
    ensure_parent(out)
    with open(out, "wb") as fh:
        writer.write(fh)
    success(f"Extracted {len(pages)} pages -> [bold]{out}[/bold]")


# ---------------------------------------------------------------------------
# Watermark
# ---------------------------------------------------------------------------

def watermark(input_path: Path, watermark_file: Path, output: Optional[Path] = None) -> None:
    """Overlay a watermark (PDF or image) on every page."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        abort("pypdf is required.")

    if not input_path.exists():
        abort(f"File not found: {input_path}")
    if not watermark_file.exists():
        abort(f"Watermark file not found: {watermark_file}")

    # If watermark is an image, convert it to a single-page PDF first
    wm_path = watermark_file
    if watermark_file.suffix.lower() in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
        wm_path = _image_to_pdf_watermark(watermark_file)

    wm_reader = PdfReader(str(wm_path))
    wm_page = wm_reader.pages[0]

    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        page.merge_page(wm_page)
        writer.add_page(page)

    out = output or resolve_output(input_path, None, "_watermarked", ".pdf")
    ensure_parent(out)
    with open(out, "wb") as fh:
        writer.write(fh)
    success(f"Watermarked {len(reader.pages)} pages -> [bold]{out}[/bold]")


def _image_to_pdf_watermark(image_path: Path) -> Path:
    """Convert an image file to a temporary single-page PDF for use as a watermark."""
    import tempfile
    try:
        import img2pdf
        from PIL import Image
    except ImportError:
        abort("img2pdf and Pillow are required for image watermarks.")

    tmp = Path(tempfile.mktemp(suffix=".pdf"))
    with open(tmp, "wb") as fh:
        fh.write(img2pdf.convert(str(image_path)))
    return tmp


# ---------------------------------------------------------------------------
# Encrypt
# ---------------------------------------------------------------------------

def encrypt(input_path: Path, password: str, output: Optional[Path] = None) -> None:
    """Encrypt a PDF with a password."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        abort("pypdf is required.")

    if not input_path.exists():
        abort(f"File not found: {input_path}")

    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    out = output or resolve_output(input_path, None, "_encrypted", ".pdf")
    ensure_parent(out)
    with open(out, "wb") as fh:
        writer.write(fh)
    success(f"Encrypted -> [bold]{out}[/bold]")


# ---------------------------------------------------------------------------
# Decrypt
# ---------------------------------------------------------------------------

def decrypt(input_path: Path, password: str, output: Optional[Path] = None) -> None:
    """Decrypt a password-protected PDF."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        abort("pypdf is required.")

    if not input_path.exists():
        abort(f"File not found: {input_path}")

    reader = PdfReader(str(input_path))
    if reader.is_encrypted:
        if not reader.decrypt(password):
            abort("Incorrect password or unsupported encryption.")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    out = output or resolve_output(input_path, None, "_decrypted", ".pdf")
    ensure_parent(out)
    with open(out, "wb") as fh:
        writer.write(fh)
    success(f"Decrypted -> [bold]{out}[/bold]")



def resize_image(input_path, output_path, width, height):
    with Image.open(input_path) as img:
        img.resize((width, height)).save(output_path)


def convert_image(input_path, output_path, fmt):
    with Image.open(input_path) as img:
        if fmt.upper() in ["JPEG", "JPG"]:
            img = img.convert("RGB")

        img.save(output_path, format=fmt.upper())


def compress_image(input_path, output_path, quality=85):
    with Image.open(input_path) as img:
        img.save(
            output_path,
            optimize=True,
            quality=quality
        )


def rotate_image(input_path, output_path, angle):
    with Image.open(input_path) as img:
        img.rotate(-angle, expand=True).save(output_path)


def crop_image(input_path, output_path,
               left, top, right, bottom):

    with Image.open(input_path) as img:

        width, height = img.size

        left = max(0, left)
        top = max(0, top)

        right = min(width, right)
        bottom = min(height, bottom)

        if left >= right:
            raise ValueError(
                "Right must be greater than Left."
            )

        if top >= bottom:
            raise ValueError(
                "Bottom must be greater than Top."
            )

        cropped = img.crop(
            (left, top, right, bottom)
        )

        cropped.save(output_path)


def flip_horizontal(input_path, output_path):
    with Image.open(input_path) as img:
        ImageOps.mirror(img).save(output_path)


def flip_vertical(input_path, output_path):
    with Image.open(input_path) as img:
        ImageOps.flip(img).save(output_path)

def add_text_watermark(
        input_path,
        output_path,
        text):

    with Image.open(input_path).convert("RGBA") as base:

        overlay = Image.new(
            "RGBA",
            base.size,
            (255, 255, 255, 0)
        )

        draw = ImageDraw.Draw(overlay)

        try:
            font = ImageFont.truetype(
                "arial.ttf",
                40
            )
        except:
            font = ImageFont.load_default()

        x = base.width - 250
        y = base.height - 60

        draw.text(
            (x, y),
            text,
            fill=(255, 255, 255, 150),
            font=font
        )

        result = Image.alpha_composite(
            base,
            overlay
        )

        result.convert("RGB").save(output_path)


def remove_background(input_path, output_path):

    try:
        from rembg import remove

    except ImportError:

        abort(
            "Background removal requires extra packages.\n"
            "Run:\n"
            "pip install docmax-demo[image]"
        )

    with open(input_path, "rb") as f:
        data = f.read()

    result = remove(data)

    with open(output_path, "wb") as f:
        f.write(result)