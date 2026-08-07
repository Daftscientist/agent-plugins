"""Preview request and result models."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .base import PresentationId, RevisionId, SlideId, StrictModel
from .common import Activity


class PreviewAll(StrictModel):
    type: Literal["all"] = "all"


class PreviewRange(StrictModel):
    type: Literal["range"] = "range"
    start: int = Field(ge=1)
    end: int = Field(ge=1)

    @model_validator(mode="after")
    def ordered(self) -> "PreviewRange":
        if self.end < self.start:
            raise ValueError("end must be greater than or equal to start")
        return self


class PreviewSlides(StrictModel):
    type: Literal["slides"] = "slides"
    slide_ids: list[SlideId] = Field(min_length=1, max_length=100)


PreviewSelection = Annotated[PreviewAll | PreviewRange | PreviewSlides, Field(discriminator="type")]


class PreviewLayout(StrEnum):
    AUTO = "auto"
    SINGLE = "single"
    CONTACT_SHEET = "contact_sheet"


class PreviewQuality(StrEnum):
    STANDARD = "standard"
    HIGH = "high"


class PreviewLabels(StrEnum):
    NONE = "none"
    NUMBER = "number"
    NAME = "name"
    NUMBER_AND_NAME = "number_and_name"


class PresentationPreviewArgs(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId | None = None
    selection: PreviewSelection = Field(default_factory=PreviewAll)
    layout: PreviewLayout = PreviewLayout.AUTO
    quality: PreviewQuality = PreviewQuality.STANDARD
    labels: PreviewLabels = PreviewLabels.NUMBER_AND_NAME
    columns: Literal[2, 3, 4, 5] | None = None
    activity: Activity | None = None


class PreviewImageDescriptor(StrictModel):
    page: int = Field(ge=1)
    slide_ids: list[SlideId]
    width_px: int = Field(gt=0)
    height_px: int = Field(gt=0)
    mime_type: Literal["image/png"] = "image/png"


class PresentationPreviewResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    layout: PreviewLayout
    images: list[PreviewImageDescriptor]
