"""Presentation tool request and response models."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator, model_validator

from .base import PresentationId, RevisionId, SlideId, StrictModel
from .common import (
    Activity,
    ColorToken,
    FontToken,
    PresentationTheme,
    PresetSlideSize,
    SlideSize,
    SlideSizePreset,
    SlideTransition,
)


class PresentationSource(StrictModel):
    uri: str = Field(min_length=1)
    filename_hint: str | None = Field(default=None, max_length=255)


class NewSlide(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=240)
    html: str = Field(min_length=1)
    transition: SlideTransition | None = None
    size: SlideSize | None = None


class SlideRef(StrictModel):
    slide_id: SlideId
    number: int = Field(ge=1)
    name: str
    description: str | None = None


class PresentationCreateArgs(StrictModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=500)
    size: SlideSize = Field(
        default_factory=lambda: PresetSlideSize(preset=SlideSizePreset.WIDE_16_9)
    )
    theme: PresentationTheme = Field(default_factory=PresentationTheme)
    slides: list[NewSlide] = Field(default_factory=lambda: [], max_length=100)
    activity: Activity | None = None


class PresentationCreateResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    name: str
    slide_count: int = Field(ge=0)
    slides: list[SlideRef]
    resource_uri: str


class PresentationOpenArgs(StrictModel):
    source: PresentationSource
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=500)
    activity: Activity | None = None


class ImportWarning(StrictModel):
    code: str
    message: str
    slide_number: int | None = Field(default=None, ge=1)
    element: str | None = None


class PresentationOpenResult(PresentationCreateResult):
    warnings: list[ImportWarning]


class PresentationSearchField(StrEnum):
    NAME = "name"
    DESCRIPTION = "description"
    SLIDE_NAMES = "slide_names"
    SLIDE_DESCRIPTIONS = "slide_descriptions"
    SLIDE_TEXT = "slide_text"


class PresentationSearchSort(StrEnum):
    RELEVANCE = "relevance"
    UPDATED_DESC = "updated_desc"
    UPDATED_ASC = "updated_asc"
    CREATED_DESC = "created_desc"
    CREATED_ASC = "created_asc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"


class PresentationSearchArgs(StrictModel):
    query: str | None = Field(default=None, max_length=500)
    search_in: list[PresentationSearchField] = Field(
        default_factory=lambda: [
            PresentationSearchField.NAME,
            PresentationSearchField.DESCRIPTION,
            PresentationSearchField.SLIDE_NAMES,
            PresentationSearchField.SLIDE_TEXT,
        ],
        min_length=1,
    )
    created_after: datetime | None = None
    created_before: datetime | None = None
    updated_after: datetime | None = None
    updated_before: datetime | None = None
    sort: PresentationSearchSort = PresentationSearchSort.RELEVANCE
    limit: int = Field(default=20, ge=1, le=100)
    cursor: str | None = Field(default=None, max_length=2048)

    @field_validator("created_after", "created_before", "updated_after", "updated_before")
    @classmethod
    def utc_datetime(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def valid_ranges(self) -> "PresentationSearchArgs":
        if self.created_after and self.created_before and self.created_after > self.created_before:
            raise ValueError("created_after must not be later than created_before")
        if self.updated_after and self.updated_before and self.updated_after > self.updated_before:
            raise ValueError("updated_after must not be later than updated_before")
        return self


class PresentationSearchMatch(StrictModel):
    slide_id: SlideId | None = None
    slide_name: str | None = None
    snippet: str


class PresentationSearchItem(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    slide_count: int
    matches: list[PresentationSearchMatch]
    resource_uri: str


class PresentationSearchResult(StrictModel):
    items: list[PresentationSearchItem]
    next_cursor: str | None = None


class PresentationInspectDetail(StrEnum):
    SUMMARY = "summary"
    OUTLINE = "outline"


class PresentationInspectArgs(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId | None = None
    detail: PresentationInspectDetail = PresentationInspectDetail.OUTLINE


class PresentationInspectResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    name: str
    description: str | None
    size: SlideSize
    theme: PresentationTheme
    created_at: datetime
    updated_at: datetime
    slide_count: int
    preview_page_count: int
    slides: list[SlideRef]


class ThemePalettePatch(StrictModel):
    background: ColorToken | None = None
    foreground: ColorToken | None = None
    accent: ColorToken | None = None
    muted: ColorToken | None = None

    @model_validator(mode="after")
    def meaningful_patch(self) -> "ThemePalettePatch":
        if not self.model_fields_set:
            raise ValueError("palette patch must include at least one color")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("theme colors cannot be cleared")
        return self


class ThemeFontsPatch(StrictModel):
    heading: FontToken | None = None
    body: FontToken | None = None

    @model_validator(mode="after")
    def meaningful_patch(self) -> "ThemeFontsPatch":
        if not self.model_fields_set:
            raise ValueError("font patch must include at least one family")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("theme font families cannot be cleared")
        return self


class PresentationThemePatch(StrictModel):
    palette: ThemePalettePatch | None = None
    fonts: ThemeFontsPatch | None = None

    @model_validator(mode="after")
    def meaningful_patch(self) -> "PresentationThemePatch":
        if not self.model_fields_set:
            raise ValueError("theme patch must include palette or fonts")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("theme groups cannot be cleared")
        return self


class PresentationUpdateArgs(StrictModel):
    presentation_id: PresentationId
    expected_revision: RevisionId | None = None
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=500)
    size: SlideSize | None = None
    theme: PresentationThemePatch | None = None
    activity: Activity | None = None

    @model_validator(mode="after")
    def has_patch(self) -> "PresentationUpdateArgs":
        if not ({"name", "description", "size", "theme"} & self.model_fields_set):
            raise ValueError("at least one mutable field must be supplied")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("presentation name cannot be cleared")
        if "theme" in self.model_fields_set and self.theme is None:
            raise ValueError("presentation theme cannot be cleared")
        return self


class MutationResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId


class PresentationExportArgs(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId | None = None
    format: Literal["pptx"] = "pptx"
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    activity: Activity | None = None


class PresentationExportResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    filename: str
    mime_type: Literal["application/vnd.openxmlformats-officedocument.presentationml.presentation"]
    size_bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    resource_uri: str


class PresentationDeleteArgs(StrictModel):
    presentation_id: PresentationId
    expected_revision: RevisionId | None = None
    activity: Activity | None = None


class PresentationDeleteResult(StrictModel):
    presentation_id: PresentationId
    deleted: Literal[True] = True


class RevisionRef(StrictModel):
    presentation_id: PresentationId
    revision_id: RevisionId
