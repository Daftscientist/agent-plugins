"""Bounded URI input resolvers with SSRF and local containment defenses."""

import asyncio
import base64
import binascii
import ipaddress
import socket
from pathlib import Path
from urllib.parse import unquote, unquote_to_bytes, urljoin, urlparse

import httpx

from office_mcp.config import OfficeConfig
from office_mcp.errors import ErrorCode, OfficeError


def forbidden_address(address: str) -> bool:
    ip = ipaddress.ip_address(address)
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


async def _validated_addresses(host: str, port: int) -> list[str]:
    normalized_host = host.rstrip(".").lower()
    if normalized_host == "localhost" or normalized_host.endswith(
        (".localhost", ".local", ".internal")
    ):
        raise OfficeError(ErrorCode.INVALID_PRESENTATION_SOURCE, "source host is not permitted")
    try:
        records = await asyncio.to_thread(socket.getaddrinfo, host, port, 0, socket.SOCK_STREAM)
    except OSError as exc:
        raise OfficeError(
            ErrorCode.INVALID_PRESENTATION_SOURCE, "source host could not be resolved"
        ) from exc
    addresses = list(dict.fromkeys(str(record[4][0]) for record in records))
    if not addresses or any(forbidden_address(address) for address in addresses):
        raise OfficeError(ErrorCode.INVALID_PRESENTATION_SOURCE, "source host is not permitted")
    return addresses


class DataUriResolver:
    def __init__(self, maximum: int) -> None:
        self.maximum = maximum

    async def resolve(self, uri: str) -> bytes:
        try:
            header, encoded = uri.split(",", 1)
        except ValueError as exc:
            raise OfficeError(ErrorCode.INVALID_PRESENTATION_SOURCE, "malformed data URI") from exc
        if not header.lower().startswith("data:"):
            raise OfficeError(ErrorCode.UNSUPPORTED_SOURCE_SCHEME, "expected a data URI")
        try:
            data = (
                base64.b64decode(encoded, validate=True)
                if ";base64" in header.lower()
                else unquote_to_bytes(encoded)
            )
        except (ValueError, binascii.Error) as exc:
            raise OfficeError(
                ErrorCode.INVALID_PRESENTATION_SOURCE, "data URI payload is invalid"
            ) from exc
        if len(data) > self.maximum:
            raise OfficeError(
                ErrorCode.SOURCE_TOO_LARGE, "presentation source exceeds the configured byte limit"
            )
        return data


class FileUriResolver:
    def __init__(self, config: OfficeConfig) -> None:
        self.config = config

    async def resolve(self, uri: str) -> bytes:
        if not self.config.allow_file_input or not self.config.allowed_file_roots:
            raise OfficeError(ErrorCode.UNSUPPORTED_SOURCE_SCHEME, "file: input is disabled")
        parsed = urlparse(uri)
        if parsed.netloc not in {"", "localhost"}:
            raise OfficeError(
                ErrorCode.INVALID_PRESENTATION_SOURCE, "remote file authorities are not allowed"
            )
        if "\x00" in parsed.path:
            raise OfficeError(ErrorCode.INVALID_PRESENTATION_SOURCE, "invalid local path")
        try:
            path = Path(unquote(parsed.path)).resolve(strict=True)
        except OSError as exc:
            raise OfficeError(
                ErrorCode.INVALID_PRESENTATION_SOURCE, "local source does not exist"
            ) from exc
        if not any(path.is_relative_to(root) for root in self.config.allowed_file_roots):
            raise OfficeError(
                ErrorCode.INVALID_PRESENTATION_SOURCE, "local path is outside configured roots"
            )
        if not path.is_file():
            raise OfficeError(
                ErrorCode.INVALID_PRESENTATION_SOURCE, "local source is not a regular file"
            )
        if path.stat().st_size > self.config.max_pptx_bytes:
            raise OfficeError(
                ErrorCode.SOURCE_TOO_LARGE, "presentation source exceeds the configured byte limit"
            )
        return await asyncio.to_thread(path.read_bytes)


