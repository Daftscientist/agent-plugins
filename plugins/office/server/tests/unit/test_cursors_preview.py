import io

import pytest
from PIL import Image

from office_mcp.domain.cursors import CursorCodec
from office_mcp.domain.preview import auto_columns, contact_sheets
from office_mcp.errors import OfficeError
from office_mcp.models.preview import PreviewLabels, PreviewQuality


def png(color: str = "red") -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (160, 90), color).save(buffer, "PNG")
    return buffer.getvalue()


def sized_png(size: tuple[int, int], color: str) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, "PNG")
    return buffer.getvalue()


def test_cursor_integrity_and_expiry_shape() -> None:
    codec = CursorCodec(b"secret" * 8)
    cursor = codec.encode({"scope": "a", "offset": 20})
    assert codec.decode(cursor)["offset"] == 20
    with pytest.raises(OfficeError):
        codec.decode(cursor[:-1] + ("A" if cursor[-1] != "A" else "B"))


def test_contact_sheet_layout_and_splitting() -> None:
    assert [auto_columns(n) for n in (2, 5, 10, 25)] == [2, 3, 4, 5]
    images = [png() for _ in range(80)]
    ids = [f"sld_{index:08d}" for index in range(80)]
    sheets = contact_sheets(
        images,
        ids,
        [f"Slide {index}" for index in range(80)],
        PreviewLabels.NUMBER_AND_NAME,
        PreviewQuality.STANDARD,
        None,
    )
    assert [len(item.slide_ids) for item in sheets] == [30, 30, 20]
    assert all(item.png.startswith(b"\x89PNG") for item in sheets)


def test_contact_sheet_preserves_mixed_slide_aspect_ratios() -> None:
    sheet = contact_sheets(
        [sized_png((160, 90), "red"), sized_png((90, 160), "blue")],
        ["sld_00000001", "sld_00000002"],
        ["Wide", "Tall"],
        PreviewLabels.NONE,
        PreviewQuality.STANDARD,
        2,
    )[0]
    image = Image.open(io.BytesIO(sheet.png)).convert("RGB")

    def bounds(color: tuple[int, int, int]) -> tuple[int, int]:
        points = [
            (x, y)
            for y in range(image.height)
            for x in range(image.width)
            if image.getpixel((x, y)) == color
        ]
        return max(x for x, _ in points) - min(x for x, _ in points) + 1, max(
            y for _, y in points
        ) - min(y for _, y in points) + 1

    assert bounds((255, 0, 0)) == (400, 225)
    assert bounds((0, 0, 255)) == (225, 400)
