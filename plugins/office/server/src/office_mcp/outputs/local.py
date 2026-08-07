"""Immutable local output sink."""

import asyncio
import hashlib
import re
import shutil
from pathlib import Path

from office_mcp.storage.protocols import RequestScope


class OfficeResourceOutputSink:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    @staticmethod
    def _presentation_id(uri: str) -> str | None:
        match = re.match(r"^office://presentations/(prs_[A-Za-z0-9_-]{8,})(?:/|$)", uri)
        return match.group(1) if match else None

    def _bucket(self, scope: RequestScope, uri: str) -> Path:
        scope_dir = self.root / hashlib.sha256(scope.key.encode()).hexdigest()
        presentation = self._presentation_id(uri)
        name = hashlib.sha256((presentation or "misc").encode()).hexdigest()
        return scope_dir / name

    async def publish(self, scope: RequestScope, uri: str, data: bytes) -> None:
        digest = hashlib.sha256(uri.encode()).hexdigest()
        bucket = self._bucket(scope, uri)
        bucket.mkdir(parents=True, exist_ok=True, mode=0o700)
        target = bucket / digest
        if target.exists():
            existing = await asyncio.to_thread(target.read_bytes)
            if existing != data:
                raise RuntimeError("immutable output URI collision")
            return
        await asyncio.to_thread(target.write_bytes, data)

    async def read(self, scope: RequestScope, uri: str) -> bytes | None:
        digest = hashlib.sha256(uri.encode()).hexdigest()
        target = self._bucket(scope, uri) / digest
        if not target.is_file():
            return None
        return await asyncio.to_thread(target.read_bytes)

    async def delete_presentation(self, scope: RequestScope, presentation_id: str) -> None:
        uri = f"office://presentations/{presentation_id}"
        bucket = self._bucket(scope, uri)
        if bucket.is_dir():
            await asyncio.to_thread(shutil.rmtree, bucket)
