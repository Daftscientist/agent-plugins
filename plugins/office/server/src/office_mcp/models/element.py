"""Element request and response models."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .base import ElementId, PresentationId, RevisionId, SlideId, StrictModel
from .common import Activity


class ElementById(StrictModel):
    type: Literal["id"] = "id"
    element_id: ElementId


class ElementByName(StrictModel):
    type: Literal["name"] = "name"
    element_name: str = Field(min_length=1, max_length=100)


ElementSelector = Annotated[ElementById | ElementByName, Field(discriminator="type")]


class ElementInspectArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    element: ElementSelector
    revision: RevisionId | None = None
    depth: int = Field(default=1, ge=0, le=10)
    include_html: bool = True
    include_styles: bool = True


class ElementInspectResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    slide_id: SlideId
    element_id: ElementId
    element_name: str | None
    tag: str
    text: str | None
    attributes: dict[str, str]
    styles: dict[str, str] | None
    html: str | None
    child_ids: list[ElementId]


class ElementInsertPosition(StrEnum):
    BEFORE = "before"
    AFTER = "after"
    PREPEND = "prepend"
    APPEND = "append"


class ElementAddArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    relative_to: ElementSelector
    position: ElementInsertPosition
    html: str = Field(min_length=1)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None


class AddedElement(StrictModel):
    element_id: ElementId
    element_name: str | None
    tag: str


class ElementAddResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slide_id: SlideId
    roots: list[AddedElement]


class StyleMutation(StrictModel):
    set: dict[str, str] = Field(default_factory=dict, max_length=100)
    remove: list[str] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def disjoint(self) -> "StyleMutation":
        overlap = {key.lower() for key in self.set} & {key.lower() for key in self.remove}
        if overlap:
            raise ValueError(f"style properties cannot be both set and removed: {sorted(overlap)}")
        return self


class AttributeMutation(StrictModel):
    set: dict[str, str] = Field(default_factory=dict, max_length=100)
    remove: list[str] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def valid(self) -> "AttributeMutation":
        overlap = {key.lower() for key in self.set} & {key.lower() for key in self.remove}
        if overlap:
            raise ValueError(f"attributes cannot be both set and removed: {sorted(overlap)}")
        forbidden = {
            key
            for key in (*self.set, *self.remove)
            if key.lower() == "data-office-id" or key.lower().startswith("data-domoxml-")
        }
        if forbidden:
            raise ValueError("Office/domOXML internal attributes are server-owned")
        if any(key.lower().startswith("on") for key in self.set):
            raise ValueError("event-handler attributes are not allowed")
        return self


class ElementMutation(StrictModel):
    element: ElementSelector
    text: str | None = None
    inner_html: str | None = None
    replace_html: str | None = None
    styles: StyleMutation | None = None
    attributes: AttributeMutation | None = None

    @model_validator(mode="after")
    def valid_operations(self) -> "ElementMutation":
        content = {"text", "inner_html", "replace_html"} & self.model_fields_set
        if len(content) > 1:
            raise ValueError("text, inner_html, and replace_html are mutually exclusive")
        if not content and self.styles is None and self.attributes is None:
            raise ValueError("at least one element operation must be supplied")
        return self


class ElementUpdateArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    elements: list[ElementMutation] = Field(min_length=1, max_length=100)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None


class ElementUpdateResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slide_id: SlideId
    updated_element_ids: list[ElementId]


class ElementMoveOperation(StrictModel):
    element: ElementSelector
    relative_to: ElementSelector
    position: ElementInsertPosition


class ElementMoveArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    moves: list[ElementMoveOperation] = Field(min_length=1, max_length=50)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None


class ElementMoveResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slide_id: SlideId
    moved_element_ids: list[ElementId]


class ElementDeleteArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    elements: list[ElementSelector] = Field(min_length=1, max_length=100)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None


class ElementDeleteResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slide_id: SlideId
    deleted_element_ids: list[ElementId]
