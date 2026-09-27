from pathlib import Path

import questionary

from docmax-demo.watcher import watch


def auto_ocr_workflow():
    folder = questionary.path(
        "Folder to watch:"
    ).ask()

    if not folder:
        return

    fmt = questionary.select(
        "Output format:",
        choices=[
            "txt",
            "pdf"
        ]
    ).ask()

    lang = questionary.text(
        "OCR language:",
        default="eng"
    ).ask()

    watch(
        Path(folder),
        action="ocr",
        lang=lang,
        fmt=fmt
    )


def auto_searchable_workflow():
    folder = questionary.path(
        "Folder to watch:"
    ).ask()

    if not folder:
        return

    lang = questionary.text(
        "OCR language:",
        default="eng"
    ).ask()

    watch(
        Path(folder),
        action="searchable",
        lang=lang
    )


def auto_compress_workflow():
    folder = questionary.path(
        "Folder to watch:"
    ).ask()

    if not folder:
        return

    watch(
        Path(folder),
        action="compress"
    )


def auto_preprocess_workflow():
    folder = questionary.path(
        "Folder to watch:"
    ).ask()

    if not folder:
        return

    watch(
        Path(folder),
        action="preprocess"
    )