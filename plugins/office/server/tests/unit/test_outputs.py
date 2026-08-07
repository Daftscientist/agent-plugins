from pathlib import Path

from office_mcp.outputs import OfficeResourceOutputSink
from office_mcp.storage.protocols import RequestScope


async def test_outputs_are_immutable_scoped_and_purged_with_presentation(tmp_path: Path) -> None:
    sink = OfficeResourceOutputSink(tmp_path)
    scope_a, scope_b = RequestScope("a"), RequestScope("b")
    presentation_id = "prs_12345678"
    uri = f"office://presentations/{presentation_id}/revisions/rev_12345678/file"
    await sink.publish(scope_a, uri, b"pptx")
    assert await sink.read(scope_a, uri) == b"pptx"
    assert await sink.read(scope_b, uri) is None
    await sink.publish(scope_a, uri, b"pptx")
    await sink.delete_presentation(scope_a, presentation_id)
    assert await sink.read(scope_a, uri) is None
