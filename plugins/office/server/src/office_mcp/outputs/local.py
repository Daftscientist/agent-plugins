"""Immutable local output sink."""

import asyncio
import hashlib
from pathlib import Path

from office_mcp.storage.protocols import RequestScope


class OfficeResourceOutputSink:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    async def publish(self, scope: RequestScope, uri: str, data: bytes) -> None:
        digest = hashlib.sha256(uri.encode()).hexdigest()
        scope_dir = self.root / hashlib.sha256(scope.key.encode()).hexdigest()
        scope_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        target = scope_dir / digest
        if target.exists():
            existing = await asyncio.to_thread(target.read_bytes)
            if existing != data:
                raise RuntimeError("immutable output URI collision")
            return
        await asyncio.to_thread(target.write_bytes, data)

    async def read(self, scope: RequestScope, uri: str) -> bytes | None:
        digest = hashlib.sha256(uri.encode()).hexdigest()
        target = self.root / hashlib.sha256(scope.key.encode()).hexdigest() / digest
        if not target.is_file():
            return None
        return await asyncio.to_thread(target.read_bytes)
