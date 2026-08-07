"""Safe inline-HTML policy, stable element identity, and DOM utilities."""

import base64
import binascii
import io
import re
from collections.abc import Iterable
from typing import Any, cast
from urllib.parse import unquote_to_bytes, urlparse

import tinycss2
from bs4 import BeautifulSoup, Tag
from PIL import Image

from office_mcp.constants import MAX_HTML_BYTES, MAX_REMOTE_ASSET_BYTES
from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.ids import element_id
from office_mcp.models.element import ElementById, ElementByName, ElementSelector

ACTIVE_TAGS = {
    "script",
    "iframe",
    "object",
    "embed",
    "style",
    "link",
    "form",
    "base",
    "meta",
    "audio",
    "video",
}
URL_ATTRS = {"href", "src", "srcset", "action", "formaction", "poster", "xlink:href"}
CSS_PROPERTY = re.compile(r"^--?[a-zA-Z][a-zA-Z0-9-]*$|^[a-zA-Z][a-zA-Z0-9-]*$")
OFFICE_ID = re.compile(r"^el_[A-Za-z0-9_-]{8,}$")
MAX_IMAGE_PIXELS = 40_000_000
MAX_IMAGE_DIMENSION = 10_000


def _valid_data_image(value: str) -> bool:
    try:
        header, payload = value.split(",", 1)
        mime_type = header[5:].split(";", 1)[0].lower()
        expected = {
            "image/png": "PNG",
            "image/jpeg": "JPEG",
            "image/gif": "GIF",
            "image/webp": "WEBP",
        }.get(mime_type)
        if expected is None:
            return False
        data = (
            base64.b64decode(payload, validate=True)
            if ";base64" in header.lower()
            else unquote_to_bytes(payload)
        )
        if not data or len(data) > MAX_REMOTE_ASSET_BYTES:
            return False
        with Image.open(io.BytesIO(data)) as image:
            if image.format != expected:
                return False
            width, height = image.size
            if (
                width <= 0
                or height <= 0
                or width > MAX_IMAGE_DIMENSION
                or height > MAX_IMAGE_DIMENSION
                or width * height > MAX_IMAGE_PIXELS
            ):
                return False
            image.verify()
        return True
    except (ValueError, binascii.Error, OSError, Image.DecompressionBombError):
        return False


def _unsafe_url(tag_name: str, attribute: str, value: str) -> bool:
    stripped = re.sub(r"[\x00-\x20]+", "", value)
    if attribute == "srcset":
        return True
    if stripped.startswith("#"):
        return False
    parsed = urlparse(stripped)
    if attribute == "href" and tag_name == "a":
        return parsed.scheme.lower() not in {"https", "mailto"}
    return parsed.scheme.lower() != "data" or not _valid_data_image(stripped)


def _css_urls(tokens: list[Any]) -> Iterable[str]:
    for token in tokens:
        token_type = getattr(token, "type", "")
        if token_type == "url":
            yield str(token.value)
        elif token_type == "function":
            if token.lower_name == "url":
                yield tinycss2.serialize(token.arguments).strip().strip("\"'")
            else:
                yield from _css_urls(cast(list[Any], token.arguments))
        content = getattr(token, "content", None)
        if isinstance(content, list):
            yield from _css_urls(cast(list[Any], content))


