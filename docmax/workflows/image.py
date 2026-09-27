import questionary
from pathlib import Path
from rich.console import Console

from docmax-demo.menu import image_menu
from docmax-demo.operations import (
    resize_image,
    convert_image,
    compress_image,
    rotate_image,
    crop_image,
    add_text_watermark,
    remove_background,
    flip_horizontal,
    flip_vertical
)

from docmax-demo.workflows.common import (
    failure_screen,
    select_single_image,
    get_output_name,
    success_screen,
    show_file_info,
)

console = Console()
def resize_workflow():
    input_file = select_single_image()
    if not input_file:
        return

    show_file_info(input_file)

    width = questionary.text(
        "Width:",
        default="800"
    ).ask()

    height = questionary.text(
        "Height:",
        default="600"
    ).ask()

    output = get_output_name(
        f"{input_file.stem}_resized{input_file.suffix}"
    )

    if not output:
        return

    output_path = Path(output)

    resize_image(
        input_file,
        output_path,
        int(width),
        int(height)
    )

    success_screen(
        "Resize Complete",
        output_file=output_path.name,
        extra_lines=[
            f"Dimensions : {width} x {height}",
            f"Location   : {output_path.resolve()}"
        ]
    )


def convert_format_workflow():
    input_file = select_single_image()
    if not input_file:
        return

    show_file_info(input_file)

    fmt = questionary.select(
        "Convert to:",
        choices=["JPEG", "PNG", "WEBP", "BMP"]
    ).ask()

    extension_map = {
        "JPEG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
        "BMP": ".bmp"
    }

    output = get_output_name(
        f"{input_file.stem}{extension_map[fmt]}"
    )

    if not output:
        return

    output_path = Path(output)

    convert_image(
        input_file,
        output_path,
        fmt
    )

    success_screen(
        "Conversion Complete",
        output_file=output_path.name,
        extra_lines=[
            f"Format   : {fmt}",
            f"Location : {output_path.resolve()}"
        ]
    )


def flip_h_workflow():
    input_file = select_single_image()
    if not input_file:
        return

    output = get_output_name(
        f"{input_file.stem}_flip_h{input_file.suffix}"
    )

    if not output:
        return

    output_path = Path(output)

    flip_horizontal(
        input_file,
        output_path
    )

    success_screen(
        "Image Flipped",
        output_file=output_path.name,
        extra_lines=[
            "Direction : Horizontal",
            f"Location  : {output_path.resolve()}"
        ]
    )


def flip_v_workflow():
    input_file = select_single_image()
    if not input_file:
        return

    output = get_output_name(
        f"{input_file.stem}_flip_v{input_file.suffix}"
    )

    if not output:
        return

    output_path = Path(output)

    flip_vertical(
        input_file,
        output_path
    )

    success_screen(
        "Image Flipped",
        output_file=output_path.name,
        extra_lines=[
            "Direction : Vertical",
            f"Location  : {output_path.resolve()}"
        ]
    )


def compress_image_workflow():
    input_file = select_single_image()
    if not input_file:
        return

    quality = questionary.select(
        "Quality:",
        choices=["95", "85", "75", "50"]
    ).ask()

    output = get_output_name(
        f"{input_file.stem}_compressed{input_file.suffix}"
    )

    if not output:
        return

    output_path = Path(output)

    compress_image(
        input_file,
        output_path,
        int(quality)
    )

    success_screen(
        "Compression Complete",
        output_file=output_path.name,
        extra_lines=[
            f"Quality  : {quality}",
            f"Location : {output_path.resolve()}"
        ]
    )


def rotate_image_workflow():
    input_file = select_single_image()
    if not input_file:
        return

    angle = questionary.select(
        "Rotation:",
        choices=["90", "180", "270"]
    ).ask()

    output = get_output_name(
        f"{input_file.stem}_rotated{angle}{input_file.suffix}"
    )

    if not output:
        return

    output_path = Path(output)

    rotate_image(
        input_file,
        output_path,
        int(angle)
    )

    success_screen(
        "Rotation Complete",
        output_file=output_path.name,
        extra_lines=[
            f"Angle    : {angle}°",
            f"Location : {output_path.resolve()}"
        ]
    )


def crop_workflow():
    input_file = select_single_image()
    if not input_file:
        return

    left = int(questionary.text("Left:", default="0").ask())
    top = int(questionary.text("Top:", default="0").ask())
    right = int(questionary.text("Right:").ask())
    bottom = int(questionary.text("Bottom:").ask())

    output = get_output_name(
        f"{input_file.stem}_cropped{input_file.suffix}"
    )

    if not output:
        return

    output_path = Path(output)

    crop_image(
        input_file,
        output_path,
        left,
        top,
        right,
        bottom
    )

    success_screen(
        "Crop Complete",
        output_file=output_path.name,
        extra_lines=[
            f"Location : {output_path.resolve()}"
        ]
    )


def watermark_image_workflow():
    input_file = select_single_image()
    if not input_file:
        return

    text = questionary.text(
        "Watermark text:",
        default="docmax-demo"
    ).ask()

    output = get_output_name(
        f"{input_file.stem}_watermarked{input_file.suffix}"
    )

    if not output:
        return

    output_path = Path(output)

    add_text_watermark(
        input_file,
        output_path,
        text
    )

    success_screen(
        "Watermark Complete",
        output_file=output_path.name,
        extra_lines=[
            f"Location : {output_path.resolve()}"
        ]
    )


def remove_bg_workflow():
    input_file = select_single_image()
    if not input_file:
        return

    output = get_output_name(
        f"{input_file.stem}_nobg.png"
    )

    if not output:
        return

    output_path = Path(output)

    remove_background(
        input_file,
        output_path
    )

    success_screen(
        "Background Removed",
        output_file=output_path.name,
        extra_lines=[
            f"Location : {output_path.resolve()}"
        ]
    )