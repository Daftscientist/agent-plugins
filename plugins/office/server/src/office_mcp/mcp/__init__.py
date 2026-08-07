"""MCP protocol registration."""

from .completions import register_completions
from .prompts import register_prompts
from .resources import register_resources
from .tools import register_tools

__all__ = ["register_completions", "register_prompts", "register_resources", "register_tools"]
