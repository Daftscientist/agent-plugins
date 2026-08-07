"""Untrusted PPTX ZIP/package validation."""

import io
import posixpath
import zipfile
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

from defusedxml.common import DefusedXmlException
from defusedxml.ElementTree import fromstring

from office_mcp.config import OfficeConfig
from office_mcp.constants import MAX_REMOTE_ASSET_BYTES, MAX_ZIP_ENTRIES
from office_mcp.errors import ErrorCode, OfficeError


def validate_pptx(data: bytes, config: OfficeConfig) -> None:
    if len(data) > config.max_pptx_bytes:
        raise OfficeError(
            ErrorCode.SOURCE_TOO_LARGE, "presentation source exceeds the configured byte limit"
        )
    if not data.startswith(b"PK"):
        raise OfficeError(ErrorCode.INVALID_PPTX, "source is not an OOXML ZIP package")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as package:
            members = package.infolist()
            if len(members) > MAX_ZIP_ENTRIES:
                raise OfficeError(ErrorCode.INVALID_PPTX, "PPTX contains too many package entries")
            total = 0
            names: set[str] = set()
            normalized_names: set[str] = set()
            for member in members:
                normalized = posixpath.normpath(member.filename.replace("\\", "/"))
                if (
                    normalized.startswith("../")
                    or normalized.startswith("/")
                    or "\x00" in normalized
                ):
                    raise OfficeError(
                        ErrorCode.INVALID_PPTX, "PPTX contains an unsafe package path"
                    )
                if normalized in normalized_names:
                    raise OfficeError(
                        ErrorCode.INVALID_PPTX, "PPTX contains duplicate package paths"
                    )
                normalized_names.add(normalized)
                if member.flag_bits & 0x1:
                    raise OfficeError(
                        ErrorCode.INVALID_PPTX, "encrypted PPTX parts are unsupported"
                    )
                total += member.file_size
                if total > config.max_decompressed_bytes:
                    raise OfficeError(
                        ErrorCode.INVALID_PPTX, "PPTX exceeds the decompressed byte limit"
                    )
                if member.compress_size and member.file_size / member.compress_size > 1000:
                    raise OfficeError(
                        ErrorCode.INVALID_PPTX, "PPTX contains a suspicious compression ratio"
                    )
                if (
                    normalized.startswith("ppt/media/")
                    and member.file_size > MAX_REMOTE_ASSET_BYTES
                ):
                    raise OfficeError(
                        ErrorCode.INVALID_PPTX, "PPTX contains an oversized media part"
                    )
                names.add(member.filename)
            required = {"[Content_Types].xml", "ppt/presentation.xml"}
            if not required.issubset(names):
                raise OfficeError(
                    ErrorCode.INVALID_PPTX, "source is not a PowerPoint OOXML package"
                )
            content_types = package.read("[Content_Types].xml")
            root = fromstring(content_types)
            content_type_values = [node.attrib.get("ContentType", "") for node in root]
            if any(
                marker in value.lower()
                for value in content_type_values
                for marker in ("macroenabled", "vbaproject", "activex")
            ):
                raise OfficeError(
                    ErrorCode.INVALID_PPTX, "macro-enabled or active content is unsupported"
                )
            expected = (
                "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
            )
            if not any(node.attrib.get("ContentType") == expected for node in root):
                macro = any("macroenabled" in value.lower() for value in content_type_values)
                message = (
                    "macro-enabled presentations are unsupported"
                    if macro
                    else "PowerPoint content type is missing"
                )
                raise OfficeError(ErrorCode.INVALID_PPTX, message)
            for name in names:
                if name.endswith((".xml", ".rels")):
                    payload = package.read(name)
                    if len(payload) > 20 * 1024 * 1024:
                        raise OfficeError(
                            ErrorCode.INVALID_PPTX, "PPTX XML part exceeds the byte limit"
                        )
                    part = fromstring(payload)
                    if name.endswith(".rels"):
                        for relationship in part:
                            target = relationship.attrib.get("Target", "")
                            if relationship.attrib.get("TargetMode") != "External":
                                parsed = urlparse(target)
                                if (
                                    parsed.scheme
                                    or parsed.netloc
                                    or "\\" in target
                                    or "\x00" in target
                                ):
                                    raise OfficeError(
                                        ErrorCode.INVALID_PPTX,
                                        "PPTX contains an unsafe internal relationship",
                                    )
                                if "/_rels/" in name:
                                    prefix, relation_name = name.rsplit("/_rels/", 1)
                                    source_part = f"{prefix}/{relation_name.removesuffix('.rels')}"
                                    base = posixpath.dirname(source_part)
                                else:
                                    base = ""
                                resolved = posixpath.normpath(
                                    posixpath.join(base, unquote(parsed.path))
                                )
                                if resolved.startswith("../") or resolved.startswith("/"):
                                    raise OfficeError(
                                        ErrorCode.INVALID_PPTX,
                                        "PPTX relationship escapes the package namespace",
                                    )
                                continue
                            parsed = urlparse(target)
                            if parsed.scheme.lower() not in {"http", "https", "mailto"}:
                                raise OfficeError(
                                    ErrorCode.INVALID_PPTX,
                                    "PPTX contains an unsafe external relationship",
                                )
    except OfficeError:
        raise
    except (
        zipfile.BadZipFile,
        KeyError,
        ElementTree.ParseError,
        DefusedXmlException,
        ValueError,
    ) as exc:
        raise OfficeError(
            ErrorCode.INVALID_PPTX, "source is not a valid safe PPTX package"
        ) from exc
