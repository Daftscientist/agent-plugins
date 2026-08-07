"""Scope-safe dependent prompt/resource argument completion."""

from mcp.server import MCPServer
from mcp_types import (
    Completion,
    CompletionArgument,
    CompletionContext,
    PromptReference,
    ResourceTemplateReference,
)

from office_mcp.domain.html import element_tags
from office_mcp.storage.protocols import PresentationStore, RequestScopeProvider


def register_completions(
    mcp: MCPServer, store: PresentationStore, scopes: RequestScopeProvider
) -> None:
    @mcp.completion()
    async def complete(
        ref: PromptReference | ResourceTemplateReference,
        argument: CompletionArgument,
        context: CompletionContext | None,
    ) -> Completion:
        scope = await scopes.current()
        partial = argument.value.casefold()
        snapshots = await store.list_current(scope)
        if argument.name == "presentation_id":
            matches = [
                item.presentation_id
                for item in snapshots
                if partial in item.presentation_id.casefold() or partial in item.name.casefold()
            ]
            return Completion(values=matches[:30], total=len(matches), has_more=len(matches) > 30)
        resolved = context.arguments if context else {}
        presentation = resolved.get("presentation_id") if resolved else None
        if presentation:
            try:
                snapshot = await store.get(scope, presentation)
            except Exception:
                return Completion(values=[], total=0, has_more=False)
            if argument.name == "slide_id":
                matches = [
                    slide.slide_id
                    for slide in snapshot.slides
                    if partial in slide.slide_id.casefold() or partial in slide.name.casefold()
                ]
                return Completion(
                    values=matches[:30], total=len(matches), has_more=len(matches) > 30
                )
            slide_value = resolved.get("slide_id") if resolved else None
            if argument.name == "element_id" and slide_value:
                slide = next(
                    (item for item in snapshot.slides if item.slide_id == slide_value), None
                )
                if slide:
                    values: list[str] = []
                    for tag in element_tags(slide.html):
                        identifier = str(tag["data-office-id"])
                        name = str(tag.get("data-office-name", tag.name))
                        text = tag.get_text(" ", strip=True)[:50]
                        display = f"{identifier} — {name} — {text}"
                        if partial in display.casefold():
                            values.append(identifier)
                    return Completion(
                        values=values[:30], total=len(values), has_more=len(values) > 30
                    )
        return Completion(values=[], total=0, has_more=False)
