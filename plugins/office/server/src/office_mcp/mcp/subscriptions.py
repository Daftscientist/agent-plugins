"""Bind hidden principal scope to modern MCP listen streams."""

from typing import Any

from mcp.server import MCPServer
from mcp.server.context import ServerRequestContext
from mcp.server.subscriptions import ListenHandler, SubscriptionBus
from mcp_types import SubscriptionsListenRequestParams, SubscriptionsListenResult

from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.storage.protocols import (
    RequestScopeProvider,
    bind_request_scope,
    reset_request_scope,
)


def register_scoped_subscriptions(
    mcp: MCPServer[Any],
    scopes: RequestScopeProvider,
    bus: SubscriptionBus,
) -> None:
    delegate = ListenHandler(bus)

    async def scoped_listen(
        ctx: ServerRequestContext[Any, Any], params: SubscriptionsListenRequestParams
    ) -> SubscriptionsListenResult:
        scope = await scopes.current()
        token = bind_request_scope(scope)
        try:
            for uri in params.notifications.resource_subscriptions or []:
                # Route every requested URI through the exact same resource-manager
                # dispatch that backs `resources/read` (template matching, ID
                # validation, and the handler's own scoped existence check) so a
                # subscription can never be accepted for a URI a read would reject.
                # Reusing the real read - rather than a hand-rolled parallel check -
                # is the only way to guarantee the two never drift apart.
                try:
                    await mcp.read_resource(uri)
                except Exception as exc:
                    raise OfficeError(
                        ErrorCode.ACCESS_DENIED, "resource subscription is invalid"
                    ) from exc
            return await delegate(ctx, params)
        finally:
            reset_request_scope(token)

    mcp._lowlevel_server.add_request_handler(  # pyright: ignore[reportPrivateUsage]
        "subscriptions/listen", SubscriptionsListenRequestParams, scoped_listen
    )
