import io

import pytest
from PIL import Image

import office_mcp.domain.preview as preview_module
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
    middle = len(cursor) // 2
    tampered = cursor[:middle] + ("A" if cursor[middle] != "A" else "B") + cursor[middle + 1 :]
    with pytest.raises(OfficeError):
        codec.decode(tampered)


def test_contact_sheet_layout_and_splitting() -> None:
    assert [auto_columns(n) for n in (2, 5, 10, 25)] == [2, 3, 4, 5]
    images = [png() for _ in range(80)]
    ids = [f"sld_{index:08d}" for index in range(80)]
    sheets = contact_sheets(
        images,
        ids,
        [f"Slide {index}" for index in range(80)],
        list(range(1, 81)),
        PreviewLabels.NUMBER_AND_NAME,
        PreviewQuality.STANDARD,
        None,
    )
    assert [len(item.slide_ids) for item in sheets] == [30, 30, 20]
    assert [item.slide_ids for item in sheets] == [ids[:30], ids[30:60], ids[60:]]
    assert [(item.width, item.height) for item in sheets] == [
        (2108, 1668),
        (2108, 1668),
        (1690, 1393),
    ]
    assert all(item.png.startswith(b"\x89PNG") for item in sheets)

    high = contact_sheets(
        images[:2],
        ids[:2],
        ["One", "Two"],
        [1, 2],
        PreviewLabels.NONE,
        PreviewQuality.HIGH,
        2,
    )[0]
    assert (high.width, high.height) == (1334, 396)


def test_contact_sheet_preserves_mixed_slide_aspect_ratios() -> None:
    sheet = contact_sheets(
        [sized_png((160, 90), "red"), sized_png((90, 160), "blue")],
        ["sld_00000001", "sld_00000002"],
        ["Wide", "Tall"],
        [1, 2],
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


def test_contact_sheet_labels_use_actual_deck_ordinals(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    labels: list[str] = []

    class Recorder:
        def text(self, _position: object, label: str, **_kwargs: object) -> None:
            labels.append(label)

    def recording_draw(_image: Image.Image) -> Recorder:
        return Recorder()

    monkeypatch.setattr(preview_module.ImageDraw, "Draw", recording_draw)
    contact_sheets(
        [png(), png()],
        ["sld_00000010", "sld_00000012"],
        ["Ten", "Twelve"],
        [10, 12],
        PreviewLabels.NUMBER,
        PreviewQuality.STANDARD,
        2,
    )
    assert labels == ["10", "12"]
