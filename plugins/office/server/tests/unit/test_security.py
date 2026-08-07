import base64
import io
import zipfile
from pathlib import Path

import pytest
from pptx import Presentation

from office_mcp.config import OfficeConfig
from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.inputs.pptx import validate_pptx
from office_mcp.inputs.resolver import CompositeInputResolver, forbidden_address


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


def test_pptx_magic_content_type_and_zip_safety() -> None:
    config = OfficeConfig(data_dir=Path("."))
    validate_pptx(pptx_bytes(), config)
    with pytest.raises(OfficeError):
        validate_pptx(b"not a zip", config)


def unsafe_relationship_package(target: str) -> bytes:
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
            f'<Relationship Id="rId1" Type="x" Target="{target}" TargetMode="External"/>'
            "</Relationships>",
        )
    return buffer.getvalue()


def test_pptx_rejects_dangerous_external_relationships() -> None:
    config = OfficeConfig(data_dir=Path("."))
    with pytest.raises(OfficeError) as error:
        validate_pptx(unsafe_relationship_package("file:///etc/passwd"), config)
    assert error.value.code is ErrorCode.INVALID_PPTX
    validate_pptx(unsafe_relationship_package("https://example.com"), config)


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