def parse_styles(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for declaration in tinycss2.parse_declaration_list(
        value, skip_whitespace=True, skip_comments=True
    ):
        if declaration.type == "error":
            raise OfficeError(ErrorCode.UNSUPPORTED_CSS, "style declaration is invalid")
        if declaration.type != "declaration":
            continue
        name = declaration.lower_name
        rendered = tinycss2.serialize(declaration.value).strip()
        if not CSS_PROPERTY.fullmatch(name):
            raise OfficeError(ErrorCode.UNSUPPORTED_CSS, f"invalid CSS property {name!r}")
        for url in _css_urls(declaration.value):
            normalized = re.sub(r"[\x00-\x20]+", "", url)
            if not (normalized.startswith("#") or _valid_data_image(normalized)):
                raise OfficeError(ErrorCode.UNSAFE_HTML, f"unsafe CSS URL in {name}")
        result[name] = rendered
    return result


def serialize_styles(styles: dict[str, str]) -> str:
    return ";".join(f"{name}:{value}" for name, value in sorted(styles.items()))


def sanitize_fragment(
    html: str,
    *,
    exactly_one_root: bool = False,
    max_bytes: int = MAX_HTML_BYTES,
    _preserve_office_ids: bool = False,
    _preserve_domoxml_metadata: bool = False,
) -> tuple[str, list[str]]:
    if len(html.encode("utf-8")) > max_bytes:
        raise OfficeError(ErrorCode.RESOURCE_TOO_LARGE, "slide HTML exceeds the byte limit")
    if "\x00" in html:
        raise OfficeError(ErrorCode.INVALID_HTML, "null bytes are not allowed")
    soup = BeautifulSoup(html, "html.parser")
    roots = [child for child in soup.contents if isinstance(child, Tag)]
    if not roots:
        raise OfficeError(ErrorCode.INVALID_HTML, "HTML must contain at least one element")
    if exactly_one_root and len(roots) != 1:
        raise OfficeError(ErrorCode.INVALID_HTML, "exactly one root element is required")
    assigned: list[str] = []
    seen_ids: set[str] = set()
    for tag in soup.find_all(True):
        name = tag.name.lower()
        if name in ACTIVE_TAGS:
            raise OfficeError(ErrorCode.UNSAFE_HTML, f"<{name}> is not allowed")
        for attr in list(tag.attrs):
            lowered = attr.lower()
            value = tag.attrs[attr]
            text_value = " ".join(value) if isinstance(value, list) else str(value)
            if lowered.startswith("on"):
                raise OfficeError(
                    ErrorCode.UNSAFE_HTML, f"event-handler attribute {attr!r} is not allowed"
                )
            if lowered == "data-office-id" and not _preserve_office_ids:
                del tag.attrs[attr]
                continue
            if lowered.startswith("data-domoxml-") and not _preserve_domoxml_metadata:
                del tag.attrs[attr]
                continue
            if lowered == "data-office-id" and (
                not OFFICE_ID.fullmatch(text_value) or text_value in seen_ids
            ):
                raise OfficeError(
                    ErrorCode.INVALID_HTML, "invalid or duplicate internal element ID"
                )
            if lowered == "data-office-id":
                seen_ids.add(text_value)
            if lowered in URL_ATTRS and _unsafe_url(name, lowered, text_value):
                raise OfficeError(ErrorCode.UNSAFE_HTML, f"unsafe URL scheme in {attr!r}")
            if lowered == "style":
                tag.attrs[attr] = serialize_styles(parse_styles(text_value))
            if lowered == "class":
                del tag.attrs[attr]
        if not (_preserve_office_ids and tag.has_attr("data-office-id")):
            new_id = element_id()
            tag.attrs["data-office-id"] = new_id
            assigned.append(new_id)
    return str(soup), assigned


def remint_ids(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        tag.attrs["data-office-id"] = element_id()
    return str(soup)


def visible_text(html: str) -> str:
    return " ".join(BeautifulSoup(html, "html.parser").stripped_strings)


def model_facing_html(html: str) -> str:
    """Remove domOXML's private preservation payloads from model-visible source."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        for attribute in list(tag.attrs):
            if attribute.lower().startswith("data-domoxml-"):
                del tag.attrs[attribute]
    return str(soup)


def detach_domoxml_metadata(tag: Tag) -> None:
    """Invalidate stale imported semantic payloads on an edited node and its ancestors."""
    current: Tag | None = tag
    while current is not None:
        for attribute in list(current.attrs):
            if attribute.lower().startswith("data-domoxml-"):
                del current.attrs[attribute]
        current = current.parent if isinstance(current.parent, Tag) else None


def element_tags(html: str) -> list[Tag]:
    return list(BeautifulSoup(html, "html.parser").find_all(True))


def select_element(soup: BeautifulSoup, selector: ElementSelector) -> Tag:
    if isinstance(selector, ElementById):
        match = soup.find(attrs=cast(Any, {"data-office-id": selector.element_id}))
        if not isinstance(match, Tag):
            raise OfficeError(ErrorCode.ELEMENT_NOT_FOUND, "element was not found")
        return match
    assert isinstance(selector, ElementByName)
    matches = soup.find_all(attrs=cast(Any, {"data-office-name": selector.element_name}))
    if not matches:
        raise OfficeError(ErrorCode.ELEMENT_NOT_FOUND, "element was not found")
    if len(matches) > 1:
        raise OfficeError(
            ErrorCode.AMBIGUOUS_ELEMENT_NAME,
            f"{len(matches)} elements are named {selector.element_name!r}. "
            "Inspect the slide structure and use an element_id.",
        )
    return matches[0]


def direct_child_ids(tag: Tag) -> list[str]:
    return [
        str(child["data-office-id"])
        for child in tag.children
        if isinstance(child, Tag) and child.has_attr("data-office-id")
    ]


def descendants_with_depth(tag: Tag, depth: int) -> Iterable[Tag]:
    yield tag
    if depth <= 0:
        return
    for child in tag.children:
        if isinstance(child, Tag):
            yield from descendants_with_depth(child, depth - 1)
