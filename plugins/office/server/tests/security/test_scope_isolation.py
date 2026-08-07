from pathlib import Path

import pytest

from office_mcp.config import OfficeConfig
from office_mcp.domain.cursors import CursorCodec
from office_mcp.domain.service import PresentationService
from office_mcp.domoxml_adapter import DomOXMLAdapter
from office_mcp.errors import OfficeError
from office_mcp.inputs import CompositeInputResolver
from office_mcp.models.presentation import (
    NewSlide,
    PresentationCreateArgs,
    PresentationExportArgs,
    PresentationInspectArgs,
    PresentationSearchArgs,
)
from office_mcp.models.preview import PresentationPreviewArgs
from office_mcp.outputs import OfficeResourceOutputSink
from office_mcp.storage.protocols import RequestScope
from office_mcp.storage.sqlite import LocalPresentationStore


async def test_guessed_ids_cursors_search_preview_and_export_do_not_cross_scope(
    tmp_path: Path,
) -> None:
    config = OfficeConfig(data_dir=tmp_path)
    service = PresentationService(
        LocalPresentationStore(tmp_path / "db.sqlite3"),
        CompositeInputResolver(config),
        OfficeResourceOutputSink(tmp_path / "exports"),
        DomOXMLAdapter(),
        CursorCodec(b"scope-key" * 4),
        config,
    )
    scope_a, scope_b = RequestScope("a"), RequestScope("b")
    created = await service.create(
        scope_a,
        PresentationCreateArgs(
            name="Secret A", slides=[NewSlide(name="Secret", html="<h1>tenant secret</h1>")]
        ),
    )
    assert not (await service.search(scope_b, PresentationSearchArgs(query="secret"))).items
    for action in (
        service.inspect(scope_b, PresentationInspectArgs(presentation_id=created.presentation_id)),
        service.preview(scope_b, PresentationPreviewArgs(presentation_id=created.presentation_id)),
        service.export(scope_b, PresentationExportArgs(presentation_id=created.presentation_id)),
    ):
        with pytest.raises(OfficeError):
            await action


async def test_search_cursor_is_scope_and_filter_bound(tmp_path: Path) -> None:
    config = OfficeConfig(data_dir=tmp_path)
    service = PresentationService(
        LocalPresentationStore(tmp_path / "db.sqlite3"),
        CompositeInputResolver(config),
        OfficeResourceOutputSink(tmp_path / "exports"),
        DomOXMLAdapter(),
        CursorCodec(b"scope-key" * 4),
        config,
    )
    scope = RequestScope("a")
    for index in range(3):
        await service.create(scope, PresentationCreateArgs(name=f"Deck {index}"))
    first = await service.search(scope, PresentationSearchArgs(limit=1))
    assert first.next_cursor
    with pytest.raises(OfficeError):
        await service.search(
            RequestScope("b"), PresentationSearchArgs(limit=1, cursor=first.next_cursor)
        )
    with pytest.raises(OfficeError):
        await service.search(
            scope, PresentationSearchArgs(query="different", limit=1, cursor=first.next_cursor)
        )
