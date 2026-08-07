"""Stable Office capabilities and protocol constants."""

from typing import Final

OFFICE_VERSION: Final = "0.1.0"
PPTX_MIME: Final = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
MAX_PPTX_BYTES: Final = 100 * 1024 * 1024
MAX_DECOMPRESSED_BYTES: Final = 500 * 1024 * 1024
MAX_ZIP_ENTRIES: Final = 20_000
MAX_HTML_BYTES: Final = 2 * 1024 * 1024
MAX_SLIDES: Final = 500
MAX_REMOTE_ASSET_BYTES: Final = 25 * 1024 * 1024
MAX_CONTACT_SHEET_SLIDES: Final = 30
SEARCH_PAGE_SIZE: Final = 100
RESOURCE_PAGE_SIZE: Final = 100
