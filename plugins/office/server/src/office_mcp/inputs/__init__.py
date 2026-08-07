"""Presentation input adapters."""

from .pptx import validate_pptx
from .resolver import CompositeInputResolver, forbidden_address

__all__ = ["CompositeInputResolver", "forbidden_address", "validate_pptx"]
