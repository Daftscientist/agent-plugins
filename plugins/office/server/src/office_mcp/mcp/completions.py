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
            values = [
                f"{item.presentation_id} — {item.name}"
                for item in snapshots
                if partial in item.presentation_id.casefold() or partial in item.name.casefold()
            ][:30]
            return Completion(values=values, total=len(values), has_more=False)
        resolved = context.arguments if context else {}
        presentation = resolved.get("presentation_id") if resolved else None
        if presentation:
            presentation = presentation.split(" — ", 1)[0]
            try:
                snapshot = await store.get(scope, presentation)
            except Exception:
                return Completion(values=[], total=0, has_more=False)
            if argument.name == "slide_id":
                values = [
                    f"{slide.slide_id} — {slide.name}"
                    for slide in snapshot.slides
                    if partial in slide.slide_id.casefold() or partial in slide.name.casefold()
                ][:30]
                return Completion(values=values, total=len(values), has_more=False)
            slide_value = resolved.get("slide_id") if resolved else None
            if argument.name == "element_id" and slide_value:
                slide_value = slide_value.split(" — ", 1)[0]
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
                            values.append(display)
                    return Completion(
                        values=values[:30], total=min(len(values), 30), has_more=len(values) > 30
                    )
        return Completion(values=[], total=0, has_more=False)
