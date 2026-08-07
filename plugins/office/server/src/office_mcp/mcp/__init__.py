"""MCP protocol registration."""

from .completions import register_completions
from .prompts import register_prompts
from .resources import register_resources
from .subscriptions import register_scoped_subscriptions
from .tools import register_tools

__all__ = [
    "register_completions",
    "register_prompts",
    "register_resources",
    "register_scoped_subscriptions",
    "register_tools",
]