class HttpsUriResolver:
    def __init__(self, config: OfficeConfig) -> None:
        self.config = config

    async def resolve(self, uri: str) -> bytes:
        if not self.config.allow_https_input:
            raise OfficeError(ErrorCode.UNSUPPORTED_SOURCE_SCHEME, "https: input is disabled")
        current = uri
        async with httpx.AsyncClient(
            timeout=20.0, follow_redirects=False, trust_env=False
        ) as client:
            for _ in range(4):
                parsed = urlparse(current)
                if (
                    parsed.scheme != "https"
                    or not parsed.hostname
                    or parsed.username
                    or parsed.password
                ):
                    raise OfficeError(
                        ErrorCode.INVALID_PRESENTATION_SOURCE,
                        "only credential-free HTTPS sources are allowed",
                    )
                port = parsed.port or 443
                address = (await _validated_addresses(parsed.hostname, port))[0]
                # Connect to the validated address, while retaining the
                # original hostname for HTTP Host and TLS SNI/certificate
                # verification.  This closes the DNS-rebinding window between
                # validation and connection.
                authority = f"[{address}]" if ":" in address else address
                if port != 443:
                    authority = f"{authority}:{port}"
                pinned = parsed._replace(netloc=authority).geturl()
                host_header = parsed.hostname if port == 443 else f"{parsed.hostname}:{port}"
                try:
                    stream = client.stream(
                        "GET",
                        pinned,
                        headers={
                            "Host": host_header,
                            "Accept": (
                                "application/vnd.openxmlformats-officedocument."
                                "presentationml.presentation, application/octet-stream"
                            ),
                        },
                        extensions={"sni_hostname": parsed.hostname},
                    )
                    async with stream as response:
                        if response.status_code in {301, 302, 303, 307, 308}:
                            location = response.headers.get("location")
                            if not location:
                                raise OfficeError(
                                    ErrorCode.INVALID_PRESENTATION_SOURCE,
                                    "source redirect has no destination",
                                )
                            current = urljoin(current, location)
                            continue
                        response.raise_for_status()
                        content_length = response.headers.get("content-length")
                        if content_length:
                            try:
                                declared_size = int(content_length)
                            except ValueError as exc:
                                raise OfficeError(
                                    ErrorCode.INVALID_PRESENTATION_SOURCE,
                                    "HTTPS source returned an invalid content length",
                                ) from exc
                            if declared_size > self.config.max_pptx_bytes:
                                raise OfficeError(
                                    ErrorCode.SOURCE_TOO_LARGE,
                                    "presentation source exceeds the configured byte limit",
                                )
                        result = bytearray()
                        async for chunk in response.aiter_bytes():
                            result.extend(chunk)
                            if len(result) > self.config.max_pptx_bytes:
                                raise OfficeError(
                                    ErrorCode.SOURCE_TOO_LARGE,
                                    "presentation source exceeds the configured byte limit",
                                )
                        return bytes(result)
                except OfficeError:
                    raise
                except httpx.HTTPError as exc:
                    raise OfficeError(
                        ErrorCode.INVALID_PRESENTATION_SOURCE,
                        "HTTPS source could not be fetched",
                    ) from exc
        raise OfficeError(ErrorCode.INVALID_PRESENTATION_SOURCE, "too many HTTPS redirects")


class CompositeInputResolver:
    def __init__(self, config: OfficeConfig) -> None:
        self._resolvers = {
            "data": DataUriResolver(config.max_pptx_bytes),
            "file": FileUriResolver(config),
            "https": HttpsUriResolver(config),
        }

    async def resolve(self, uri: str) -> bytes:
        scheme = urlparse(uri).scheme.lower()
        resolver = self._resolvers.get(scheme)
        if resolver is None:
            raise OfficeError(
                ErrorCode.UNSUPPORTED_SOURCE_SCHEME,
                f"unsupported source scheme {scheme or '(none)'!r}",
            )
        return await resolver.resolve(uri)
