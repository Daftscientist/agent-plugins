"""Persisted immutable presentation snapshot models."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from office_mcp.models.common import PresentationTheme, SlideSize, SlideTransition


def now_utc() -> datetime:
    return datetime.now(UTC)


class StoredSlide(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slide_id: str
    name: str
    description: str | None = None
    html: str
    transition: SlideTransition | None = None
    size: SlideSize | None = None


class PresentationSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    presentation_id: str
    revision_id: str
    parent_revision_id: str | None = None
    name: str
    description: str | None = None
    size: SlideSize
    theme: PresentationTheme
    slides: list[StoredSlide] = Field(default_factory=lambda: [])
    created_at: datetime
    updated_at: datetime
    imported_pptx_b64: str | None = None
    imported_preservation: list[dict[str, object]] = Field(default_factory=lambda: [])
    import_warnings: list[dict[str, object]] = Field(default_factory=lambda: [])
    content_changed_after_import: bool = False
