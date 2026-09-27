"""
docmax-demo Utilities — shared helpers used across all modules.

Config is now fully in config_manager.py (single source of truth).
recent_folder is saved/loaded via config_manager, not a local .docmax-demo.json.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel

console = Console()


# ---------------------------------------------------------------------------
# Recent folder — delegate to config_manager (no more cwd/.docmax-demo.json)
# ---------------------------------------------------------------------------

def save_recent_folder(folder: str) -> None:
    from docmax-demo.config_manager import save_recent_folder as _save
    _save(folder)


def load_recent_folder() -> Optional[str]:
    from docmax-demo.config_manager import load_recent_folder as _load
    return _load()


# ---------------------------------------------------------------------------
# Output path helpers
# ---------------------------------------------------------------------------

def resolve_output(
    input_path: Path,
    output: Optional[str],
    suffix: str,
    ext: Optional[str] = None,
) -> Path:
    if output:
        return Path(output)
    src = Path(input_path)
    new_ext = ext if ext is not None else src.suffix
    return src.with_name(src.stem + suffix + new_ext)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------

def require_tool(tool: str, install_hint: str = "") -> None:
    """Abort with a helpful message if an external tool is not found."""
    # First check saved config path
    from docmax-demo.config_manager import get_tool_path
    saved = get_tool_path(tool)
    if saved and Path(saved).exists():
        return  # found via saved config

    if shutil.which(tool) is None:
        msg = f"[bold red]Missing dependency:[/bold red] '{tool}' was not found on PATH."
        if install_hint:
            msg += f"\n[dim]{install_hint}[/dim]"
        msg += "\n\nRun [bold cyan]docmax-demo setup[/bold cyan] to install it automatically."
        console.print(Panel(msg, title="[red]Dependency Error[/red]", border_style="red"))
        sys.exit(1)


def require_tesseract() -> None:
    from docmax-demo.dependencies import has_tesseract
    if not has_tesseract():
        console.print(Panel(
            "[bold red]Missing dependency:[/bold red] Tesseract OCR not found.\n"
            "[dim]Run: [bold cyan]docmax-demo setup[/bold cyan][/dim]",
            title="[red]Dependency Error[/red]", border_style="red",
        ))
        sys.exit(1)


def require_ghostscript() -> None:
    from docmax-demo.dependencies import has_ghostscript
    if not has_ghostscript():
        console.print(Panel(
            "[bold red]Missing dependency:[/bold red] Ghostscript not found.\n"
            "[dim]Run: [bold cyan]docmax-demo setup[/bold cyan][/dim]",
            title="[red]Dependency Error[/red]", border_style="red",
        ))
        sys.exit(1)


def require_pandoc() -> None:
    from docmax-demo.dependencies import has_pandoc
    if not has_pandoc():
        console.print(Panel(
            "[bold red]Missing dependency:[/bold red] Pandoc not found.\n"
            "[dim]Run: [bold cyan]docmax-demo setup[/bold cyan][/dim]",
            title="[red]Dependency Error[/red]", border_style="red",
        ))
        sys.exit(1)


def ghostscript_bin() -> str:
    """Return the Ghostscript binary path — prefers saved config path."""
    from docmax-demo.config_manager import get_tool_path
    saved = get_tool_path("ghostscript")
    if saved and Path(saved).exists():
        return saved
    for candidate in ("gs", "gswin64c", "gswin32c"):
        if shutil.which(candidate):
            return candidate
    return "gs"  # will fail gracefully with a clear error


# ---------------------------------------------------------------------------
# Pretty printing helpers
# ---------------------------------------------------------------------------

def success(msg: str) -> None:
    console.print(f"[bold green]OK[/bold green]  {msg}")


def info(msg: str) -> None:
    console.print(f"[bold cyan]INFO[/bold cyan]  {msg}")


def warn(msg: str) -> None:
    console.print(f"[bold yellow]WARN[/bold yellow]  {msg}")


def error(msg: str) -> None:
    console.print(f"[bold red]ERROR[/bold red]  {msg}")


def abort(msg: str) -> None:
    error(msg)
    sys.exit(1)


# ---------------------------------------------------------------------------
# File collection helpers
# ---------------------------------------------------------------------------

def collect_files(
    directory: Path,
    extensions: set[str],
    recursive: bool = True,
) -> List[Path]:
    pattern = "**/*" if recursive else "*"
    files = []
    for ext in extensions:
        files.extend(directory.glob(f"{pattern}{ext}"))
    return sorted(set(files))
