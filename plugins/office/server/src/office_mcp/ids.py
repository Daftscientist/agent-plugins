"""Opaque type-prefixed identifiers."""

import secrets


def new_id(prefix: str) -> str:
    """Return an opaque URL-safe identifier with at least 128 bits of entropy."""
    return f"{prefix}_{secrets.token_urlsafe(16)}"


def presentation_id() -> str:
    return new_id("prs")


def revision_id() -> str:
    return new_id("rev")


def slide_id() -> str:
    return new_id("sld")


def element_id() -> str:
    return new_id("el")
