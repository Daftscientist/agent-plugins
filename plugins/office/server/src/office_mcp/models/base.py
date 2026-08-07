"""Public strict model base and identifier aliases."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, validate_assignment=True)


PresentationId = Annotated[str, Field(pattern=r"^prs_[A-Za-z0-9_-]{8,}$")]
RevisionId = Annotated[str, Field(pattern=r"^rev_[A-Za-z0-9_-]{8,}$")]
SlideId = Annotated[str, Field(pattern=r"^sld_[A-Za-z0-9_-]{8,}$")]
ElementId = Annotated[str, Field(pattern=r"^el_[A-Za-z0-9_-]{8,}$")]
