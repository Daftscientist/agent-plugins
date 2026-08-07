"""Scope/filter-bound opaque cursor encoding."""

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from office_mcp.errors import ErrorCode, OfficeError


class CursorCodec:
    def __init__(self, secret: bytes, ttl_seconds: int = 3600) -> None:
        self.secret = secret or secrets.token_bytes(32)
        self.ttl_seconds = ttl_seconds

    def encode(self, payload: dict[str, Any]) -> str:
        body = dict(payload, v=1, exp=int(time.time()) + self.ttl_seconds)
        encoded = base64.urlsafe_b64encode(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).rstrip(b"=")
        signature = hmac.new(self.secret, encoded, hashlib.sha256).digest()
        return f"{encoded.decode()}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"

    def decode(self, cursor: str) -> dict[str, Any]:
        try:
            encoded_text, signature_text = cursor.split(".", 1)
            encoded = encoded_text.encode()
            signature = base64.urlsafe_b64decode(signature_text + "=" * (-len(signature_text) % 4))
            expected = hmac.new(self.secret, encoded, hashlib.sha256).digest()
            if not hmac.compare_digest(signature, expected):
                raise ValueError
            payload = json.loads(
                base64.urlsafe_b64decode(encoded_text + "=" * (-len(encoded_text) % 4))
            )
            if payload.get("v") != 1 or int(payload["exp"]) < int(time.time()):
                raise ValueError
            return payload
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise OfficeError(
                ErrorCode.INVALID_PRESENTATION_SOURCE, "cursor is invalid or expired"
            ) from exc
