from pathlib import Path

from docmax-demo.extractor import (
    extract_text,
    extract_images,
    extract_metadata,
)

from docmax-demo.workflows.common import (
    select_single_pdf,
    get_output_name,
    success_screen,
)


def extract_text_workflow():
    input_file = select_single_pdf()

    if not input_file:
        return

    output = get_output_name(
        f"{input_file.stem}.txt"
    )

    if not output:
        return

    output_path = Path(output)

    extract_text(
        input_file,
        output_path,
    )

    success_screen(
        "Text Extracted",
        output_file=output_path.name,
        extra_lines=[
            f"Location : {output_path.resolve()}"
        ]
    )


def extract_images_workflow():
    input_file = select_single_pdf()

    if not input_file:
        return

    output_dir = (
        input_file.parent
        / f"{input_file.stem}_images"
    )

    extract_images(
        input_file,
        output_dir,
    )

    success_screen(
        "Images Extracted",
        extra_lines=[
            f"Folder : {output_dir.resolve()}"
        ]
    )


def extract_metadata_workflow():
    input_file = select_single_pdf()

    if not input_file:
        return

    output = get_output_name(
        f"{input_file.stem}_metadata.json"
    )

    if not output:
        return

    output_path = Path(output)

    extract_metadata(
        input_file,
        output_path,
    )

    success_screen(
        "Metadata Extracted",
        output_file=output_path.name,
        extra_lines=[
            f"Location : {output_path.resolve()}"
        ]
    )