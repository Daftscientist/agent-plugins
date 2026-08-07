from typing import Any

import anyio
import mcp_types as types
from mcp import Client
from mcp.client.subscriptions import ResourceUpdated
from mcp.server import MCPServer

from office_mcp.app import OfficeRuntime
from office_mcp.models.presentation import PresentationCreateArgs
from office_mcp.storage.protocols import LOCAL_SCOPE


async def test_identity_tools_schemas_prompts_resources_and_completions(
    office: tuple[MCPServer[Any], OfficeRuntime],
) -> None:
    mcp, _ = office
    async with Client(mcp) as client:
        info = client.server_info
        assert info is not None
        assert info.name == "Office"
        assert info.version == "0.1.0"
        assert info.icons
        assert "inline CSS" in (client.instructions or "")
        tools = await client.list_tools()
        assert len(tools.tools) == 20
        assert {tool.name for tool in tools.tools} >= {
            "presentation_create",
            "presentation_preview",
            "element_update",
        }
        for tool in tools.tools:
            assert tool.title and tool.annotations and tool.output_schema
            assert tool.input_schema.get("additionalProperties") is False
        preview = next(tool for tool in tools.tools if tool.name == "presentation_preview")
        assert (
            preview.input_schema["properties"]["selection"]["discriminator"]["propertyName"]
            == "type"
        )
        prompts = await client.list_prompts()
        assert [item.name for item in prompts.prompts] == [
            "create_presentation",
            "review_presentation",
        ]
        templates = await client.list_resource_templates()
        assert len(templates.resource_templates) == 10
        capabilities = await client.read_resource("office://capabilities")
        assert isinstance(capabilities.contents[0], types.TextResourceContents)
        assert "inline_css_only" in capabilities.contents[0].text
        listed = await client.list_resources()
        assert any(str(item.uri) == "office://capabilities" for item in listed.resources)


async def test_protocol_mutations_errors_resources_progress_and_media(
    office: tuple[MCPServer[Any], OfficeRuntime],
) -> None:
    mcp, _ = office
    progress_updates: list[tuple[float, float | None, str | None]] = []

    async def on_progress(progress: float, total: float | None, message: str | None) -> None:
        progress_updates.append((progress, total, message))

    async with Client(mcp) as client:
        malformed = await client.call_tool(
            "presentation_create", {"name": "Bad args", "unknown": True}
        )
        assert malformed.is_error
        assert isinstance(malformed.content[0], types.TextContent)
        assert "invalid presentation_create argument unknown" in malformed.content[0].text
        assert "INTERNAL_ERROR" not in malformed.content[0].text
        unsafe = await client.call_tool(
            "presentation_create",
            {"name": "Bad", "slides": [{"name": "Bad", "html": "<script>x()</script>"}]},
        )
        assert isinstance(unsafe.content[0], types.TextContent)
        assert unsafe.is_error and "UNSAFE_HTML" in unsafe.content[0].text
        created = await client.call_tool(
            "presentation_create",
            {
                "name": "Protocol",
                "slides": [
                    {
                        "name": "Cover",
                        "html": (
                            '<section><h1 data-office-name="title" '
                            'style="font-size:42px">Hello</h1></section>'
                        ),
                    }
                ],
            },
        )
        assert not created.is_error and created.structured_content
        pid = str(created.structured_content["presentation_id"])
        revision = str(created.structured_content["revision"])
        sid = str(created.structured_content["slides"][0]["slide_id"])
        structure = await client.call_tool(
            "slide_inspect",
            {"presentation_id": pid, "slide_id": sid, "detail": "structure"},
        )
        assert structure.structured_content
        title = next(
            item
            for item in structure.structured_content["structure"]
            if item["element_name"] == "title"
        )
        changed = await client.call_tool(
            "element_update",
            {
                "presentation_id": pid,
                "slide_id": sid,
                "expected_revision": revision,
                "elements": [
                    {
                        "element": {"type": "id", "element_id": title["element_id"]},
                        "text": "Changed",
                    }
                ],
            },
        )
        assert not changed.is_error
        stale = await client.call_tool(
            "presentation_update",
            {"presentation_id": pid, "expected_revision": revision, "name": "Stale"},
        )
        assert isinstance(stale.content[0], types.TextContent)
        assert stale.is_error and "REVISION_CONFLICT" in stale.content[0].text
        source = await client.read_resource(f"office://presentations/{pid}/slides/{sid}/source")
        assert isinstance(source.contents[0], types.TextResourceContents)
        assert "Changed" in source.contents[0].text
        search = await client.call_tool("presentation_search", {"query": "Changed"})
        assert search.structured_content and len(search.structured_content["items"]) == 1
        rendered = await client.call_tool(
            "presentation_preview",
            {
                "presentation_id": pid,
                "selection": {"type": "slides", "slide_ids": [sid]},
            },
            progress_callback=on_progress,
        )
        assert not rendered.is_error
        assert isinstance(rendered.content[0], types.ImageContent)
        assert rendered.structured_content
        assert rendered.structured_content["images"][0]["slide_ids"] == [sid]
        progress_updates.clear()
        exported = await client.call_tool(
            "presentation_export", {"presentation_id": pid}, progress_callback=on_progress
        )
        assert any(isinstance(item, types.ResourceLink) for item in exported.content)
        assert exported.structured_content
        file_resource = await client.read_resource(exported.structured_content["resource_uri"])
        assert isinstance(file_resource.contents[0], types.BlobResourceContents)
        assert [item[0] for item in progress_updates] == sorted(
            item[0] for item in progress_updates
        )


async def test_resource_pagination_completion_and_subscription_invalidation(
    office: tuple[MCPServer[Any], OfficeRuntime],
) -> None:
    mcp, runtime = office
    first = None
    for index in range(105):
        created = await runtime.service.create(
            LOCAL_SCOPE,
            PresentationCreateArgs(name=f"Deck {index:03d}", slides=[]),
        )
        first = first or created
    assert first is not None
    async with Client(mcp) as client:
        page1 = await client.list_resources()
        assert page1.next_cursor
        page2 = await client.list_resources(cursor=page1.next_cursor)
        assert len(page1.resources) == 100
        assert len(page2.resources) == 6 and page2.next_cursor is None
        uris = {str(item.uri) for item in page1.resources + page2.resources}
        assert len(uris) == 106 and "office://capabilities" in uris
        assert len([uri for uri in uris if uri.startswith("office://presentations/")]) == 105
        completion = await client.complete(
            types.PromptReference(type="ref/prompt", name="review_presentation"),
            {"name": "presentation_id", "value": "Deck 000"},
        )
        assert completion.completion.values
        assert "Deck 000" in completion.completion.values[0]
        root_uri = f"office://presentations/{first.presentation_id}"
        with anyio.fail_after(10):
            async with client.listen(
                resources_list_changed=True, resource_subscriptions=[root_uri]
            ) as subscription:
                update = await client.call_tool(
                    "presentation_update",
                    {
                        "presentation_id": first.presentation_id,
                        "expected_revision": first.revision,
                        "name": "Changed first",
                    },
                )
                assert not update.is_error
                assert await anext(subscription) == ResourceUpdated(uri=root_uri)


async def test_supported_legacy_client_can_discover_and_call_tools(
    office: tuple[MCPServer[Any], OfficeRuntime],
) -> None:
    mcp, _ = office
    async with Client(mcp, mode="legacy") as client:
        tools = await client.list_tools()
        assert len(tools.tools) == 20
        result = await client.call_tool("presentation_create", {"name": "Legacy client"})
        assert not result.is_error
        assert result.structured_content
        assert result.structured_content["name"] == "Legacy client"
