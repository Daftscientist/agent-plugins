"""Office resource tree and true paginated presentation catalogue."""

import io
import json
from typing import Any, Literal

from mcp.server import MCPServer
from mcp.server.context import ServerRequestContext
from mcp.server.mcpserver.context import Context
from mcp_types import ListResourcesResult, PaginatedRequestParams, Resource
from PIL import Image

from office_mcp.constants import OFFICE_VERSION, PPTX_MIME, RESOURCE_PAGE_SIZE
from office_mcp.domain.cursors import CursorCodec
from office_mcp.domain.service import PresentationService
from office_mcp.icons import (
    ELEMENT_ICONS,
    OFFICE_ICONS,
    PRESENTATION_ICONS,
    PREVIEW_ICONS,
    SLIDE_ICONS,
    VALIDATE_ICONS,
)
from office_mcp.models.element import ElementById, ElementInspectArgs
from office_mcp.models.presentation import (
    PresentationExportArgs,
    PresentationInspectArgs,
    PresentationInspectDetail,
)
from office_mcp.models.preview import (
    PresentationPreviewArgs,
    PreviewAll,
    PreviewLabels,
    PreviewQuality,
)
from office_mcp.models.slide import SlideInspectArgs, SlideInspectDetail
from office_mcp.models.validation import PresentationValidateArgs
from office_mcp.storage.protocols import PresentationStore, RequestScopeProvider


