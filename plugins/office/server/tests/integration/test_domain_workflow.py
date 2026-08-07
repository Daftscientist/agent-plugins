from typing import Any

import pytest
from mcp.server import MCPServer

from office_mcp.app import OfficeRuntime
from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.models.element import (
    ElementAddArgs,
    ElementById,
    ElementByName,
    ElementDeleteArgs,
    ElementInsertPosition,
    ElementInspectArgs,
    ElementMoveArgs,
    ElementMoveOperation,
    ElementMutation,
    ElementUpdateArgs,
    StyleMutation,
)
from office_mcp.models.presentation import (
    NewSlide,
    PresentationCreateArgs,
    PresentationDeleteArgs,
    PresentationInspectArgs,
    PresentationSearchArgs,
    PresentationUpdateArgs,
)
from office_mcp.models.slide import (
    InsertEnd,
    SlideAddArgs,
    SlideDeleteArgs,
    SlideDuplicateArgs,
    SlideInspectArgs,
    SlideInspectDetail,
    SlideReorderArgs,
    SlideUpdateArgs,
)
from office_mcp.storage.protocols import LOCAL_SCOPE


async def test_all_metadata_slide_and_element_operations(
    office: tuple[MCPServer[Any], OfficeRuntime],
) -> None:
    _, runtime = office
    service = runtime.service
    created = await service.create(
        LOCAL_SCOPE,
        PresentationCreateArgs(
            name="Metrics",
            slides=[
                NewSlide(
                    name="Cover",
                    description="Opening",
                    html=(
                        '<section data-office-name="root" style="padding:20px">'
                        '<h1 data-office-name="title" style="color:red">Hello</h1>'
                        '<p data-office-name="metric">$1M</p></section>'
                    ),
                )
            ],
        ),
    )
    pid, first_revision = created.presentation_id, created.revision
    slide = created.slides[0].slide_id
    inspected = await service.inspect(LOCAL_SCOPE, PresentationInspectArgs(presentation_id=pid))
    assert inspected.slide_count == 1

    structure = await service.slide_inspect(
        LOCAL_SCOPE,
        SlideInspectArgs(presentation_id=pid, slide_id=slide, detail=SlideInspectDetail.STRUCTURE),
    )
    title_id = next(
        item.element_id for item in structure.structure or [] if item.element_name == "title"
    )
    metric_id = next(
        item.element_id for item in structure.structure or [] if item.element_name == "metric"
    )
    element = await service.element_inspect(
        LOCAL_SCOPE,
        ElementInspectArgs(
            presentation_id=pid, slide_id=slide, element=ElementByName(element_name="title")
        ),
    )
    assert element.element_id == title_id and element.styles == {"color": "red"}

    updated = await service.element_update(
        LOCAL_SCOPE,
        ElementUpdateArgs(
            presentation_id=pid,
            slide_id=slide,
            expected_revision=first_revision,
            elements=[
                ElementMutation(
                    element=ElementByName(element_name="title"),
                    text="Updated",
                    styles=StyleMutation(set={"color": "blue"}),
                ),
                ElementMutation(element=ElementByName(element_name="metric"), text="$2M"),
            ],
        ),
    )
    assert updated.updated_element_ids == [title_id, metric_id]
    after = await service.slide_inspect(
        LOCAL_SCOPE,
        SlideInspectArgs(presentation_id=pid, slide_id=slide, detail=SlideInspectDetail.SOURCE),
    )
    assert "Updated" in (after.html or "") and "$2M" in (after.html or "")
    assert title_id in (after.html or "")

    added = await service.element_add(
        LOCAL_SCOPE,
        ElementAddArgs(
            presentation_id=pid,
            slide_id=slide,
            relative_to=ElementByName(element_name="root"),
            position=ElementInsertPosition.APPEND,
            html='<p data-office-name="new">New</p>',
            expected_revision=updated.revision,
        ),
    )
    new_id = added.roots[0].element_id
    moved = await service.element_move(
        LOCAL_SCOPE,
        ElementMoveArgs(
            presentation_id=pid,
            slide_id=slide,
            moves=[
                ElementMoveOperation(
                    element=ElementById(element_id=new_id),
                    relative_to=ElementById(element_id=title_id),
                    position=ElementInsertPosition.BEFORE,
                )
            ],
            expected_revision=added.revision,
        ),
    )
    deleted = await service.element_delete(
        LOCAL_SCOPE,
        ElementDeleteArgs(
            presentation_id=pid,
            slide_id=slide,
            elements=[ElementById(element_id=new_id)],
            expected_revision=moved.revision,
        ),
    )
    assert deleted.deleted_element_ids == [new_id]

    slide_updated = await service.slide_update(
        LOCAL_SCOPE,
        SlideUpdateArgs(
            presentation_id=pid,
            slide_id=slide,
            name="Updated cover",
            expected_revision=deleted.revision,
        ),
    )
    duplicate = await service.slide_duplicate(
        LOCAL_SCOPE,
        SlideDuplicateArgs(
            presentation_id=pid,
            slide_id=slide,
            name="Copy",
            expected_revision=slide_updated.revision,
        ),
    )
    assert duplicate.slide.slide_id != slide
    duplicate_source = await service.slide_inspect(
        LOCAL_SCOPE,
        SlideInspectArgs(
            presentation_id=pid,
            slide_id=duplicate.slide.slide_id,
            detail=SlideInspectDetail.SOURCE,
        ),
    )
    assert title_id not in (duplicate_source.html or "")

    added_slides = await service.slide_add(
        LOCAL_SCOPE,
        SlideAddArgs(
            presentation_id=pid,
            slides=[NewSlide(name="Third", html="<section><h2>Third</h2></section>")],
            position=InsertEnd(),
            expected_revision=duplicate.revision,
        ),
    )
    desired = [added_slides.added[0].slide_id, duplicate.slide.slide_id, slide]
    reordered = await service.slide_reorder(
        LOCAL_SCOPE,
        SlideReorderArgs(
            presentation_id=pid,
            slide_ids=desired,
            expected_revision=added_slides.revision,
        ),
    )
    assert [item.slide_id for item in reordered.slides] == desired
    removed = await service.slide_delete(
        LOCAL_SCOPE,
        SlideDeleteArgs(
            presentation_id=pid,
            slide_ids=[duplicate.slide.slide_id],
            expected_revision=reordered.revision,
        ),
    )
    metadata = await service.update(
        LOCAL_SCOPE,
        PresentationUpdateArgs(
            presentation_id=pid,
            name="Renamed metrics",
            description=None,
            expected_revision=removed.revision,
        ),
    )
    search = await service.search(LOCAL_SCOPE, PresentationSearchArgs(query="Third"))
    assert search.items[0].presentation_id == pid
    await service.delete(
        LOCAL_SCOPE,
        PresentationDeleteArgs(presentation_id=pid, expected_revision=metadata.revision),
    )
    with pytest.raises(OfficeError):
        await service.inspect(LOCAL_SCOPE, PresentationInspectArgs(presentation_id=pid))


