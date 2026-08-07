from mcp.server.subscriptions import ResourceUpdated, ServerEvent

from office_mcp.storage.protocols import (
    RequestScope,
    bind_request_scope,
    reset_request_scope,
)
from office_mcp.storage.subscriptions import ScopedSubscriptionBus


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
