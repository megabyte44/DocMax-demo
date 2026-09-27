"""
docmax-demo Setup — cross-platform dependency installer.

Supports:
  Windows  → winget
  macOS    → Homebrew (brew)
  Linux    → apt / apt-get  (Debian/Ubuntu)
             dnf            (Fedora/RHEL)
             pacman         (Arch)
             zypper         (openSUSE)
             Falls back to manual instructions for unsupported package managers.
"""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path
from shutil import which

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from docmax-demo.config_manager import set_tool_path

console = Console()

SYSTEM = platform.system()  # "Windows" | "Darwin" | "Linux"


# ---------------------------------------------------------------------------
# Package specs per manager
# ---------------------------------------------------------------------------

# Each entry: (display_name, winget_id, brew_formula, apt_pkg, dnf_pkg, pacman_pkg)
PACKAGES = [
    ("Tesseract OCR", "UB-Mannheim.TesseractOCR", "tesseract",      "tesseract-ocr",    "tesseract",         "tesseract"),
    ("Ghostscript",   "ArtifexSoftware.GhostScript","ghostscript",   "ghostscript",      "ghostscript",       "ghostscript"),
    ("Poppler",       "oschwartz10612.Poppler",      "poppler",       "poppler-utils",    "poppler-utils",     "poppler"),
    ("Pandoc",        "JohnMacFarlane.Pandoc",       "pandoc",        "pandoc",           "pandoc",            "pandoc"),
    ("MiKTeX/TeX",    "MiKTeX.MiKTeX",               "miktex",        "texlive-xetex",    "texlive-xetex",     "texlive-most"),
]


# ---------------------------------------------------------------------------
# Package manager detection
# ---------------------------------------------------------------------------

def _find_winget() -> str | None:
    p = which("winget")
    if p:
        return p
    candidate = (
        Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps" / "winget.exe"
    )
    return str(candidate) if candidate.exists() else None


def _find_brew() -> str | None:
    for p in ["/opt/homebrew/bin/brew", "/usr/local/bin/brew"]:
        if Path(p).exists():
            return p
    return which("brew")


def _find_apt() -> str | None:
    return which("apt") or which("apt-get")


def _find_dnf() -> str | None:
    return which("dnf") or which("yum")


def _find_pacman() -> str | None:
    return which("pacman")


def _find_zypper() -> str | None:
    return which("zypper")


# ---------------------------------------------------------------------------
# Installer helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str], name: str) -> bool:
    """Run an install command; return True on success."""
    console.print(f"  [cyan]Installing {name}...[/cyan]")
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            console.print(f"  [green]✓ {name} installed.[/green]")
            return True
        else:
            console.print(f"  [yellow]⚠ {name} returned exit code {result.returncode} — may already be installed.[/yellow]")
            return True  # non-zero often means "already installed"
    except FileNotFoundError:
        console.print(f"  [red]✗ installer not found for {name}[/red]")
        return False
    except Exception as exc:
        console.print(f"  [red]✗ {name}: {exc}[/red]")
        return False


def _install_windows(winget: str) -> None:
    console.print("\n[bold cyan]Installing via winget...[/bold cyan]\n")
    for display, winget_id, *_ in PACKAGES:
        _run([winget, "install", "--id", winget_id, "-e", "--accept-source-agreements", "--accept-package-agreements"], display)


def _install_mac(brew: str) -> None:
    console.print("\n[bold cyan]Installing via Homebrew...[/bold cyan]\n")
    for display, _, brew_formula, *_ in PACKAGES:
        if brew_formula == "miktex":
            # MiKTeX has a cask on Mac
            _run([brew, "install", "--cask", "miktex"], display)
        else:
            _run([brew, "install", brew_formula], display)


