"""Bind hidden principal scope to modern MCP listen streams."""

from typing import Any
from urllib.parse import unquote, urlsplit

from mcp.server import MCPServer
from mcp.server.context import ServerRequestContext
from mcp.server.subscriptions import ListenHandler, SubscriptionBus
from mcp_types import SubscriptionsListenRequestParams, SubscriptionsListenResult

from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.storage.protocols import (
    PresentationStore,
    RequestScopeProvider,
    bind_request_scope,
    reset_request_scope,
)


def register_scoped_subscriptions(
    mcp: MCPServer[Any],
    scopes: RequestScopeProvider,
    store: PresentationStore,
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
                parsed = urlsplit(uri)
                path = [unquote(part) for part in parsed.path.split("/") if part]
                if parsed.scheme != "office" or parsed.fragment:
                    raise OfficeError(ErrorCode.ACCESS_DENIED, "resource subscription is invalid")
                if parsed.netloc == "capabilities" and not path:
                    continue
                if parsed.netloc != "presentations" or not path:
                    raise OfficeError(ErrorCode.ACCESS_DENIED, "resource subscription is invalid")
                # Use the same scoped store lookup that backs every dynamic
                # resource read before accepting a subscription.
                await store.get(scope, path[0])
            return await delegate(ctx, params)
        finally:
            reset_request_scope(token)

    mcp._lowlevel_server.add_request_handler(  # pyright: ignore[reportPrivateUsage]
        "subscriptions/listen", SubscriptionsListenRequestParams, scoped_listen
    )
