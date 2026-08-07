from pathlib import Path

import pytest

from office_mcp.domain.state import PresentationSnapshot, StoredSlide, now_utc
from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.ids import presentation_id, revision_id, slide_id
from office_mcp.models.common import PresentationTheme, PresetSlideSize, SlideSizePreset
from office_mcp.storage.protocols import RequestScope
from office_mcp.storage.sqlite import LocalPresentationStore


def snapshot(name: str = "Deck") -> PresentationSnapshot:
    now = now_utc()
    return PresentationSnapshot(
        presentation_id=presentation_id(),
        revision_id=revision_id(),
        name=name,
        size=PresetSlideSize(preset=SlideSizePreset.WIDE_16_9),
        theme=PresentationTheme(),
        slides=[StoredSlide(slide_id=slide_id(), name="Cover", html="<h1>Hello market</h1>")],
        created_at=now,
        updated_at=now,
    )


async def test_store_create_get_commit_search_delete_and_restart(tmp_path: Path) -> None:
    database = tmp_path / "office.sqlite3"
    store = LocalPresentationStore(database)
    scope = RequestScope("a")
    original = snapshot()
    await store.create(scope, original)
    assert (await store.get(scope, original.presentation_id)).revision_id == original.revision_id
    assert await store.search_ids(scope, "market", ["slide_text"]) == [original.presentation_id]

    changed = original.model_copy(deep=True)
    changed.parent_revision_id = original.revision_id
    changed.revision_id = revision_id()
    changed.name = "Renamed"
    changed.updated_at = now_utc()
    await store.commit(scope, changed, original.revision_id)
    assert (
        await LocalPresentationStore(database).get(scope, original.presentation_id)
    ).name == "Renamed"
    assert (await store.get(scope, original.presentation_id, original.revision_id)).name == "Deck"
    await store.delete(scope, original.presentation_id, changed.revision_id)
    with pytest.raises(OfficeError):
        await store.get(scope, original.presentation_id)


async def test_store_isolation_and_revision_conflict(tmp_path: Path) -> None:
    store = LocalPresentationStore(tmp_path / "office.sqlite3")
    scope_a, scope_b = RequestScope("a"), RequestScope("b")
    original = snapshot()
    await store.create(scope_a, original)
    with pytest.raises(OfficeError) as hidden:
        await store.get(scope_b, original.presentation_id)
    assert hidden.value.code is ErrorCode.PRESENTATION_NOT_FOUND
    assert await store.search_ids(scope_b, "market", ["slide_text"]) == []
    changed = original.model_copy(deep=True)
    changed.parent_revision_id = original.revision_id
    changed.revision_id = revision_id()
    changed.updated_at = now_utc()
    with pytest.raises(OfficeError) as conflict:
        await store.commit(scope_a, changed, revision_id())
    assert conflict.value.code is ErrorCode.REVISION_CONFLICT
