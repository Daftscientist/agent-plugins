"""Runtime configuration with secure defaults."""

import os
from dataclasses import dataclass
from pathlib import Path

from .constants import MAX_DECOMPRESSED_BYTES, MAX_HTML_BYTES, MAX_PPTX_BYTES


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class OfficeConfig:
    data_dir: Path
    allow_file_input: bool = False
    allowed_file_roots: tuple[Path, ...] = ()
    allow_https_input: bool = False
    max_pptx_bytes: int = MAX_PPTX_BYTES
    max_decompressed_bytes: int = MAX_DECOMPRESSED_BYTES
    max_html_bytes: int = MAX_HTML_BYTES
    operation_timeout_seconds: float = 120.0
    max_render_concurrency: int = 2
    cursor_secret: bytes = b""

    @classmethod
    def from_env(cls) -> "OfficeConfig":
        data = Path(os.getenv("OFFICE_DATA_DIR", "./.office-data")).expanduser().resolve()
        roots = tuple(
            Path(item).expanduser().resolve()
            for item in os.getenv("OFFICE_ALLOWED_FILE_ROOTS", "").split(os.pathsep)
            if item
        )
        secret = os.getenv("OFFICE_CURSOR_SECRET", "").encode()
        return cls(
            data_dir=data,
            allow_file_input=_bool("OFFICE_ALLOW_FILE_INPUT"),
            allowed_file_roots=roots,
            allow_https_input=_bool("OFFICE_ALLOW_HTTPS_INPUT"),
            cursor_secret=secret,
        )

    def prepare(self) -> None:
        for child in ("revisions", "assets", "previews", "exports", "temp", "runtime"):
            path = self.data_dir / child
            path.mkdir(parents=True, exist_ok=True, mode=0o700)
