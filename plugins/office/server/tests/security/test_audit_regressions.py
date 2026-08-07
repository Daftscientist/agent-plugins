from datetime import datetime

import pytest
from bs4 import BeautifulSoup, Tag
from mcp.server import MCPServer
from pydantic import ValidationError

from office_mcp.app import OfficeRuntime
from office_mcp.domain.service import PresentationService
from office_mcp.models.common import PresentationTheme, ThemeFonts, ThemePalette
from office_mcp.models.element import ElementById, ElementMutation, ElementUpdateArgs
from office_mcp.models.presentation import (
    NewSlide,
    PresentationCreateArgs,
    PresentationSearchArgs,
    PresentationUpdateArgs,
)
from office_mcp.models.slide import SlideInspectArgs, SlideInspectDetail, SlideUpdateArgs
from office_mcp.storage.protocols import LOCAL_SCOPE


def test_theme_palette_rejects_render_time_network_and_css_indirection() -> None:
    for unsafe in (
        "url(http://127.0.0.1/pixel.png)",
        "url(https://example.com/pixel.png)",
        "var(--attacker)",
        "#fff;background:url(http://127.0.0.1/pixel.png)",
    ):
        with pytest.raises(ValidationError):
            ThemePalette(background=unsafe)
    assert ThemePalette(background="oklch(70% 0.15 250)").background.startswith("oklch")
    with pytest.raises(ValidationError):
        ThemeFonts(body="url(http://127.0.0.1/font.woff2)")


def test_required_names_reject_explicit_null_and_filename_keeps_extension() -> None:
    with pytest.raises(ValidationError, match="presentation name cannot be cleared"):
        PresentationUpdateArgs.model_validate({"presentation_id": "prs_12345678", "name": None})
    with pytest.raises(ValidationError, match="slide name cannot be cleared"):
        SlideUpdateArgs.model_validate(
            {
                "presentation_id": "prs_12345678",
                "slide_id": "sld_12345678",
                "name": None,
            }
        )
    invalid_themes: tuple[object, ...] = (
        None,
        {},
        {"palette": {}},
        {"palette": {"background": None}},
    )
    for theme in invalid_themes:
        with pytest.raises(ValidationError):
            PresentationUpdateArgs.model_validate(
                {"presentation_id": "prs_12345678", "theme": theme}
            )
    filename = PresentationService.sanitize_filename("x" * 255)
    assert len(filename) == 255 and filename.endswith(".pptx")


async def test_naive_datetime_search_is_normalized_to_utc(
    office: tuple[MCPServer[object], OfficeRuntime],
) -> None:
    _, runtime = office
    created = await runtime.service.create(
        LOCAL_SCOPE, PresentationCreateArgs(name="Time-safe search")
    )
    result = await runtime.service.search(
        LOCAL_SCOPE, PresentationSearchArgs(created_after=datetime(2020, 1, 1))
    )
    assert [item.presentation_id for item in result.items] == [created.presentation_id]


async def test_empty_inner_html_removes_all_children_without_inventing_markup(
    office: tuple[MCPServer[object], OfficeRuntime],
) -> None:
    _, runtime = office
    created = await runtime.service.create(
        LOCAL_SCOPE,
        PresentationCreateArgs(
            name="Clear children",
            slides=[NewSlide(name="One", html="<section><p>Remove me</p></section>")],
            theme=PresentationTheme(),
        ),
    )
    inspected = await runtime.service.slide_inspect(
        LOCAL_SCOPE,
        SlideInspectArgs(
            presentation_id=created.presentation_id,
            slide_id=created.slides[0].slide_id,
            detail=SlideInspectDetail.STRUCTURE,
        ),
    )
    root = (inspected.structure or [])[0]
    updated = await runtime.service.element_update(
        LOCAL_SCOPE,
        ElementUpdateArgs(
            presentation_id=created.presentation_id,
            slide_id=created.slides[0].slide_id,
            elements=[
                ElementMutation(element=ElementById(element_id=root.element_id), inner_html="")
            ],
        ),
    )
    source = await runtime.service.slide_inspect(
        LOCAL_SCOPE,
        SlideInspectArgs(
            presentation_id=created.presentation_id,
            slide_id=created.slides[0].slide_id,
            revision=updated.revision,
            detail=SlideInspectDetail.SOURCE,
        ),
    )
    soup = BeautifulSoup(source.html or "", "html.parser")
    section = soup.find("section")
    assert isinstance(section, Tag)
    assert not section.contents
