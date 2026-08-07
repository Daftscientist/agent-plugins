"""Slide request and response models."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .base import ElementId, PresentationId, RevisionId, SlideId, StrictModel
from .common import Activity, SlideSize, SlideTransition
from .presentation import NewSlide, SlideRef


class InsertStart(StrictModel):
    type: Literal["start"] = "start"


class InsertEnd(StrictModel):
    type: Literal["end"] = "end"


class InsertBefore(StrictModel):
    type: Literal["before"] = "before"
    slide_id: SlideId


class InsertAfter(StrictModel):
    type: Literal["after"] = "after"
    slide_id: SlideId


SlideInsertionPosition = Annotated[
    InsertStart | InsertEnd | InsertBefore | InsertAfter, Field(discriminator="type")
]


class SlideAddArgs(StrictModel):
    presentation_id: PresentationId
    expected_revision: RevisionId | None = None
    slides: list[NewSlide] = Field(min_length=1, max_length=50)
    position: SlideInsertionPosition = Field(default_factory=InsertEnd)
    activity: Activity | None = None


class SlideAddResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    added: list[SlideRef]
    slide_count: int


class SlideInspectDetail(StrEnum):
    SUMMARY = "summary"
    STRUCTURE = "structure"
    SOURCE = "source"


class SlideInspectArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    revision: RevisionId | None = None
    detail: SlideInspectDetail = SlideInspectDetail.STRUCTURE


class SlideSummary(StrictModel):
    slide_id: SlideId
    number: int
    name: str
    description: str | None
    transition: SlideTransition | None
    size: SlideSize | None
    element_count: int


class ElementStructureNode(StrictModel):
    element_id: ElementId
    element_name: str | None
    tag: str
    text: str | None
    child_ids: list[ElementId]


class SlideInspectResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    summary: SlideSummary
    structure: list[ElementStructureNode] | None = None
    html: str | None = None


class SlideUpdateArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    expected_revision: RevisionId | None = None
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=240)
    transition: SlideTransition | None = None
    size: SlideSize | None = None
    html: str | None = None
    activity: Activity | None = None

    @model_validator(mode="after")
    def has_patch(self) -> "SlideUpdateArgs":
        if not ({"name", "description", "transition", "size", "html"} & self.model_fields_set):
            raise ValueError("at least one mutable field must be supplied")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("slide name cannot be cleared")
        return self


class SlideDuplicateArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    expected_revision: RevisionId | None = None
    name: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=240)
    position: SlideInsertionPosition | None = None
    activity: Activity | None = None


class SlideDuplicateResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slide: SlideRef


class SlideDeleteArgs(StrictModel):
    presentation_id: PresentationId
    slide_ids: list[SlideId] = Field(min_length=1, max_length=100)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None

    @model_validator(mode="after")
    def unique_ids(self) -> "SlideDeleteArgs":
        if len(set(self.slide_ids)) != len(self.slide_ids):
            raise ValueError("duplicate slide IDs are not allowed")
        return self


class SlideDeleteResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    deleted_slide_ids: list[SlideId]
    slide_count: int


class SlideReorderArgs(StrictModel):
    presentation_id: PresentationId
    slide_ids: list[SlideId] = Field(min_length=1, max_length=500)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None


class SlideReorderResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slides: list[SlideRef]
