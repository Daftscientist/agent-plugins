import io
import zipfile
from typing import Any, cast

import pytest
from mcp.server import MCPServer
from PIL import Image

from office_mcp.app import OfficeRuntime
from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.inputs import validate_pptx
from office_mcp.models.common import (
    CustomSlideSize,
    PresetSlideSize,
    SlideSizePreset,
    SlideTransition,
)
from office_mcp.models.presentation import NewSlide, PresentationCreateArgs, PresentationExportArgs
from office_mcp.models.validation import PresentationValidateArgs, ValidationDetail
from office_mcp.storage.protocols import LOCAL_SCOPE

PNG_1PX = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
)

RGB = tuple[int, int, int]


def pixel(image: Image.Image, position: tuple[int, int]) -> RGB:
    return cast(RGB, image.getpixel(position))


def color_counts(image: Image.Image, size: tuple[int, int]) -> list[tuple[int, RGB]]:
    thumbnail = image.resize(size)  # pyright: ignore[reportUnknownMemberType]
    return cast(list[tuple[int, RGB]], thumbnail.getcolors(maxcolors=size[0] * size[1]) or [])


@pytest.mark.integration
async def test_visual_feature_size_and_transition_matrix(
    office: tuple[MCPServer[Any], OfficeRuntime],
) -> None:
    _, runtime = office
    created = await runtime.service.create(
        LOCAL_SCOPE,
        PresentationCreateArgs(
            name="Visual feature matrix",
            slides=[
                NewSlide(
                    name="Typography and effects",
                    transition=SlideTransition.FADE,
                    html=(
                        '<section style="width:100%;height:100%;padding:64px;'
                        'background:linear-gradient(135deg,#ffffff,#dbeafe)">'
                        '<h1 style="font-size:48px;line-height:1.1">Two-line<br>headline</h1>'
                        '<div style="border:3px solid #2b579a;box-shadow:0 12px 24px '
                        'rgba(0,0,0,.25);padding:24px">Effects</div></section>'
                    ),
                ),
                NewSlide(
                    name="Images and SVG",
                    transition=SlideTransition.WIPE,
                    size=PresetSlideSize(preset=SlideSizePreset.STANDARD_4_3),
                    html=(
                        '<section style="width:100%;height:100%;padding:48px;background:#fff">'
                        f'<img src="data:image/png;base64,{PNG_1PX}" '
                        'style="width:120px;height:120px">'
                        '<svg viewBox="0 0 100 100" style="width:200px;height:200px">'
                        '<circle cx="50" cy="50" r="45" fill="#d24726"></circle>'
                        "</svg></section>"
                    ),
                ),
                NewSlide(
                    name="Table and groups",
                    transition=SlideTransition.PUSH,
                    size=PresetSlideSize(preset=SlideSizePreset.WIDE_16_10),
                    html=(
                        '<main style="width:100%;height:100%;padding:48px">'
                        '<div style="display:flex;gap:24px"><div style="flex:1">'
                        '<table style="border-collapse:collapse;width:100%">'
                        '<tr><th style="border:1px solid #111">Metric</th>'
                        '<th style="border:1px solid #111">Value</th></tr>'
                        '<tr><td style="border:1px solid #111">ARR</td>'
                        '<td style="border:1px solid #111">$2M</td></tr>'
                        '</table></div><div style="flex:1">Nested group</div></div></main>'
                    ),
                ),
                NewSlide(
                    name="Custom square",
                    transition=SlideTransition.CUT,
                    size=CustomSlideSize(width_in=8, height_in=8),
                    html='<section style="width:100%;height:100%;background:#107c10"></section>',
                ),
            ],
        ),
    )
    snapshot = await runtime.store.get(LOCAL_SCOPE, created.presentation_id)
    pngs = await runtime.service.adapter.preview_pngs(snapshot, {0, 1, 2, 3})
    rendered = [Image.open(io.BytesIO(image)).convert("RGB") for image in pngs]
    sizes = [image.size for image in rendered]
    assert sizes == [(2560, 1440), (1920, 1440), (1920, 1200), (1536, 1536)]

    # Visual goldens for the authored feature families. These assertions
    # intentionally inspect rendered pixels, not merely the input HTML.
    effects = rendered[0]
    assert pixel(effects, (20, 20)) != pixel(effects, (2540, 1420))  # gradient
    thumbnail_colors = color_counts(effects, (256, 144))
    assert len(thumbnail_colors) > 100  # gradient, antialiasing, text, border, shadow
    assert sum(count for count, color in thumbnail_colors if max(color) < 90) > 20
    assert (
        sum(
            1
            for y in range(100, 430)
            if sum(1 for x in range(100, 1200) if max(pixel(effects, (x, y))) < 100) > 20
        )
        > 60
    )  # two-line heading plus effect text
    assert any(
        pixel(effects, (x, y))[2] > pixel(effects, (x, y))[0] + 40
        for x in range(100, 1500, 10)
        for y in range(250, 800, 10)
    )  # blue border survives

    imagery = rendered[1]
    imagery_colors = color_counts(imagery, (192, 144))
    assert any(color[0] > 220 and color[1] < 50 and color[2] < 50 for _, color in imagery_colors)
    assert any(
        color[0] > 160 and 35 < color[1] < 120 and color[2] < 80 for _, color in imagery_colors
    )  # inline SVG circle

    table_image = rendered[2]
    assert (
        sum(
            1
            for y in range(70, 500)
            for x in range(70, 1200)
            if max(pixel(table_image, (x, y))) < 100
        )
        > 500
    )

    validation = await runtime.service.validate(
        LOCAL_SCOPE,
        PresentationValidateArgs(
            presentation_id=created.presentation_id, detail=ValidationDetail.FULL
        ),
    )
    assert not validation.valid
    assert (
        sum(warning.code == "MIXED_SLIDE_SIZE_UNSUPPORTED" for warning in validation.warnings) == 3
    )
    with pytest.raises(OfficeError) as error:
        await runtime.service.export(
            LOCAL_SCOPE, PresentationExportArgs(presentation_id=created.presentation_id)
        )
    assert error.value.code is ErrorCode.EXPORT_FAILED

    uniform = snapshot.model_copy(deep=True)
    for slide in uniform.slides:
        slide.size = None
    pptx, _ = await runtime.service.adapter.export_pptx(uniform)
    validate_pptx(pptx, runtime.config)
    with zipfile.ZipFile(io.BytesIO(pptx)) as package:
        slide_xml = b"".join(
            package.read(name)
            for name in package.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        )
    assert slide_xml.count(b"<p:transition") == 4
    assert b"<a:tbl" in slide_xml
    roundtrip = await runtime.service.adapter.import_pptx(pptx)
    assert [slide.transition for slide in roundtrip.slides] == [
        SlideTransition.FADE,
        SlideTransition.WIPE,
        SlideTransition.PUSH,
        SlideTransition.CUT,
    ]
