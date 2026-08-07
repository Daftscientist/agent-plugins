import base64
import io
import zipfile
from pathlib import Path
from typing import Any, ClassVar

import pytest
from pptx import Presentation

from office_mcp.config import OfficeConfig
from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.inputs.pptx import validate_pptx
from office_mcp.inputs.resolver import (
    CompositeInputResolver,
    HttpsUriResolver,
    forbidden_address,
    validated_addresses,
)


def pptx_bytes() -> bytes:
    buffer = io.BytesIO()
    Presentation().save(buffer)
    return buffer.getvalue()


@pytest.mark.parametrize("address", ["127.0.0.1", "10.0.0.1", "169.254.169.254", "::1", "0.0.0.0"])
def test_private_and_metadata_addresses_are_forbidden(address: str) -> None:
    assert forbidden_address(address)


async def test_data_uri_is_portable_and_bounded(tmp_path: Path) -> None:
    data = pptx_bytes()
    resolver = CompositeInputResolver(OfficeConfig(data_dir=tmp_path, max_pptx_bytes=len(data)))
    uri = (
        "data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,"
        + base64.b64encode(data).decode()
    )
    assert await resolver.resolve(uri) == data
    too_small = CompositeInputResolver(OfficeConfig(data_dir=tmp_path, max_pptx_bytes=1))
    with pytest.raises(OfficeError) as error:
        await too_small.resolve(uri)
    assert error.value.code is ErrorCode.SOURCE_TOO_LARGE


async def test_file_input_defaults_off_and_blocks_symlink_escape(tmp_path: Path) -> None:
    source = tmp_path / "deck.pptx"
    source.write_bytes(pptx_bytes())
    disabled = CompositeInputResolver(OfficeConfig(data_dir=tmp_path))
    with pytest.raises(OfficeError):
        await disabled.resolve(source.as_uri())
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    link = allowed / "escape.pptx"
    link.symlink_to(source)
    enabled = CompositeInputResolver(
        OfficeConfig(
            data_dir=tmp_path, allow_file_input=True, allowed_file_roots=(allowed.resolve(),)
        )
    )
    with pytest.raises(OfficeError):
        await enabled.resolve(link.as_uri())
    with pytest.raises(OfficeError):
        await disabled.resolve("file:///etc/passwd")
    with pytest.raises(OfficeError):
        await enabled.resolve("file:///C:/Windows/System32/config/SAM")
    with pytest.raises(OfficeError):
        await enabled.resolve("file:///tmp/bad%00name")


async def test_dns_resolution_rejects_any_private_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    def private_dns(*_args: object) -> list[tuple[int, int, int, str, tuple[str, int]]]:
        return [(2, 1, 6, "", ("169.254.169.254", 443))]

    monkeypatch.setattr("office_mcp.inputs.resolver.socket.getaddrinfo", private_dns)
    with pytest.raises(OfficeError):
        await validated_addresses("metadata.example", 443)


