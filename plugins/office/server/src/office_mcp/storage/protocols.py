"""Storage and request-scope abstraction seams."""

from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Protocol

from office_mcp.domain.state import PresentationSnapshot


@dataclass(frozen=True)
class RequestScope:
    key: str


LOCAL_SCOPE = RequestScope("local")
_REQUEST_SCOPE: ContextVar[RequestScope] = ContextVar("office_request_scope", default=LOCAL_SCOPE)


def bind_request_scope(scope: RequestScope) -> Token[RequestScope]:
    """Bind hidden request identity for scoped caches/event fan-out in this task."""
    return _REQUEST_SCOPE.set(scope)


def reset_request_scope(token: Token[RequestScope]) -> None:
    _REQUEST_SCOPE.reset(token)


def bound_request_scope() -> RequestScope:
    return _REQUEST_SCOPE.get()


class RequestScopeProvider(Protocol):
    async def current(self) -> RequestScope: ...


class LocalScopeProvider:
    async def current(self) -> RequestScope:
        return LOCAL_SCOPE


class PresentationStore(Protocol):
    async def create(self, scope: RequestScope, snapshot: PresentationSnapshot) -> None: ...

    async def get(
        self, scope: RequestScope, presentation_id: str, revision_id: str | None = None
    ) -> PresentationSnapshot: ...

    async def commit(
        self,
        scope: RequestScope,
        snapshot: PresentationSnapshot,
        expected_revision: str | None,
    ) -> None: ...

    async def delete(
        self, scope: RequestScope, presentation_id: str, expected_revision: str | None
    ) -> None: ...

    async def list_current(self, scope: RequestScope) -> list[PresentationSnapshot]: ...

    async def search_ids(self, scope: RequestScope, query: str, fields: list[str]) -> list[str]: ...


class InputResolver(Protocol):
    async def resolve(self, uri: str) -> bytes: ...


class OutputSink(Protocol):
    async def publish(self, scope: RequestScope, uri: str, data: bytes) -> None: ...

    async def read(self, scope: RequestScope, uri: str) -> bytes | None: ...

    async def delete_presentation(self, scope: RequestScope, presentation_id: str) -> None: ...
