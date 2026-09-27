import questionary
from rich.console import Console
from rich.table import Table

from docmax-demo.setup import setup_dependencies
from docmax-demo.dependencies import doctor
from docmax-demo.config_manager import (
    load_config,
    save_config,
)

console = Console()


def settings_ocr_workflow():
    config = load_config()

    lang = questionary.select(
        "Default OCR language",
        choices=[
            "eng",
            "hin",
            "tel",
            "tam",
            "jpn",
        ],
        default=config.get(
            "ocr_language",
            "eng",
        ),
    ).ask()

    dpi = int(
        questionary.text(
            "DPI",
            default=str(
                config.get(
                    "ocr_dpi",
                    300,
                )
            ),
        ).ask()
    )

    workers = int(
        questionary.text(
            "Workers",
            default=str(
                config.get(
                    "ocr_workers",
                    4,
                )
            ),
        ).ask()
    )

    config["ocr_language"] = lang
    config["ocr_dpi"] = dpi
    config["ocr_workers"] = workers

    save_config(config)

    console.print(
        "\n[green]OCR settings saved.[/green]\n"
    )


def doctor_workflow():
    doctor()


def setup_workflow():
    setup_dependencies()


def show_paths_workflow():
    config = load_config()

    table = Table(
        title="Configured Tools"
    )

    table.add_column("Tool")
    table.add_column("Path")

    for tool in [
        "tesseract",
        "poppler",
        "ghostscript",
        "pandoc",
        "xelatex",
    ]:
        table.add_row(
            tool,
            config.get(
                tool,
                "Not configured",
            ),
        )

    console.print(table)