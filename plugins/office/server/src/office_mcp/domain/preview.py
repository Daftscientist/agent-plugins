"""Deterministic single-slide and bounded contact-sheet composition."""

import io
import math
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

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
    labels: PreviewLabels,
    quality: PreviewQuality,
    columns: int | None,
) -> list[ContactSheet]:
    sheets: list[ContactSheet] = []
    for offset in range(0, len(pngs), MAX_CONTACT_SHEET_SLIDES):
        chunk = pngs[offset : offset + MAX_CONTACT_SHEET_SLIDES]
        chunk_ids = slide_ids[offset : offset + MAX_CONTACT_SHEET_SLIDES]
        chunk_names = names[offset : offset + MAX_CONTACT_SHEET_SLIDES]
        images: list[Image.Image] = [Image.open(io.BytesIO(data)).convert("RGB") for data in chunk]
        cols = columns or auto_columns(len(images))
        rows = math.ceil(len(images) / cols)
        cell_width = 640 if quality is PreviewQuality.HIGH else 400
        aspect = images[0].height / images[0].width
        cell_height = round(cell_width * aspect)
        label_height = 0 if labels is PreviewLabels.NONE else 32
        gutter = 18
        width = gutter + cols * (cell_width + gutter)
        height = gutter + rows * (cell_height + label_height + gutter)
        canvas = Image.new("RGB", (width, height), "#e5e7eb")
        draw = ImageDraw.Draw(canvas)
        font = ImageFont.load_default(size=16)
        for index, (image, name) in enumerate(zip(images, chunk_names, strict=True)):
            row, col = divmod(index, cols)
            x = gutter + col * (cell_width + gutter)
            y = gutter + row * (cell_height + label_height + gutter)
            resized = image.resize(  # pyright: ignore[reportUnknownMemberType]
                (cell_width, cell_height), Image.Resampling.LANCZOS
            )
            canvas.paste(resized, (x, y))
            number = offset + index + 1
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
