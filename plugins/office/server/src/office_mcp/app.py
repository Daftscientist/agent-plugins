"""Office MCP application composition root."""

from dataclasses import dataclass

from mcp.server import MCPServer
from mcp.server.subscriptions import SubscriptionBus

from office_mcp.config import OfficeConfig
from office_mcp.domain.cursors import CursorCodec
from office_mcp.domain.service import PresentationService
from office_mcp.domoxml_adapter import DomOXMLAdapter
from office_mcp.icons import OFFICE_ICONS
from office_mcp.inputs import CompositeInputResolver
from office_mcp.mcp import (
    register_completions,
    register_prompts,
    register_resources,
    register_scoped_subscriptions,
    register_tools,
)
from office_mcp.outputs import OfficeResourceOutputSink
from office_mcp.storage import LocalPresentationStore, LocalScopeProvider
from office_mcp.storage.protocols import (
    InputResolver,
    OutputSink,
    PresentationStore,
    RequestScopeProvider,
)
from office_mcp.storage.subscriptions import ScopedSubscriptionBus


@dataclass(frozen=True)
class OfficeRuntime:
    config: OfficeConfig
    store: PresentationStore
    scopes: RequestScopeProvider
    output: OutputSink
    service: PresentationService
    cursor: CursorCodec


def create_server(
    config: OfficeConfig | None = None,
    *,
    store: PresentationStore | None = None,
    scopes: RequestScopeProvider | None = None,
    resolver: InputResolver | None = None,
    output: OutputSink | None = None,
    adapter: DomOXMLAdapter | None = None,
    subscriptions: SubscriptionBus | None = None,
) -> tuple[MCPServer, OfficeRuntime]:
    config = config or OfficeConfig.from_env()
    config.prepare()
    store = store or LocalPresentationStore(config.data_dir / "office.sqlite3")
    scopes = scopes or LocalScopeProvider()
    resolver = resolver or CompositeInputResolver(config)
    output = output or OfficeResourceOutputSink(config.data_dir / "exports")
    adapter = adapter or DomOXMLAdapter(
        max_concurrency=config.max_render_concurrency,
        timeout_seconds=config.operation_timeout_seconds,
    )
    cursor = CursorCodec(config.cursor_secret)
    service = PresentationService(
        store=store,
        resolver=resolver,
        output=output,
        adapter=adapter,
        cursor=cursor,
        config=config,
    )
    subscriptions = subscriptions or ScopedSubscriptionBus()
    mcp = MCPServer(
        "Office",
        version="0.1.0",
        instructions=(
            "Create and edit Microsoft Office presentations. Author slides using semantic HTML "
            "with inline CSS. Inspect unfamiliar presentations before modifying them. Prefer "
            "element-level mutations for small edits. Use presentation_preview for visual "
            "verification and presentation_validate for editability/fidelity verification."
        ),
        icons=OFFICE_ICONS,
        subscriptions=subscriptions,
    )
    register_tools(mcp, service, scopes)
    register_resources(mcp, service, store, scopes, cursor)
    register_prompts(mcp)
    register_completions(mcp, store, scopes)
    register_scoped_subscriptions(mcp, scopes, subscriptions)
    runtime = OfficeRuntime(config, store, scopes, output, service, cursor)
    return mcp, runtime


mcp, runtime = create_server()
