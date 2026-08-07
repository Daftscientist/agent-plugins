"""Shared public domain types."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field

from .base import StrictModel


class Activity(StrictModel):
    label: Annotated[str, Field(min_length=1, max_length=100)]


class SlideSizePreset(StrEnum):
    WIDE_16_9 = "16:9"
    STANDARD_4_3 = "4:3"
    WIDE_16_10 = "16:10"


class PresetSlideSize(StrictModel):
    type: Literal["preset"] = "preset"
    preset: SlideSizePreset = SlideSizePreset.WIDE_16_9


class CustomSlideSize(StrictModel):
    type: Literal["custom"] = "custom"
    width_in: float = Field(gt=0, le=56.0)
    height_in: float = Field(gt=0, le=56.0)


SlideSize = Annotated[PresetSlideSize | CustomSlideSize, Field(discriminator="type")]


class SlideTransition(StrEnum):
    NONE = "none"
    FADE = "fade"
    PUSH = "push"
    WIPE = "wipe"
    COVER = "cover"
    SPLIT = "split"
    CUT = "cut"
    ZOOM = "zoom"
    DISSOLVE = "dissolve"
    MORPH = "morph"


class ThemePalette(StrictModel):
    background: str = "#ffffff"
    foreground: str = "#0b0b0c"
    accent: str = "#4f46e5"
    muted: str = "#6b7280"


class ThemeFonts(StrictModel):
    heading: str = "Inter"
    body: str = "Inter"


class PresentationTheme(StrictModel):
    palette: ThemePalette = Field(default_factory=ThemePalette)
    fonts: ThemeFonts = Field(default_factory=ThemeFonts)


class Representation(StrEnum):
    NATIVE = "native"
    DECOMPOSED = "decomposed"
    HYBRID = "hybrid"
    LAYERED = "layered"
    ELEMENT_LAYER = "element_layer"
    RASTERIZED = "rasterized"
    APPROXIMATED = "approximated"
    FAILED = "failed"


class Editability(StrEnum):
    SEMANTIC = "semantic"
    COMPONENTS = "components"
    LAYERS = "layers"
    NONE = "none"


class SourceRetention(StrEnum):
    NOT_REQUIRED = "not_required"
    ATTACHED = "attached"
    DETACHED = "detached"
    IGNORED = "ignored"
    LOST = "lost"
