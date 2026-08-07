"""Complete typed MCP tool registry generated from the authoritative Pydantic contracts."""

import base64
import inspect
import json
import logging
import uuid
from collections.abc import Awaitable, Callable, Mapping
from typing import Annotated, Any, cast

from mcp.server import MCPServer
from mcp.server.mcpserver.context import Context
from mcp_types import CallToolResult, Icon, ImageContent, ResourceLink, TextContent, ToolAnnotations
from pydantic import BaseModel, Field, ValidationError
from pydantic_core import PydanticUndefined

from office_mcp.domain.service import PresentationService
from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.icons import (
    ELEMENT_ICONS,
    EXPORT_ICONS,
    PRESENTATION_ICONS,
    PREVIEW_ICONS,
    SLIDE_ICONS,
    VALIDATE_ICONS,
)
from office_mcp.models.element import (
    ElementAddArgs,
    ElementAddResult,
    ElementDeleteArgs,
    ElementDeleteResult,
    ElementInspectArgs,
    ElementInspectResult,
    ElementMoveArgs,
    ElementMoveResult,
    ElementUpdateArgs,
    ElementUpdateResult,
)
from office_mcp.models.presentation import (
    MutationResult,
    PresentationCreateArgs,
    PresentationCreateResult,
    PresentationDeleteArgs,
    PresentationDeleteResult,
    PresentationExportArgs,
    PresentationExportResult,
    PresentationInspectArgs,
    PresentationInspectResult,
    PresentationOpenArgs,
    PresentationOpenResult,
    PresentationSearchArgs,
    PresentationSearchResult,
    PresentationUpdateArgs,
)
from office_mcp.models.preview import PresentationPreviewArgs, PresentationPreviewResult
from office_mcp.models.slide import (
    SlideAddArgs,
    SlideAddResult,
    SlideDeleteArgs,
    SlideDeleteResult,
    SlideDuplicateArgs,
    SlideDuplicateResult,
    SlideInspectArgs,
    SlideInspectResult,
    SlideReorderArgs,
    SlideReorderResult,
    SlideUpdateArgs,
)
from office_mcp.models.validation import PresentationValidateArgs, PresentationValidationResult
from office_mcp.storage.protocols import RequestScopeProvider, bind_request_scope

logger = logging.getLogger(__name__)


async def _notifications(ctx: Context, name: str, args: BaseModel, result: Any) -> None:
    presentation = getattr(args, "presentation_id", None) or getattr(
        result, "presentation_id", None
    )
    if name in {"presentation_create", "presentation_open", "presentation_delete"}:
        await ctx.notify_resources_changed()
    if not presentation or name in {
        "presentation_search",
        "presentation_inspect",
        "presentation_validate",
        "presentation_preview",
        "presentation_export",
    }:
        return
    base = f"office://presentations/{presentation}"
    for uri in (base, f"{base}/outline", f"{base}/validation", f"{base}/preview"):
        await ctx.notify_resource_updated(uri)
    slide_ids: list[str] = []
    direct_slide = getattr(args, "slide_id", None)
    if direct_slide:
        slide_ids.append(str(direct_slide))
    slide_ids.extend(str(item) for item in getattr(args, "slide_ids", []) or [])
    if name == "slide_add":
        slide_ids.extend(str(item.slide_id) for item in result.added)
    elif name == "slide_duplicate":
        slide_ids.append(str(result.slide.slide_id))
    elif name == "slide_reorder":
        slide_ids.extend(str(item.slide_id) for item in result.slides)
    for slide in dict.fromkeys(slide_ids):
        slide_base = f"{base}/slides/{slide}"
        for uri in (slide_base, f"{slide_base}/source", f"{slide_base}/preview"):
            await ctx.notify_resource_updated(uri)
    element_ids = cast(
        list[str],
        getattr(result, "updated_element_ids", None)
        or getattr(result, "moved_element_ids", None)
        or getattr(result, "deleted_element_ids", None)
        or [],
    )
    if name == "element_add":
        element_ids.extend(str(item.element_id) for item in result.roots)
    if direct_slide:
        for element_id in element_ids:
            await ctx.notify_resource_updated(f"{base}/slides/{direct_slide}/elements/{element_id}")


