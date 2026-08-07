import base64
import io
from typing import Any

from mcp.server import MCPServer
from PIL import Image

from office_mcp.app import OfficeRuntime
from office_mcp.inputs.pptx import validate_pptx
from office_mcp.models.presentation import (
    NewSlide,
    PresentationCreateArgs,
    PresentationExportArgs,
    PresentationOpenArgs,
    PresentationSource,
)
from office_mcp.models.preview import PresentationPreviewArgs, PreviewSlides
from office_mcp.models.validation import PresentationValidateArgs, ValidationDetail
from office_mcp.storage.protocols import LOCAL_SCOPE


async def test_real_domoxml_preview_validation_export_and_import(
    office: tuple[MCPServer[Any], OfficeRuntime],
) -> None:
    _, runtime = office
    created = await runtime.service.create(
        LOCAL_SCOPE,
        PresentationCreateArgs(
            name="Rendered",
            slides=[
                NewSlide(
                    name="Cover",
                    html=(
                        '<section style="width:100%;height:100%;background:#fff;padding:64px">'
                        '<h1 data-office-name="title" style="font-size:42px;color:#111">'
                        "Real render</h1></section>"
                    ),
                )
            ],
        ),
    )
    images, preview = await runtime.service.preview(
        LOCAL_SCOPE,
        PresentationPreviewArgs(
            presentation_id=created.presentation_id,
            selection=PreviewSlides(slide_ids=[created.slides[0].slide_id]),
        ),
    )
    assert preview.images[0].slide_ids == [created.slides[0].slide_id]
    image = Image.open(io.BytesIO(images[0]))
    assert image.width > image.height

    validation = await runtime.service.validate(
        LOCAL_SCOPE,
        PresentationValidateArgs(
            presentation_id=created.presentation_id, detail=ValidationDetail.FULL
        ),
    )
    assert validation.valid
    assert validation.coverage is not None

    exported = await runtime.service.export(
        LOCAL_SCOPE, PresentationExportArgs(presentation_id=created.presentation_id)
    )
    data = await runtime.output.read(LOCAL_SCOPE, exported.resource_uri)
    assert data is not None
    validate_pptx(data, runtime.config)
    assert exported.sha256 and exported.size_bytes == len(data)

    source = (
        "data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,"
        + base64.b64encode(data).decode()
    )
    imported = await runtime.service.open(
        LOCAL_SCOPE,
        PresentationOpenArgs(source=PresentationSource(uri=source, filename_hint="roundtrip.pptx")),
    )
    untouched = await runtime.service.export(
        LOCAL_SCOPE, PresentationExportArgs(presentation_id=imported.presentation_id)
    )
    untouched_bytes = await runtime.output.read(LOCAL_SCOPE, untouched.resource_uri)
    assert untouched_bytes == data
