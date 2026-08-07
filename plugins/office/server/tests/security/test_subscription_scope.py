from pathlib import Path
from typing import Any

import pytest
from mcp import Client, MCPError
from mcp.server import MCPServer
from mcp.server.subscriptions import ResourceUpdated, ServerEvent

from office_mcp.app import OfficeRuntime, create_server
from office_mcp.config import OfficeConfig
from office_mcp.models.presentation import PresentationCreateArgs
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
