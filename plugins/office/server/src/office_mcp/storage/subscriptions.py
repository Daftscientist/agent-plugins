"""Principal-scoped MCP subscription fan-out."""

import logging
from collections.abc import Callable

import anyio.lowlevel
from mcp.server.subscriptions import ServerEvent

from .protocols import bound_request_scope

logger = logging.getLogger(__name__)


class ScopedSubscriptionBus:
    """Keep resource/list events inside the hidden request scope that published them."""

    def __init__(self) -> None:
        self._listeners: dict[object, tuple[str, Callable[[ServerEvent], None]]] = {}

    async def publish(self, event: ServerEvent) -> None:
        scope_key = bound_request_scope().key
        for listener_scope, listener in list(self._listeners.values()):
            if listener_scope != scope_key:
                continue
            try:
                listener(event)
            except Exception:
                logger.exception("scoped subscription listener raised; continuing")
        await anyio.lowlevel.checkpoint()

    def subscribe(self, listener: Callable[[ServerEvent], None]) -> Callable[[], None]:
        token = object()
        self._listeners[token] = (bound_request_scope().key, listener)

        def unsubscribe() -> None:
            self._listeners.pop(token, None)

        return unsubscribe