async def test_stale_revision_and_invalid_hierarchy_operations_are_atomic(
    office: tuple[MCPServer[Any], OfficeRuntime],
) -> None:
    _, runtime = office
    service = runtime.service
    created = await service.create(
        LOCAL_SCOPE,
        PresentationCreateArgs(
            name="Concurrency",
            slides=[
                NewSlide(
                    name="One",
                    html=(
                        '<section data-office-name="root">'
                        '<p data-office-name="child">x</p></section>'
                    ),
                )
            ],
        ),
    )
    pid, sid = created.presentation_id, created.slides[0].slide_id
    fresh = await service.update(
        LOCAL_SCOPE,
        PresentationUpdateArgs(
            presentation_id=pid, name="Fresh", expected_revision=created.revision
        ),
    )
    with pytest.raises(OfficeError) as conflict:
        await service.update(
            LOCAL_SCOPE,
            PresentationUpdateArgs(
                presentation_id=pid, name="Stale", expected_revision=created.revision
            ),
        )
    assert conflict.value.code is ErrorCode.REVISION_CONFLICT
    with pytest.raises(OfficeError) as cycle:
        await service.element_move(
            LOCAL_SCOPE,
            ElementMoveArgs(
                presentation_id=pid,
                slide_id=sid,
                moves=[
                    ElementMoveOperation(
                        element=ElementByName(element_name="root"),
                        relative_to=ElementByName(element_name="child"),
                        position=ElementInsertPosition.APPEND,
                    )
                ],
                expected_revision=fresh.revision,
            ),
        )
    assert cycle.value.code is ErrorCode.INVALID_ELEMENT_MOVE
    assert (
        await service.inspect(LOCAL_SCOPE, PresentationInspectArgs(presentation_id=pid))
    ).revision == fresh.revision
