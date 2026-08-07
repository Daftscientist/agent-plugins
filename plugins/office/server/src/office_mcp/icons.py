"""Self-contained light/dark MCP icon metadata."""

import base64

from mcp_types import Icon


def _svg(label: str, foreground: str, background: str) -> str:
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="14" fill="{background}"/>'
        f'<text x="32" y="42" text-anchor="middle" font-family="Arial" font-size="30" '
        f'font-weight="700" fill="{foreground}">{label}</text></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


OFFICE_ICONS: list[Icon] = [
    Icon(src=_svg("O", "#ffffff", "#d24726"), mime_type="image/svg+xml", theme="light"),
    Icon(src=_svg("O", "#ffffff", "#9f351d"), mime_type="image/svg+xml", theme="dark"),
]
PRESENTATION_ICONS: list[Icon] = [
    Icon(src=_svg("P", "#ffffff", "#d24726"), mime_type="image/svg+xml")
]
SLIDE_ICONS: list[Icon] = [Icon(src=_svg("S", "#ffffff", "#7c3aed"), mime_type="image/svg+xml")]
ELEMENT_ICONS: list[Icon] = [Icon(src=_svg("E", "#ffffff", "#2563eb"), mime_type="image/svg+xml")]
PREVIEW_ICONS: list[Icon] = [Icon(src=_svg("◉", "#ffffff", "#059669"), mime_type="image/svg+xml")]
VALIDATE_ICONS: list[Icon] = [Icon(src=_svg("✓", "#ffffff", "#0891b2"), mime_type="image/svg+xml")]
EXPORT_ICONS: list[Icon] = [Icon(src=_svg("↗", "#ffffff", "#475569"), mime_type="image/svg+xml")]
