from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.errors import LiveError
from docmax-demo.utils import save_recent_folder, load_recent_folder

console = Console()
def show_file_info(path):
    size_mb = path.stat().st_size / 1024 / 1024

    console.print(
        f"[cyan]{path.name}[/cyan]"
        f"  ({size_mb:.2f} MB)"
    )

def select_folder():
    recent_folder = load_recent_folder()

    choices = []

    if recent_folder and Path(recent_folder).exists():
        choices.append(
            f"Recent Folder ({Path(recent_folder).name})"
        )

    choices.extend([
        "Current Folder",
        "Choose Folder",
    ])

    mode = questionary.select(
        "How would you like to select files?",
        choices=choices,
    ).ask()

    if mode and mode.startswith("Recent Folder"):
        return Path(recent_folder)

    if mode == "Current Folder":
        return Path(".")

    folder_path = questionary.path(
        "Folder containing PDFs:"
    ).ask()

    if not folder_path:
        return None

    folder = Path(folder_path)

    save_recent_folder(str(folder))

    return folder


def select_multiple_pdfs():
    folder = select_folder()

    if not folder:
        return None, None

    pdfs = sorted(folder.glob("*.pdf"))

    if not pdfs:
        console.print(
            "[red]No PDF files found.[/red]"
        )
        return None, None

    selected = questionary.checkbox(
        "Select PDFs",
        choices=[pdf.name for pdf in pdfs],
    ).ask()

    if not selected:
        return None, None

    return folder, selected

def processing_screen(
    title,
    details=None,
):
    body = ""

    if details:
        body += "\n".join(details)

    console.print()

    console.print(
        Panel(
            body,
            title=title,
            border_style="cyan",
        )
    )

    console.print()
def select_single_pdf():
    folder = select_folder()

    if not folder:
        return None

    pdfs = sorted(folder.glob("*.pdf"))

    if not pdfs:
        console.print(
            "[red]No PDF files found.[/red]"
        )
        return None

    selected = questionary.select(
        "Select PDF",
        choices=[pdf.name for pdf in pdfs],
    ).ask()

    if not selected:
        return None

    return folder / selected

def show_file_info(path):
    size_mb = (
        path.stat().st_size
        / 1024
        / 1024
    )

    console.print(
        f"[cyan]File:[/cyan] "
        f"{path.name} "
        f"({size_mb:.2f} MB)\n"
    )

def select_single_image():
    folder = select_folder()

    if not folder:
        return None

    image_extensions = [
        "*.png",
        "*.jpg",
        "*.jpeg",
        "*.bmp",
        "*.webp",
        "*.tiff"
    ]

    images = []

    for ext in image_extensions:
        images.extend(folder.glob(ext))

    images = sorted(images)

    if not images:
        console.print(
            "[red]No image files found.[/red]"
        )
        return None

    selected = questionary.select(
        "Select Image",
        choices=[img.name for img in images],
    ).ask()

    if not selected:
        return None

    return folder / selected
def success_screen(
    title,
    output_file=None,
    extra_lines=None,
):
    body = f"✓ {title}\n"

    if output_file:
        body += f"\nOutput File : {output_file}"

    if extra_lines:
        for line in extra_lines:
            body += f"\n{line}"

    try:
        console.clear_live()

    except (AttributeError, LiveError,IndexError):
        pass

    console.print()

    console.print(
        Panel(
            body,
            title="Success",
            border_style="green",
        )
    )

    console.print()
    
def failure_screen(
    title,
    reason,
):
    body = f"✗ {title}\n"

    body += f"\nReason : {reason}"

    try:
        console.clear_live()

    except (AttributeError, LiveError ,IndexError):
        pass

    console.print()

    console.print(
        Panel(
            body,
            title="Failed",
            border_style="red",
        )
    )

    console.print()
def get_output_name(default_name):
    return questionary.text(
        "Output file:",
        default=default_name,
    ).ask()