def _install_linux_apt(apt: str) -> None:
    console.print("\n[bold cyan]Installing via apt...[/bold cyan]\n")
    pkgs = [row[3] for row in PACKAGES]  # apt_pkg column
    # Update first (best-effort)
    subprocess.run(["sudo", apt, "update", "-y"], check=False)
    _run(["sudo", apt, "install", "-y"] + pkgs, "all dependencies")


def _install_linux_dnf(dnf: str) -> None:
    console.print("\n[bold cyan]Installing via dnf...[/bold cyan]\n")
    pkgs = [row[4] for row in PACKAGES]  # dnf_pkg column
    _run(["sudo", dnf, "install", "-y"] + pkgs, "all dependencies")


def _install_linux_pacman(pacman: str) -> None:
    console.print("\n[bold cyan]Installing via pacman...[/bold cyan]\n")
    pkgs = [row[5] for row in PACKAGES]  # pacman_pkg column
    _run(["sudo", pacman, "-S", "--noconfirm"] + pkgs, "all dependencies")


def _install_linux_zypper(zypper: str) -> None:
    console.print("\n[bold cyan]Installing via zypper...[/bold cyan]\n")
    pkgs = [row[3] for row in PACKAGES]
    _run(["sudo", zypper, "install", "-y"] + pkgs, "all dependencies")


def _show_manual_instructions() -> None:
    console.print(Panel(
        "[bold yellow]No supported package manager found.[/bold yellow]\n\n"
        "Please install the following manually:\n\n"
        "  • Tesseract  → https://tesseract-ocr.github.io/tessdoc/Installation.html\n"
        "  • Ghostscript → https://ghostscript.com/releases/gsdnld.html\n"
        "  • Poppler    → https://poppler.freedesktop.org\n"
        "  • Pandoc     → https://pandoc.org/installing.html\n"
        "  • MiKTeX     → https://miktex.org/download  (optional, for PDF conversion)\n",
        title="[yellow]Manual Installation Required[/yellow]",
        border_style="yellow",
    ))


# ---------------------------------------------------------------------------
# Path discovery (cross-platform, no .exe assumptions)
# ---------------------------------------------------------------------------

def _discover_tool(binary_names: list[str], search_dirs: list[Path] | None = None) -> str | None:
    """Find a tool binary on PATH or in common install dirs."""
    # 1. Check PATH first (works on all platforms after proper install)
    for name in binary_names:
        found = which(name)
        if found:
            return found

    # 2. Search extra dirs (useful on Windows where PATH may not be updated yet)
    if search_dirs:
        suffixes = [".exe", ""] if SYSTEM == "Windows" else [""]
        for directory in search_dirs:
            if not directory.exists():
                continue
            for name in binary_names:
                for suffix in suffixes:
                    for match in directory.rglob(f"{name}{suffix}"):
                        if match.is_file():
                            return str(match)
    return None


def _windows_search_dirs() -> list[Path]:
    return [
        Path("C:/Program Files"),
        Path("C:/Program Files (x86)"),
        Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages",
        Path.home() / "AppData" / "Local" / "Programs",
    ]


def _mac_search_dirs() -> list[Path]:
    return [
        Path("/opt/homebrew/bin"),
        Path("/usr/local/bin"),
        Path("/opt/homebrew/Cellar"),
    ]


def _linux_search_dirs() -> list[Path]:
    return [
        Path("/usr/bin"),
        Path("/usr/local/bin"),
        Path("/snap/bin"),
        Path.home() / ".local" / "bin",
    ]


def _get_search_dirs() -> list[Path]:
    if SYSTEM == "Windows":
        return _windows_search_dirs()
    elif SYSTEM == "Darwin":
        return _mac_search_dirs()
    else:
        return _linux_search_dirs()


