"""Storage adapters."""

from .protocols import LOCAL_SCOPE, LocalScopeProvider, RequestScope
from .sqlite import LocalPresentationStore

__all__ = ["LOCAL_SCOPE", "LocalPresentationStore", "LocalScopeProvider", "RequestScope"]
