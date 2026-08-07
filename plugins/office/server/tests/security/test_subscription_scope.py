from pathlib import Path
from typing import Any

import pytest
from mcp import Client, MCPError
from mcp.server import MCPServer
from mcp.server.subscriptions import ResourceUpdated, ServerEvent

from office_mcp.app import OfficeRuntime, create_server
from office_mcp.config import OfficeConfig
from office_mcp.models.presentation import NewSlide, PresentationCreateArgs
from office_mcp.models.slide import SlideInspectArgs, SlideInspectDetail
from office_mcp.storage.protocols import (
    RequestScope,
    bind_request_scope,
    reset_request_scope,
)
from office_mcp.storage.subscriptions import ScopedSubscriptionBus


class SwitchingScopeProvider:
    def __init__(self, scope: RequestScope) -> None:
        self.scope = scope

    async def current(self) -> RequestScope:
        return self.scope


async def test_subscription_events_never_cross_hidden_request_scopes() -> None:
    bus = ScopedSubscriptionBus()
    scope_a, scope_b = RequestScope("a"), RequestScope("b")
    received_a: list[ServerEvent] = []
    received_b: list[ServerEvent] = []

    token = bind_request_scope(scope_a)
    unsubscribe_a = bus.subscribe(received_a.append)
    reset_request_scope(token)
    token = bind_request_scope(scope_b)
    unsubscribe_b = bus.subscribe(received_b.append)
    reset_request_scope(token)

    event = ResourceUpdated(uri="office://presentations/prs_secret123")
    token = bind_request_scope(scope_a)
    await bus.publish(event)
    reset_request_scope(token)
    assert received_a == [event]
    assert received_b == []

    unsubscribe_a()
    unsubscribe_b()


async def test_subscription_requires_the_same_scoped_resource_authorization_as_read(
    tmp_path: Path,
) -> None:
    scope_a, scope_b = RequestScope("a"), RequestScope("b")
    scopes = SwitchingScopeProvider(scope_a)
    server: tuple[MCPServer[Any], OfficeRuntime] = create_server(
        OfficeConfig(data_dir=tmp_path / "office"), scopes=scopes
    )
    mcp, runtime = server
    created = await runtime.service.create(
        scope_a, PresentationCreateArgs(name="Only A can read this")
    )
    scopes.scope = scope_b
    async with Client(mcp) as client:
        with pytest.raises(MCPError):
            async with client.listen(
                resource_subscriptions=[f"office://presentations/{created.presentation_id}"]
            ):
                pytest.fail("an unauthorized subscription was accepted")


async def test_subscription_rejects_a_nonexistent_slide_a_read_would_also_reject(
    tmp_path: Path,
) -> None:
    """Subscription authorization must validate the full route (slide/revision/element),
    not just the presentation - a bug previously let a subscription through for an exact
    URI that `resources/read` would reject, because only the leading path segment
    (the presentation ID) was checked."""
    scope = RequestScope("only-scope")
    scopes = SwitchingScopeProvider(scope)
    server: tuple[MCPServer[Any], OfficeRuntime] = create_server(
        OfficeConfig(data_dir=tmp_path / "office"), scopes=scopes
    )
    mcp, runtime = server
    created = await runtime.service.create(scope, PresentationCreateArgs(name="Real deck"))
    nonexistent_slide_uri = (
        f"office://presentations/{created.presentation_id}/slides/sld_00000000nonexistent"
    )
    async with Client(mcp) as client:
        with pytest.raises(MCPError):
            await client.read_resource(nonexistent_slide_uri)
        with pytest.raises(MCPError):
            async with client.listen(resource_subscriptions=[nonexistent_slide_uri]):
                pytest.fail("a subscription for a nonexistent slide was accepted")


async def test_subscription_and_read_agree_for_every_resource_family(tmp_path: Path) -> None:
    """For every registered resource template, a subscription must be accepted exactly
    when the equivalent read would succeed, and rejected exactly when it would fail -
    covering the presentation, revision, slide, and element route families, not just
    the presentation-level check the earlier bug happened to leave in place."""
    scope = RequestScope("only-scope")
    scopes = SwitchingScopeProvider(scope)
    server: tuple[MCPServer[Any], OfficeRuntime] = create_server(
        OfficeConfig(data_dir=tmp_path / "office"), scopes=scopes
    )
    mcp, runtime = server
    created = await runtime.service.create(
        scope,
        PresentationCreateArgs(
            name="Every family",
            slides=[
                NewSlide(name="Cover", html='<section><p data-office-name="x">Hi</p></section>')
            ],
        ),
    )
    pid = created.presentation_id
    revision = created.revision
    sid = created.slides[0].slide_id
    inspected = await runtime.service.slide_inspect(
        scope,
        SlideInspectArgs(presentation_id=pid, slide_id=sid, detail=SlideInspectDetail.STRUCTURE),
    )
    assert inspected.structure
    element = inspected.structure[0].element_id

    bad_pid = "prs_00000000nonexistent"
    bad_revision = "rev_00000000nonexistent"
    bad_slide = "sld_00000000nonexistent"
    bad_element = "el_00000000nonexistent"

    accepted = [
        f"office://presentations/{pid}",
        f"office://presentations/{pid}/outline",
        f"office://presentations/{pid}/validation",
        f"office://presentations/{pid}/revisions/{revision}",
        f"office://presentations/{pid}/slides/{sid}",
        f"office://presentations/{pid}/slides/{sid}/source",
        f"office://presentations/{pid}/slides/{sid}/elements/{element}",
    ]
    rejected = [
        f"office://presentations/{bad_pid}",
        f"office://presentations/{bad_pid}/outline",
        f"office://presentations/{pid}/revisions/{bad_revision}",
        f"office://presentations/{pid}/slides/{bad_slide}",
        f"office://presentations/{pid}/slides/{bad_slide}/source",
        f"office://presentations/{pid}/slides/{sid}/elements/{bad_element}",
    ]

    async with Client(mcp) as client:
        for uri in accepted:
            await client.read_resource(uri)
            async with client.listen(resource_subscriptions=[uri]):
                pass
        for uri in rejected:
            with pytest.raises(MCPError):
                await client.read_resource(uri)
            with pytest.raises(MCPError):
                async with client.listen(resource_subscriptions=[uri]):
                    pytest.fail(f"a subscription for a read-rejected URI was accepted: {uri}")