def _model_signature(model: type[BaseModel], return_annotation: Any) -> inspect.Signature:
    parameters: list[inspect.Parameter] = []
    for name, field in model.model_fields.items():
        annotation = field.rebuild_annotation()
        if field.discriminator or field.description:
            annotation = Annotated[
                annotation,
                Field(discriminator=field.discriminator, description=field.description),
            ]
        if field.is_required():
            default = inspect.Parameter.empty
        elif field.default_factory is not None:
            default = field.get_default(call_default_factory=True, validated_data={})
        elif field.default is not PydanticUndefined:
            default = field.default
        else:
            default = None
        parameters.append(
            inspect.Parameter(
                name, inspect.Parameter.KEYWORD_ONLY, default=default, annotation=annotation
            )
        )
    parameters.append(inspect.Parameter("ctx", inspect.Parameter.KEYWORD_ONLY, annotation=Context))
    return inspect.Signature(parameters=parameters, return_annotation=return_annotation)


def register_tools(
    mcp: MCPServer[Any], service: PresentationService, scopes: RequestScopeProvider
) -> None:
    specs: list[
        tuple[
            str,
            str,
            str,
            type[BaseModel],
            Any,
            Callable[..., Awaitable[Any]],
            ToolAnnotations,
            list[Icon],
        ]
    ] = [
        (
            "presentation_create",
            "Create presentation",
            "Create a new editable PowerPoint presentation from semantic inline-styled HTML.",
            PresentationCreateArgs,
            PresentationCreateResult,
            service.create,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=False,
                idempotent_hint=False,
                open_world_hint=False,
            ),
            PRESENTATION_ICONS,
        ),
        (
            "presentation_open",
            "Open presentation",
            "Import a PPTX source into an editable workspace while preserving and reporting "
            "unsupported constructs.",
            PresentationOpenArgs,
            PresentationOpenResult,
            service.open,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=False,
                idempotent_hint=False,
                open_world_hint=service.config.allow_https_input,
            ),
            PRESENTATION_ICONS,
        ),
        (
            "presentation_search",
            "Search presentations",
            "Search persistent presentations semantically by metadata and visible slide text.",
            PresentationSearchArgs,
            PresentationSearchResult,
            service.search,
            ToolAnnotations(read_only_hint=True, open_world_hint=False),
            PRESENTATION_ICONS,
        ),
        (
            "presentation_inspect",
            "Inspect presentation",
            "Inspect presentation metadata and outline without loading slide HTML. "
            "Use this first for an existing deck.",
            PresentationInspectArgs,
            PresentationInspectResult,
            service.inspect,
            ToolAnnotations(read_only_hint=True, open_world_hint=False),
            PRESENTATION_ICONS,
        ),
        (
            "presentation_update",
            "Update presentation",
            "Update presentation metadata, size, or theme as one optimistic revision.",
            PresentationUpdateArgs,
            MutationResult,
            service.update,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=False,
                idempotent_hint=False,
                open_world_hint=False,
            ),
            PRESENTATION_ICONS,
        ),
        (
            "presentation_validate",
            "Validate presentation",
            "Validate domOXML representation, editability, source-retention coverage, "
            "warnings, and failures.",
            PresentationValidateArgs,
            PresentationValidationResult,
            service.validate,
            ToolAnnotations(read_only_hint=True, open_world_hint=False),
            VALIDATE_ICONS,
        ),
        (
            "presentation_preview",
            "Preview presentation",
            "Render selected slides. One slide returns detail; multiple slides return "
            "bounded contact sheets.",
            PresentationPreviewArgs,
            Annotated[CallToolResult, PresentationPreviewResult],
            service.preview,
            ToolAnnotations(read_only_hint=True, open_world_hint=False),
            PREVIEW_ICONS,
        ),
        (
            "presentation_export",
            "Export presentation",
            "Materialise an immutable PPTX for a specific revision and return its resource link.",
            PresentationExportArgs,
            Annotated[CallToolResult, PresentationExportResult],
            service.export,
            ToolAnnotations(read_only_hint=True, open_world_hint=False),
            EXPORT_ICONS,
        ),
        (
            "presentation_delete",
            "Delete presentation",
            "Permanently delete a standalone Office presentation and all stored revisions.",
            PresentationDeleteArgs,
            PresentationDeleteResult,
            service.delete,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=True,
                idempotent_hint=True,
                open_world_hint=False,
            ),
            PRESENTATION_ICONS,
        ),
        (
            "slide_add",
            "Add slides",
            "Add one or more named inline-HTML slides in one transaction and revision.",
            SlideAddArgs,
            SlideAddResult,
            service.slide_add,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=False,
                idempotent_hint=False,
                open_world_hint=False,
            ),
            SLIDE_ICONS,
        ),
        (
            "slide_inspect",
            "Inspect slide",
            "Inspect one slide. Prefer structure; request source only for exact styles "
            "or redesign.",
            SlideInspectArgs,
            SlideInspectResult,
            service.slide_inspect,
            ToolAnnotations(read_only_hint=True, open_world_hint=False),
            SLIDE_ICONS,
        ),
        (
            "slide_update",
            "Update slide",
            "Update slide metadata or replace full HTML for a genuine redesign; "
            "prefer element_update for small edits.",
            SlideUpdateArgs,
            MutationResult,
            service.slide_update,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=False,
                idempotent_hint=False,
                open_world_hint=False,
            ),
            SLIDE_ICONS,
        ),
        (
            "slide_duplicate",
            "Duplicate slide",
            "Duplicate a slide with fresh slide and element IDs for layout reuse.",
            SlideDuplicateArgs,
            SlideDuplicateResult,
            service.slide_duplicate,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=False,
                idempotent_hint=False,
                open_world_hint=False,
            ),
            SLIDE_ICONS,
        ),
        (
            "slide_delete",
            "Delete slides",
            "Delete one or more slides atomically.",
            SlideDeleteArgs,
            SlideDeleteResult,
            service.slide_delete,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=True,
                idempotent_hint=True,
                open_world_hint=False,
            ),
            SLIDE_ICONS,
        ),
        (
            "slide_reorder",
            "Reorder slides",
            "Set the complete declarative slide order using every current stable "
            "slide ID exactly once.",
            SlideReorderArgs,
            SlideReorderResult,
            service.slide_reorder,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=False,
                idempotent_hint=True,
                open_world_hint=False,
            ),
            SLIDE_ICONS,
        ),
        (
            "element_inspect",
            "Inspect element",
            "Inspect one stable element subtree, attributes, and inline styles.",
            ElementInspectArgs,
            ElementInspectResult,
            service.element_inspect,
            ToolAnnotations(read_only_hint=True, open_world_hint=False),
            ELEMENT_ICONS,
        ),
        (
            "element_add",
            "Add element",
            "Insert a safe inline-styled HTML subtree relative to a stable element.",
            ElementAddArgs,
            ElementAddResult,
            service.element_add,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=False,
                idempotent_hint=False,
                open_world_hint=False,
            ),
            ELEMENT_ICONS,
        ),
        (
            "element_update",
            "Update elements",
            "Atomically update one or more elements. Use for normal text, style, "
            "attribute, or subtree edits.",
            ElementUpdateArgs,
            ElementUpdateResult,
            service.element_update,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=False,
                idempotent_hint=False,
                open_world_hint=False,
            ),
            ELEMENT_ICONS,
        ),
        (
            "element_move",
            "Move elements",
            "Move elements in DOM hierarchy/order; pixel geometry remains inline CSS.",
            ElementMoveArgs,
            ElementMoveResult,
            service.element_move,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=False,
                idempotent_hint=False,
                open_world_hint=False,
            ),
            ELEMENT_ICONS,
        ),
        (
            "element_delete",
            "Delete elements",
            "Delete one or more stable slide elements atomically.",
            ElementDeleteArgs,
            ElementDeleteResult,
            service.element_delete,
            ToolAnnotations(
                read_only_hint=False,
                destructive_hint=True,
                idempotent_hint=True,
                open_world_hint=False,
            ),
            ELEMENT_ICONS,
        ),
    ]

    def make_handler(
        name: str,
        title: str,
        description: str,
        args_model: type[BaseModel],
        result_annotation: Any,
        method: Callable[..., Awaitable[Any]],
    ):
        async def handler(**kwargs: Any) -> Any:
            ctx: Context = kwargs.pop("ctx")
            raw_params: Mapping[str, Any] = ctx.request_context.params or {}
            raw_arguments = cast(dict[str, Any], raw_params.get("arguments", {}))
            # MCP arguments arrive as JSON. Pydantic's strict Python mode
            # rejects the string representation of enums, while strict JSON
            # mode accepts wire values and still prevents scalar coercion.
            try:
                args = args_model.model_validate_json(json.dumps(raw_arguments))
            except ValidationError as exc:
                first = exc.errors(include_url=False)[0]
                location = ".".join(str(item) for item in first["loc"]) or "arguments"
                raise OfficeError(
                    ErrorCode.INVALID_PRESENTATION_SOURCE,
                    f"invalid {name} argument {location}: {first['msg']}",
                ) from exc
            try:
                scope = await scopes.current()
                bind_request_scope(scope)
                expensive = name in {
                    "presentation_open",
                    "presentation_validate",
                    "presentation_preview",
                    "presentation_export",
                }
                if expensive:
                    label = getattr(getattr(args, "activity", None), "label", None) or title
                    await ctx.report_progress(0, 1, label)
                value = await method(scope, args)
                if name == "presentation_preview":
                    images, metadata = value
                    result = CallToolResult(
                        content=[
                            ImageContent(
                                data=base64.b64encode(image).decode(), mime_type="image/png"
                            )
                            for image in images
                        ],
                        # Keep enum instances until the SDK has validated the
                        # declared structured output; transport serialization
                        # converts them to their JSON string values afterward.
                        structured_content=metadata.model_dump(),
                    )
                elif name == "presentation_export":
                    metadata = value
                    result = CallToolResult(
                        content=[
                            TextContent(
                                text=f"Exported {metadata.filename} ({metadata.size_bytes} bytes)."
                            ),
                            ResourceLink(
                                name=metadata.filename,
                                uri=metadata.resource_uri,
                                description="Immutable exported PowerPoint revision",
                                mime_type=metadata.mime_type,
                                size=metadata.size_bytes,
                            ),
                        ],
                        structured_content=metadata.model_dump(),
                    )
                else:
                    result = value
                await _notifications(
                    ctx, name, args, value[1] if name == "presentation_preview" else value
                )
                if expensive:
                    await ctx.report_progress(1, 1, f"{title} complete")
                return result
            except OfficeError:
                raise
            except Exception as exc:
                trace = uuid.uuid4().hex
                logger.exception("Office tool %s failed trace=%s", name, trace)
                raise OfficeError(
                    ErrorCode.INTERNAL_ERROR, f"operation failed; trace ID {trace}"
                ) from exc

        handler.__name__ = name
        handler.__qualname__ = name
        handler.__doc__ = description
        handler.__annotations__ = {"ctx": Context, "return": result_annotation}
        handler.__signature__ = _model_signature(args_model, result_annotation)  # type: ignore[attr-defined]
        return handler

    for (
        name,
        title,
        description,
        args_model,
        result_annotation,
        method,
        annotations,
        icons,
    ) in specs:
        handler = make_handler(name, title, description, args_model, result_annotation, method)
        mcp.tool(
            name=name,
            title=title,
            description=description,
            annotations=annotations,
            icons=icons,
        )(handler)
        # The SDK builds a transient argument model from the flat function
        # signature.  Its generated schema does not expose a config hook, so
        # make the already-enforced extra-field policy explicit to clients.
        tool_manager = cast(Any, mcp)._tool_manager
        tool_manager._tools[name].parameters["additionalProperties"] = False
