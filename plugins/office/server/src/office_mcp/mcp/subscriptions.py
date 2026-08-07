"""Bind hidden principal scope to modern MCP listen streams."""

from typing import Any

from mcp.server import MCPServer
from mcp.server.context import ServerRequestContext
from mcp.server.subscriptions import ListenHandler, SubscriptionBus
from mcp_types import SubscriptionsListenRequestParams, SubscriptionsListenResult

from office_mcp.storage.protocols import (
    RequestScopeProvider,
    bind_request_scope,
    reset_request_scope,
)


def register_scoped_subscriptions(
    mcp: MCPServer[Any], scopes: RequestScopeProvider, bus: SubscriptionBus
) -> None:
    delegate = ListenHandler(bus)

    async def scoped_listen(
        ctx: ServerRequestContext[Any, Any], params: SubscriptionsListenRequestParams
    ) -> SubscriptionsListenResult:
        token = bind_request_scope(await scopes.current())
        try:
            return await delegate(ctx, params)
        finally:
            reset_request_scope(token)

    mcp._lowlevel_server.add_request_handler(  # pyright: ignore[reportPrivateUsage]
        "subscriptions/listen", SubscriptionsListenRequestParams, scoped_listen
    )
