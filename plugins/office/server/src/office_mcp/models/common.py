"""Shared public domain types."""

import re
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AfterValidator, Field

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


_CSS_COLOR = re.compile(
    r"^(?:#[0-9a-f]{3,8}|[a-z]+|"
    r"(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch|color)"
    r"\([0-9a-z.,%+\- /]+\))$",
    re.IGNORECASE,
)


def _validated_css_color(value: str) -> str:
    value = value.strip()
    if not _CSS_COLOR.fullmatch(value):
        raise ValueError("must be a literal CSS color; URLs and CSS variables are not allowed")
    return value


ColorToken = Annotated[
    str,
    Field(min_length=1, max_length=100),
    AfterValidator(_validated_css_color),
]


def _validated_font_family(value: str) -> str:
    value = value.strip()
    if not value or any(ord(char) < 32 or char in ";{}():/@\\" for char in value):
        raise ValueError("must be a literal font-family name or comma-separated family list")
    return value


FontToken = Annotated[
    str,
    Field(min_length=1, max_length=200),
    AfterValidator(_validated_font_family),
]


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
    background: ColorToken = "#ffffff"
    foreground: ColorToken = "#0b0b0c"
    accent: ColorToken = "#4f46e5"
    muted: ColorToken = "#6b7280"


class ThemeFonts(StrictModel):
    heading: FontToken = "Inter"
    body: FontToken = "Inter"


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