def _discover_and_save_all() -> dict[str, str | None]:
    """Find all tools and persist their paths to config."""
    search_dirs = _get_search_dirs()

    tools = {
        "tesseract":  _discover_tool(["tesseract"], search_dirs),
        "ghostscript": _discover_tool(["gs", "gswin64c", "gswin32c"], search_dirs),
        "pandoc":     _discover_tool(["pandoc"], search_dirs),
        "poppler":    _discover_tool(["pdfinfo", "pdftotext"], search_dirs),
        "xelatex":    _discover_tool(["xelatex"], search_dirs),
    }

    table = Table(title="Discovered Tools")
    table.add_column("Tool")
    table.add_column("Path")
    table.add_column("Status")

    for tool, path in tools.items():
        if path:
            set_tool_path(tool, path)
            table.add_row(tool, path, "[green]✓ Found[/green]")
        else:
            table.add_row(tool, "—", "[yellow]Not found[/yellow]")

    console.print(table)
    return tools


# ---------------------------------------------------------------------------
# PATH warning (shown after pip install if tools missing)
# ---------------------------------------------------------------------------

def warn_missing_tools() -> None:
    """
    Called at CLI startup. If critical tools are not on PATH and not in config,
    print a helpful one-time notice directing the user to run `docmax-demo setup`.
    """
    from docmax-demo.dependencies import has_tesseract, has_ghostscript

    missing = []
    if not has_tesseract():
        missing.append("Tesseract OCR  (needed for OCR features)")
    if not has_ghostscript():
        missing.append("Ghostscript    (needed for PDF compression)")

    if not missing:
        return

    lines = "\n".join(f"  • {m}" for m in missing)
    console.print(Panel(
        f"[bold yellow]Some external tools are not on your PATH:[/bold yellow]\n\n"
        f"{lines}\n\n"
        f"Run [bold cyan]docmax-demo setup[/bold cyan] to install them automatically,\n"
        f"or add them to your PATH if already installed.\n\n"
        f"[dim]After installing, run [bold]docmax-demo doctor[/bold] to verify.[/dim]",
        title="[yellow]⚠  Missing Dependencies[/yellow]",
        border_style="yellow",
    ))


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def setup_dependencies() -> None:
    console.print(Panel(
        f"[bold cyan]docmax-demo Setup[/bold cyan]\n"
        f"Detected OS: [bold]{SYSTEM}[/bold] ({platform.machine()})\n\n"
        f"This will install: Tesseract, Ghostscript, Poppler, Pandoc, MiKTeX",
        title="Setup",
        border_style="cyan",
    ))

    if SYSTEM == "Windows":
        winget = _find_winget()
        if winget:
            _install_windows(winget)
        else:
            console.print("[red]winget not found.[/red] Install 'App Installer' from the Microsoft Store.")

    elif SYSTEM == "Darwin":
        brew = _find_brew()
        if brew:
            _install_mac(brew)
        else:
            console.print(
                "[yellow]Homebrew not found.[/yellow]\n"
                "Install it first: [cyan]https://brew.sh[/cyan]\n"
                "Then re-run [bold]docmax-demo setup[/bold]."
            )
            return

    elif SYSTEM == "Linux":
        if apt := _find_apt():
            _install_linux_apt(apt)
        elif dnf := _find_dnf():
            _install_linux_dnf(dnf)
        elif pacman := _find_pacman():
            _install_linux_pacman(pacman)
        elif zypper := _find_zypper():
            _install_linux_zypper(zypper)
        else:
            _show_manual_instructions()
            return

    else:
        _show_manual_instructions()
        return

    # After install: scan PATH + common dirs and save found paths
    console.print("\n[bold cyan]Scanning for installed tools...[/bold cyan]\n")
    found = _discover_and_save_all()

    missing = [k for k, v in found.items() if not v]
    if missing:
        console.print(
            f"\n[yellow]Note:[/yellow] {', '.join(missing)} not found on PATH yet.\n"
            "If you just installed them, you may need to [bold]restart your terminal[/bold]\n"
            "or open a new shell so PATH updates take effect, then run [bold]docmax-demo doctor[/bold]."
        )
    else:
        console.print("\n[bold green]✓ Setup complete. All tools found and configured.[/bold green]")
