import io
from typing import Any

import pytest
from mcp.server import MCPServer
from PIL import Image

from office_mcp.app import OfficeRuntime
from office_mcp.models.presentation import NewSlide, PresentationCreateArgs
from office_mcp.models.preview import PresentationPreviewArgs, PreviewSlides
from office_mcp.storage.protocols import LOCAL_SCOPE


@pytest.mark.integration
async def test_domoxml_color_block_golden(
    office: tuple[MCPServer[Any], OfficeRuntime],
) -> None:
    """Catch viewport, layout, colour, clipping, and unexpected render regressions."""
    _, runtime = office
    created = await runtime.service.create(
        LOCAL_SCOPE,
        PresentationCreateArgs(
            name="Golden",
            slides=[
                NewSlide(
                    name="Color blocks",
                    html=(
                        '<section style="position:relative;width:100%;height:100%;'
                        'background:#102030">'
                        '<div style="position:absolute;left:0;top:0;width:50%;height:100%;'
                        'background:#d24726"></div>'
                        '<div style="position:absolute;right:0;top:0;width:50%;height:100%;'
                        'background:#2b579a"></div></section>'
                    ),
                )
            ],
        ),
    )
    images, _ = await runtime.service.preview(
        LOCAL_SCOPE,
        PresentationPreviewArgs(
            presentation_id=created.presentation_id,
            selection=PreviewSlides(slide_ids=[created.slides[0].slide_id]),
        ),
    )
    image = Image.open(io.BytesIO(images[0])).convert("RGB")
    assert image.size == (2560, 1440)
    assert sorted(image.getcolors(maxcolors=4) or [], reverse=True) == [
        (1_843_200, (210, 71, 38)),
        (1_843_200, (43, 87, 154)),
    ]