def _json(value: Any) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def combine_contact_sheets(images: list[bytes]) -> bytes:
    """Expose every sheet through the singular canonical preview resource."""
    if not images:
        return b""
    if len(images) == 1:
        return images[0]
    decoded = [Image.open(io.BytesIO(data)).convert("RGB") for data in images]
    gutter = 18
    width = max(image.width for image in decoded)
    height = sum(image.height for image in decoded) + gutter * (len(decoded) - 1)
    combined = Image.new("RGB", (width, height), "#e5e7eb")
    y = 0
    for image in decoded:
        combined.paste(image, ((width - image.width) // 2, y))
        y += image.height + gutter
    output = io.BytesIO()
    combined.save(output, format="PNG", optimize=True)
    return output.getvalue()


def register_resources(
    mcp: MCPServer[Any],
    service: PresentationService,
    store: PresentationStore,
    scopes: RequestScopeProvider,
    cursor: CursorCodec,
) -> None:
    @mcp.resource(
        "office://capabilities",
        name="Office capabilities",
        title="Office capabilities",
        description="Machine-readable current Office/domOXML capabilities.",
        mime_type="application/json",
        icons=OFFICE_ICONS,
    )
    def capabilities() -> str:
        return _json(
            {
                "office_version": OFFICE_VERSION,
                "presentation": {
                    "input": ["pptx", "html"],
                    "output": ["pptx", "png", "html"],
                    "authoring": {"html": True, "inline_css_only": True, "javascript": False},
                    "remote_render_assets": False,
                    "slide_sizes": ["16:9", "4:3", "16:10", "custom"],
                    "pptx_uniform_size_required": True,
                    "transitions": [
                        "none",
                        "fade",
                        "push",
                        "wipe",
                        "cover",
                        "split",
                        "cut",
                        "zoom",
                        "dissolve",
                        "morph",
                    ],
                    "unsupported_authored_features": [
                        "charts",
                        "animations",
                        "speaker_notes",
                        "audio",
                        "video",
                        "master_layouts",
                    ],
                },
            }
        )

    @mcp.resource(
        "office://presentations/{presentation_id}",
        name="Presentation",
        title="Presentation metadata",
        mime_type="application/json",
        icons=PRESENTATION_ICONS,
    )
    async def presentation_root(presentation_id: str, ctx: Context) -> str:
        scope = await scopes.current()
        return _json(
            await service.inspect(
                scope,
                PresentationInspectArgs(
                    presentation_id=presentation_id, detail=PresentationInspectDetail.SUMMARY
                ),
            )
        )

    @mcp.resource(
        "office://presentations/{presentation_id}/outline",
        name="Presentation outline",
        title="Presentation outline",
        mime_type="application/json",
        icons=PRESENTATION_ICONS,
    )
    async def outline(presentation_id: str, ctx: Context) -> str:
        scope = await scopes.current()
        return _json(
            await service.inspect(scope, PresentationInspectArgs(presentation_id=presentation_id))
        )

    @mcp.resource(
        "office://presentations/{presentation_id}/validation",
        name="Presentation validation",
        title="Presentation validation",
        mime_type="application/json",
        icons=VALIDATE_ICONS,
    )
    async def validation(presentation_id: str, ctx: Context) -> str:
        scope = await scopes.current()
        return _json(
            await service.validate(scope, PresentationValidateArgs(presentation_id=presentation_id))
        )

    @mcp.resource(
        "office://presentations/{presentation_id}/preview{?quality,labels,columns}",
        name="Presentation preview",
        title="Presentation preview",
        mime_type="image/png",
        icons=PREVIEW_ICONS,
    )
    async def presentation_preview(
        presentation_id: str,
        ctx: Context,
        quality: str = "standard",
        labels: str = "number_and_name",
        columns: Literal[2, 3, 4, 5] | None = None,
    ) -> bytes:
        scope = await scopes.current()
        images, _ = await service.preview(
            scope,
            PresentationPreviewArgs(
                presentation_id=presentation_id,
                selection=PreviewAll(),
                quality=PreviewQuality(quality),
                labels=PreviewLabels(labels),
                columns=columns,
            ),
        )
        return combine_contact_sheets(images)

    @mcp.resource(
        "office://presentations/{presentation_id}/revisions/{revision_id}",
        name="Revision metadata",
        title="Presentation revision",
        mime_type="application/json",
        icons=PRESENTATION_ICONS,
    )
    async def revision_metadata(presentation_id: str, revision_id: str, ctx: Context) -> str:
        scope = await scopes.current()
        snapshot = await store.get(scope, presentation_id, revision_id)
        return _json(
            {
                "presentation_id": snapshot.presentation_id,
                "revision": snapshot.revision_id,
                "parent_revision": snapshot.parent_revision_id,
                "created_at": snapshot.updated_at.isoformat(),
                "slide_count": len(snapshot.slides),
            }
        )

    @mcp.resource(
        "office://presentations/{presentation_id}/revisions/{revision_id}/file",
        name="PowerPoint file",
        title="PowerPoint revision file",
        mime_type=PPTX_MIME,
        icons=PRESENTATION_ICONS,
    )
    async def revision_file(presentation_id: str, revision_id: str, ctx: Context) -> bytes:
        scope = await scopes.current()
        metadata = await service.export(
            scope, PresentationExportArgs(presentation_id=presentation_id, revision=revision_id)
        )
        data = await service.output.read(scope, metadata.resource_uri)
        assert data is not None
        return data

    @mcp.resource(
        "office://presentations/{presentation_id}/slides/{slide_id}",
        name="Slide",
        title="Slide structure",
        mime_type="application/json",
        icons=SLIDE_ICONS,
    )
    async def slide_root(presentation_id: str, slide_id: str, ctx: Context) -> str:
        scope = await scopes.current()
        return _json(
            await service.slide_inspect(
                scope, SlideInspectArgs(presentation_id=presentation_id, slide_id=slide_id)
            )
        )

    @mcp.resource(
        "office://presentations/{presentation_id}/slides/{slide_id}/source",
        name="Slide source",
        title="Slide source",
        mime_type="text/html",
        icons=SLIDE_ICONS,
    )
    async def slide_source(presentation_id: str, slide_id: str, ctx: Context) -> str:
        scope = await scopes.current()
        result = await service.slide_inspect(
            scope,
            SlideInspectArgs(
                presentation_id=presentation_id, slide_id=slide_id, detail=SlideInspectDetail.SOURCE
            ),
        )
        return result.html or ""

    @mcp.resource(
        "office://presentations/{presentation_id}/slides/{slide_id}/preview{?quality}",
        name="Slide preview",
        title="Slide preview",
        mime_type="image/png",
        icons=PREVIEW_ICONS,
    )
    async def slide_preview(
        presentation_id: str, slide_id: str, ctx: Context, quality: str = "standard"
    ) -> bytes:
        scope = await scopes.current()
        from office_mcp.models.preview import PreviewSlides

        images, _ = await service.preview(
            scope,
            PresentationPreviewArgs(
                presentation_id=presentation_id,
                selection=PreviewSlides(slide_ids=[slide_id]),
                quality=PreviewQuality(quality),
            ),
        )
        return images[0]

    @mcp.resource(
        "office://presentations/{presentation_id}/slides/{slide_id}/elements/{element_id}",
        name="Element",
        title="Slide element",
        mime_type="application/json",
        icons=ELEMENT_ICONS,
    )
    async def element(presentation_id: str, slide_id: str, element_id: str, ctx: Context) -> str:
        scope = await scopes.current()
        return _json(
            await service.element_inspect(
                scope,
                ElementInspectArgs(
                    presentation_id=presentation_id,
                    slide_id=slide_id,
                    element=ElementById(element_id=element_id),
                ),
            )
        )

    async def paginated_resources(
        ctx: ServerRequestContext, params: PaginatedRequestParams | None
    ) -> ListResourcesResult:
        scope = await scopes.current()
        snapshots = await store.list_current(scope)
        after_updated: str | None = None
        after_id: str | None = None
        if params and params.cursor:
            payload = cursor.decode(params.cursor)
            if payload.get("scope") != scope.key or payload.get("kind") != "resources":
                from office_mcp.errors import ErrorCode, OfficeError

                raise OfficeError(ErrorCode.ACCESS_DENIED, "resource cursor is invalid")
            after_updated = str(payload["after_updated"])
            after_id = str(payload["after_id"])
        if after_updated is not None and after_id is not None:
            snapshots = [
                snapshot
                for snapshot in snapshots
                if snapshot.updated_at.isoformat() < after_updated
                or (
                    snapshot.updated_at.isoformat() == after_updated
                    and snapshot.presentation_id > after_id
                )
            ]
        include_capabilities = after_updated is None
        capacity = RESOURCE_PAGE_SIZE - 1 if include_capabilities else RESOURCE_PAGE_SIZE
        page = snapshots[:capacity]
        resources = (
            [
                Resource(
                    name="Office capabilities",
                    title="Office capabilities",
                    uri="office://capabilities",
                    description="Machine-readable Office/domOXML capabilities and limits.",
                    mime_type="application/json",
                    icons=OFFICE_ICONS,
                )
            ]
            if include_capabilities
            else []
        ) + [
            Resource(
                name=snapshot.name,
                title=snapshot.name,
                uri=f"office://presentations/{snapshot.presentation_id}",
                description=snapshot.description or f"{len(snapshot.slides)}-slide presentation",
                mime_type="application/json",
                icons=PRESENTATION_ICONS,
            )
            for snapshot in page
        ]
        next_cursor = None
        if len(snapshots) > capacity:
            last = page[-1]
            next_cursor = cursor.encode(
                {
                    "scope": scope.key,
                    "kind": "resources",
                    "after_updated": last.updated_at.isoformat(),
                    "after_id": last.presentation_id,
                }
            )
        return ListResourcesResult(resources=resources, next_cursor=next_cursor)

    mcp._lowlevel_server.add_request_handler(  # pyright: ignore[reportPrivateUsage]
        "resources/list", PaginatedRequestParams, paginated_resources
    )
