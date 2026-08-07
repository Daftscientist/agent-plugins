from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from mcp.server import MCPServer

from office_mcp.app import OfficeRuntime, create_server
from office_mcp.config import OfficeConfig


@pytest.fixture
def office(tmp_path: Path) -> Iterator[tuple[MCPServer[Any], OfficeRuntime]]:
    config = OfficeConfig(data_dir=tmp_path / "office", cursor_secret=b"test-secret" * 4)
    yield create_server(config)
