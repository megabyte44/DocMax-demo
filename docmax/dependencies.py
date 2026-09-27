"""
docmax-demo Dependencies — checks whether external tools are available.

Resolution order for each tool:
  1. Saved path in ~/.docmax-demo/config.json  (set by `docmax-demo setup`)
  2. shutil.which (tool is on system PATH)
"""

from __future__ import annotations

from pathlib import Path
from shutil import which

from rich.console import Console
from rich.table import Table

from docmax-demo.config_manager import get_tool_path

console = Console()


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def has_tesseract() -> bool:
    return bool(get_tool_path("tesseract") or which("tesseract"))


def has_ghostscript() -> bool:
    # Saved under key "ghostscript" by setup.py
    if get_tool_path("ghostscript"):
        return True
    # Also check common binary names directly on PATH
    return any(which(b) for b in ("gs", "gswin64c", "gswin32c"))


def has_poppler() -> bool:
    if get_tool_path("poppler"):
        return True
    return bool(which("pdfinfo") or which("pdftotext"))


def has_pandoc() -> bool:
    return bool(get_tool_path("pandoc") or which("pandoc"))


def has_xelatex() -> bool:
    return bool(get_tool_path("xelatex") or which("xelatex"))


# ---------------------------------------------------------------------------
# Doctor (system check table)
# ---------------------------------------------------------------------------

def doctor() -> None:
    table = Table(title="docmax-demo System Check")
    table.add_column("Dependency", style="bold")
    table.add_column("Status")
    table.add_column("Path / Note", style="dim")

    checks = [
        ("Tesseract OCR", has_tesseract, "tesseract", "OCR features"),
        ("Ghostscript",   has_ghostscript, "ghostscript", "PDF compression"),
        ("Poppler",       has_poppler, "poppler", "PDF→image, OCR on PDFs"),
        ("Pandoc",        has_pandoc, "pandoc", "Document conversion"),
        ("XeLaTeX",       has_xelatex, "xelatex", "PDF generation via Pandoc"),
    ]

    any_missing = False
    for name, check_fn, config_key, purpose in checks:
        ok = check_fn()
        saved_path = get_tool_path(config_key)

        if ok:
            note = saved_path if saved_path else "(on PATH)"
            table.add_row(name, "[green]✓ Installed[/green]", note)
        else:
            table.add_row(name, "[red]✗ Missing[/red]", f"needed for {purpose}")
            any_missing = True

    console.print(table)

    if any_missing:
        console.print(
            "\n[yellow]Run [bold cyan]docmax-demo setup[/bold cyan] to install missing tools.[/yellow]"
        )
    else:
        console.print("\n[green]All dependencies satisfied.[/green]")


# ---------------------------------------------------------------------------
# Gated checks (used inside workflows — print hint and return bool)
# ---------------------------------------------------------------------------

def _missing_hint(tool_name: str) -> None:
    console.print(
        f"\n[red]{tool_name} is not installed or not on PATH.[/red]\n"
        "Run [bold cyan]docmax-demo setup[/bold cyan] to install it automatically.\n"
        "Then run [bold cyan]docmax-demo doctor[/bold cyan] to verify.\n"
    )


def check_tesseract() -> bool:
    if has_tesseract():
        return True
    _missing_hint("Tesseract OCR")
    return False


def check_ghostscript() -> bool:
    if has_ghostscript():
        return True
    _missing_hint("Ghostscript")
    return False


def check_poppler() -> bool:
    if has_poppler():
        return True
    _missing_hint("Poppler")
    return False


def check_pandoc() -> bool:
    if has_pandoc():
        return True
    _missing_hint("Pandoc")
    return False
