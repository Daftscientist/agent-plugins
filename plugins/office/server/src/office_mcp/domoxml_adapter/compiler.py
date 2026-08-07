"""The only module that translates Office domain state to/from domOXML."""

import asyncio
import base64
import io
import mimetypes
from dataclasses import dataclass

import tinycss2
from bs4 import BeautifulSoup, Tag
from domoxml import Presentation, Slide, pptx_to_html
from domoxml.types import (
    CustomSize,
    Fonts,
    OutputFormat,
    Palette,
    Theme,
    Transition,
)
from domoxml.types import (
    SlideSize as DomSlideSize,
)
from pptx import Presentation as PptxPresentation

from office_mcp.domain.html import parse_styles, sanitize_fragment, serialize_styles
from office_mcp.domain.state import PresentationSnapshot, StoredSlide
from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.models.common import CustomSlideSize, PresetSlideSize, SlideSize


@dataclass(frozen=True)
class ImportedPresentation:
    slides: list[StoredSlide]
    warnings: list[dict[str, object]]
    preservation: list[dict[str, object]]
    coverage: list[dict[str, object]]


def _size(size: SlideSize):
    if isinstance(size, PresetSlideSize):
        return DomSlideSize(size.preset.value)
    assert isinstance(size, CustomSlideSize)
    return CustomSize(width_in=size.width_in, height_in=size.height_in)


def _inline_css(html: str, css: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
    for rule in rules:
        if rule.type != "qualified-rule":
            continue
        selector = tinycss2.serialize(rule.prelude).strip()
        declarations = parse_styles(tinycss2.serialize(rule.content))
        try:
            matches = soup.select(selector)
        except Exception:
            continue
        for tag in matches:
            existing = parse_styles(str(tag.get("style", "")))
            declarations_for_tag = dict(declarations)
            declarations_for_tag.update(existing)
            tag["style"] = serialize_styles(declarations_for_tag)
    return str(soup)


class DomOXMLAdapter:
    def __init__(self, *, max_concurrency: int = 2, timeout_seconds: float = 120.0) -> None:
        self._render_slots = asyncio.Semaphore(max(1, max_concurrency))
        self._timeout_seconds = timeout_seconds

    def _presentation(self, snapshot: PresentationSnapshot) -> Presentation:
        palette = snapshot.theme.palette
        fonts = snapshot.theme.fonts
        deck = Presentation(
            size=_size(snapshot.size),
            theme=Theme(
                palette=Palette(
                    background=palette.background,
                    foreground=palette.foreground,
                    accent=palette.accent,
                    muted=palette.muted,
                ),
                fonts=Fonts(heading=fonts.heading, body=fonts.body),
            ),
        )
        for slide in snapshot.slides:
            deck.add(
                Slide(
                    html=slide.html,
                    transition=Transition(slide.transition.value) if slide.transition else None,
                    size=_size(slide.size) if slide.size else None,
                )
            )
        return deck

    async def render(
        self,
        snapshot: PresentationSnapshot,
        formats: set[OutputFormat],
        indices: set[int] | None = None,
    ):
        try:
            async with self._render_slots, asyncio.timeout(self._timeout_seconds):
                return await self._presentation(snapshot).arender(formats, indices=indices)
        except TimeoutError as exc:
            raise OfficeError(ErrorCode.RENDER_FAILED, "presentation rendering timed out") from exc
        except OfficeError:
            raise
        except Exception as exc:
            raise OfficeError(
                ErrorCode.RENDER_FAILED, "domOXML could not render the presentation"
            ) from exc

    async def export_pptx(self, snapshot: PresentationSnapshot) -> tuple[bytes, object]:
        if snapshot.imported_pptx_b64 and not snapshot.content_changed_after_import:
            return base64.b64decode(snapshot.imported_pptx_b64), None
        if not snapshot.slides:
            buffer = io.BytesIO()
            PptxPresentation().save(buffer)
            return buffer.getvalue(), None
        result = await self.render(snapshot, {OutputFormat.PPTX})
        if result.pptx is None:
            raise OfficeError(ErrorCode.EXPORT_FAILED, "domOXML produced no PPTX output")
        return result.pptx, result

    async def preview_pngs(
        self, snapshot: PresentationSnapshot, indices: set[int]
    ) -> tuple[bytes, ...]:
        if not indices:
            return ()
        result = await self.render(snapshot, {OutputFormat.PNG}, indices=indices)
        return result.pngs

    async def validate(self, snapshot: PresentationSnapshot, indices: set[int] | None = None):
        if not snapshot.slides:
            return None
        return await self.render(snapshot, {OutputFormat.PPTX}, indices=indices)

    async def import_pptx(self, data: bytes) -> ImportedPresentation:
        try:
            async with self._render_slots, asyncio.timeout(self._timeout_seconds):
                imported = await asyncio.to_thread(pptx_to_html, data)
        except TimeoutError as exc:
            raise OfficeError(ErrorCode.IMPORT_FAILED, "PPTX import timed out") from exc
        except Exception as exc:
            raise OfficeError(ErrorCode.IMPORT_FAILED, "domOXML could not import the PPTX") from exc
        assets = {
            asset.path: (
                mimetypes.guess_type(asset.path)[0] or "application/octet-stream",
                base64.b64encode(asset.data).decode(),
            )
            for asset in imported.assets
        }
        slides: list[StoredSlide] = []
        for index, source in enumerate(imported.slides, start=1):
            html = _inline_css(source.html, imported.css)
            for path, (mime_type, encoded) in assets.items():
                html = html.replace(path, f"data:{mime_type};base64,{encoded}")
            normalized, _ = sanitize_fragment(html)
            soup = BeautifulSoup(normalized, "html.parser")
            title = soup.find(["h1", "h2", "h3", "title"])
            name = (
                " ".join(title.stripped_strings)[:80]
                if isinstance(title, Tag)
                else f"Slide {index}"
            )
            slides.append(StoredSlide(slide_id="", name=name or f"Slide {index}", html=normalized))
        warnings: list[dict[str, object]] = [
            {
                "code": "DOMOXML_WARNING",
                "message": item.message,
                "element": item.element or None,
            }
            for item in imported.warnings
        ]
        preservation = [item.model_dump(mode="json") for item in imported.preserved]
        coverage = [item.model_dump(mode="json") for item in imported.coverage.items]
        return ImportedPresentation(slides, warnings, preservation, coverage)
