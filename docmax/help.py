from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

console = Console()
def show_install_help():
# 1. Build the text using from_markup so tags like [yellow] work perfectly
    content = Text.from_markup(
        f"""
    [bold cyan]docmax-demo Installation Options[/bold cyan]

    [yellow]Core:[/yellow]
    pip install docmax-demo

    [yellow]OCR Support:[/yellow]
    pip install docmax-demo{escape("[ocr]")}

    [yellow]Image Processing:[/yellow]
    pip install docmax-demo{escape("[image]")}

    [yellow]Table Extraction:[/yellow]
    pip install docmax-demo{escape("[tables]")}

    [yellow]Everything:[/yellow]
    pip install docmax-demo{escape("[full]")}
    """
    )

    # 2. Print the Panel containing our clean Text object
    console.print(
        Panel(
            content,
            title="Install Extras",
            border_style="cyan",
        )
    )
