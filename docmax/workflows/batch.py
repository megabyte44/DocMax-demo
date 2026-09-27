import questionary

from docmax-demo.batch import (
    batch_convert,
    batch_compress,
    batch_with_ocr,
)

from docmax-demo.workflows.common import select_folder


def batch_convert_workflow():
    folder = select_folder()

    if not folder:
        return

    target = questionary.select(
        "Convert documents to:",
        choices=[
            "pdf",
            "docx",
            "md",
        ],
    ).ask()

    batch_convert(
        folder,
        target,
    )


def batch_compress_workflow():
    folder = select_folder()

    if not folder:
        return

    batch_compress(
        folder,
    )


def batch_ocr_folder_workflow():
    folder = select_folder()

    if not folder:
        return

    lang = questionary.text(
        "OCR language:",
        default="eng",
    ).ask()

    fmt = questionary.select(
        "Output format:",
        choices=[
            "txt",
            "pdf",
        ],
    ).ask()

    batch_with_ocr(
        folder,
        lang,
        fmt,
    )