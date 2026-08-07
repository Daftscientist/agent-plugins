"""Deterministic single-slide and bounded contact-sheet composition."""

import io
import math
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont, ImageOps

from office_mcp.constants import MAX_CONTACT_SHEET_SLIDES
from office_mcp.models.preview import PreviewLabels, PreviewQuality


@dataclass(frozen=True)
class ContactSheet:
    png: bytes
    slide_ids: list[str]
    width: int
    height: int


def auto_columns(count: int) -> int:
    if count <= 4:
        return 2
    if count <= 9:
        return 3
    if count <= 20:
        return 4
    return 5


def contact_sheets(
    pngs: list[bytes],
    slide_ids: list[str],
    names: list[str],
    numbers: list[int],
    labels: PreviewLabels,
    quality: PreviewQuality,
    columns: int | None,
) -> list[ContactSheet]:
    sheets: list[ContactSheet] = []
    for offset in range(0, len(pngs), MAX_CONTACT_SHEET_SLIDES):
        chunk = pngs[offset : offset + MAX_CONTACT_SHEET_SLIDES]
        chunk_ids = slide_ids[offset : offset + MAX_CONTACT_SHEET_SLIDES]
        chunk_names = names[offset : offset + MAX_CONTACT_SHEET_SLIDES]
        chunk_numbers = numbers[offset : offset + MAX_CONTACT_SHEET_SLIDES]
        images: list[Image.Image] = [Image.open(io.BytesIO(data)).convert("RGB") for data in chunk]
        cols = columns or auto_columns(len(images))
        rows = math.ceil(len(images) / cols)
        cell_width = 640 if quality is PreviewQuality.HIGH else 400
        # Use one bounded cell geometry while fitting each slide without
        # distortion. Mixed custom/preset slide sizes therefore letterbox
        # instead of being stretched to the first slide's aspect ratio.
        max_aspect = max(image.height / image.width for image in images)
        cell_height = round(cell_width * min(max_aspect, 1.0))
        label_height = 0 if labels is PreviewLabels.NONE else 32
        gutter = 18
        width = gutter + cols * (cell_width + gutter)
        height = gutter + rows * (cell_height + label_height + gutter)
        canvas = Image.new("RGB", (width, height), "#e5e7eb")
        draw = ImageDraw.Draw(canvas)
        font = ImageFont.load_default(size=16)
        for index, (image, name, number) in enumerate(
            zip(images, chunk_names, chunk_numbers, strict=True)
        ):
            row, col = divmod(index, cols)
            x = gutter + col * (cell_width + gutter)
            y = gutter + row * (cell_height + label_height + gutter)
            resized = ImageOps.contain(  # pyright: ignore[reportUnknownMemberType]
                image, (cell_width, cell_height), Image.Resampling.LANCZOS
            )
            image_x = x + (cell_width - resized.width) // 2
            image_y = y + (cell_height - resized.height) // 2
            canvas.paste(resized, (image_x, image_y))
            if labels is PreviewLabels.NUMBER:
                label = str(number)
            elif labels is PreviewLabels.NAME:
                label = name
            elif labels is PreviewLabels.NUMBER_AND_NAME:
                label = f"{number} · {name}"
            else:
                label = ""
            if label:
                draw.text((x, y + cell_height + 7), label[:80], fill="#111827", font=font)
        buffer = io.BytesIO()
        canvas.save(buffer, format="PNG", optimize=True)
        sheets.append(ContactSheet(buffer.getvalue(), chunk_ids, width, height))
    return sheets
