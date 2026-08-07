"""Stable, sanitised domain errors."""

from enum import StrEnum


class ErrorCode(StrEnum):
    PRESENTATION_NOT_FOUND = "PRESENTATION_NOT_FOUND"
    SLIDE_NOT_FOUND = "SLIDE_NOT_FOUND"
    ELEMENT_NOT_FOUND = "ELEMENT_NOT_FOUND"
    AMBIGUOUS_ELEMENT_NAME = "AMBIGUOUS_ELEMENT_NAME"
    INVALID_PRESENTATION_SOURCE = "INVALID_PRESENTATION_SOURCE"
    UNSUPPORTED_SOURCE_SCHEME = "UNSUPPORTED_SOURCE_SCHEME"
    SOURCE_TOO_LARGE = "SOURCE_TOO_LARGE"
    INVALID_PPTX = "INVALID_PPTX"
    INVALID_HTML = "INVALID_HTML"
    UNSAFE_HTML = "UNSAFE_HTML"
    UNSUPPORTED_CSS = "UNSUPPORTED_CSS"
    REVISION_CONFLICT = "REVISION_CONFLICT"
    INVALID_SLIDE_ORDER = "INVALID_SLIDE_ORDER"
    INVALID_ELEMENT_MOVE = "INVALID_ELEMENT_MOVE"
    IMPORT_FAILED = "IMPORT_FAILED"
    RENDER_FAILED = "RENDER_FAILED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    EXPORT_FAILED = "EXPORT_FAILED"
    RESOURCE_TOO_LARGE = "RESOURCE_TOO_LARGE"
    ACCESS_DENIED = "ACCESS_DENIED"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class OfficeError(Exception):
    """A model-recoverable error with a stable public code."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code.value}: {message}")


class RevisionConflict(OfficeError):
    def __init__(self, expected: str, current: str) -> None:
        super().__init__(
            ErrorCode.REVISION_CONFLICT,
            f"presentation changed since {expected}; current revision is {current}. "
            "Re-inspect before applying the mutation.",
        )
