"""Validation request and result models."""

from enum import StrEnum

from pydantic import Field

from .base import PresentationId, RevisionId, SlideId, StrictModel
from .common import Editability, Representation, SourceRetention


class ValidationDetail(StrEnum):
    SUMMARY = "summary"
    FULL = "full"


class PresentationValidateArgs(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId | None = None
    slide_ids: list[SlideId] | None = None
    detail: ValidationDetail = ValidationDetail.SUMMARY


class CoverageItem(StrictModel):
    slide_id: SlideId
    element: str
    representation: Representation
    editability: Editability
    source_retention: SourceRetention
    output_count: int = Field(ge=0)
    raster_area_emu2: int = Field(ge=0)
    reason: str


class ValidationWarning(StrictModel):
    code: str
    message: str
    slide_id: SlideId | None = None
    element: str | None = None


class PresentationValidationResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    valid: bool
    slide_count: int
    native_ratio: float = Field(ge=0, le=1)
    editable_ratio: float = Field(ge=0, le=1)
    layered_ratio: float = Field(ge=0, le=1)
    warning_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)
    warnings: list[ValidationWarning]
    coverage: list[CoverageItem] | None = None