async def test_https_redirect_is_revalidated_and_connection_is_dns_pinned(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import office_mcp.inputs.resolver as resolver_module

    seen_hosts: list[str] = []
    seen_requests: list[tuple[str, dict[str, Any]]] = []

    async def addresses(host: str, _port: int) -> list[str]:
        seen_hosts.append(host)
        if host == "127.0.0.1":
            raise OfficeError(ErrorCode.INVALID_PRESENTATION_SOURCE, "private")
        return ["93.184.216.34"]

    class RedirectResponse:
        status_code = 302
        headers: ClassVar[dict[str, str]] = {"location": "https://127.0.0.1/metadata"}

        async def __aenter__(self) -> "RedirectResponse":
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

    class FakeClient:
        def __init__(self, **_kwargs: object) -> None:
            pass

        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        def stream(self, _method: str, url: str, **kwargs: Any) -> RedirectResponse:
            seen_requests.append((url, kwargs))
            return RedirectResponse()

    monkeypatch.setattr(resolver_module, "validated_addresses", addresses)
    monkeypatch.setattr(resolver_module.httpx, "AsyncClient", FakeClient)
    resolver = HttpsUriResolver(OfficeConfig(data_dir=tmp_path, allow_https_input=True))
    with pytest.raises(OfficeError):
        await resolver.resolve("https://example.com/deck.pptx")
    assert seen_hosts == ["example.com", "127.0.0.1"]
    assert seen_requests[0][0].startswith("https://93.184.216.34/")
    assert seen_requests[0][1]["headers"]["Host"] == "example.com"
    assert seen_requests[0][1]["extensions"]["sni_hostname"] == "example.com"


def test_pptx_magic_content_type_and_zip_safety() -> None:
    config = OfficeConfig(data_dir=Path("."))
    validate_pptx(pptx_bytes(), config)
    with pytest.raises(OfficeError):
        validate_pptx(b"not a zip", config)


def unsafe_relationship_package(target: str, target_mode: str = "External") -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as package:
        package.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Override PartName="/ppt/presentation.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'presentationml.presentation.main+xml"/></Types>',
        )
        package.writestr(
            "ppt/presentation.xml",
            '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>',
        )
        package.writestr(
            "ppt/_rels/presentation.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="x" Target="{target}" '
            f'TargetMode="{target_mode}"/>'
            "</Relationships>",
        )
    return buffer.getvalue()


def test_pptx_rejects_dangerous_external_relationships() -> None:
    config = OfficeConfig(data_dir=Path("."))
    with pytest.raises(OfficeError) as error:
        validate_pptx(unsafe_relationship_package("file:///etc/passwd"), config)
    assert error.value.code is ErrorCode.INVALID_PPTX
    validate_pptx(unsafe_relationship_package("https://example.com"), config)


def test_pptx_rejects_relationships_escaping_package_namespace() -> None:
    with pytest.raises(OfficeError):
        validate_pptx(
            unsafe_relationship_package("../../../../etc/passwd", "Internal"),
            OfficeConfig(data_dir=Path(".")),
        )


def test_pptx_rejects_duplicate_normalized_paths() -> None:
    data = pptx_bytes()
    source = zipfile.ZipFile(io.BytesIO(data))
    buffer = io.BytesIO()
    with source, zipfile.ZipFile(buffer, "w") as package:
        for member in source.infolist():
            package.writestr(member, source.read(member.filename))
        package.writestr("ppt/./presentation.xml", source.read("ppt/presentation.xml"))
    with pytest.raises(OfficeError):
        validate_pptx(buffer.getvalue(), OfficeConfig(data_dir=Path(".")))


def test_pptx_rejects_zip_bombs_and_xxe() -> None:
    config = OfficeConfig(data_dir=Path("."))
    bomb = io.BytesIO()
    with zipfile.ZipFile(bomb, "w", compression=zipfile.ZIP_DEFLATED) as package:
        package.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Override PartName="/ppt/presentation.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'presentationml.presentation.main+xml"/></Types>',
        )
        package.writestr("ppt/presentation.xml", "<presentation/>")
        package.writestr("ppt/media/bomb.bin", b"0" * 2_000_000)
    with pytest.raises(OfficeError):
        validate_pptx(bomb.getvalue(), config)

    xxe = io.BytesIO()
    with zipfile.ZipFile(xxe, "w") as package:
        package.writestr(
            "[Content_Types].xml",
            '<!DOCTYPE x [<!ENTITY secret SYSTEM "file:///etc/passwd">]>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Override PartName="/ppt/presentation.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'presentationml.presentation.main+xml"/>&secret;</Types>',
        )
        package.writestr("ppt/presentation.xml", "<presentation/>")
    with pytest.raises(OfficeError) as error:
        validate_pptx(xxe.getvalue(), config)
    assert error.value.code is ErrorCode.INVALID_PPTX
