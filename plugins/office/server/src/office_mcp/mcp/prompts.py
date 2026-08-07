"""Focused user-selected Office workflow prompts."""

from mcp.server import MCPServer

from office_mcp.icons import PRESENTATION_ICONS, VALIDATE_ICONS


def register_prompts(mcp: MCPServer) -> None:
    @mcp.prompt(
        name="create_presentation",
        title="Create presentation",
        description="Start a structured Office presentation workflow.",
        icons=PRESENTATION_ICONS,
    )
    def create_presentation(
        topic: str, audience: str = "", purpose: str = "", style: str = "", slide_count: str = ""
    ) -> str:
        return (
            f"Create a presentation about {topic}. Audience: {audience or 'unspecified'}. "
            f"Purpose: {purpose or 'unspecified'}. Style: {style or 'appropriate to the topic'}. "
            f"Slide-count hint: {slide_count or 'choose an effective length'}. "
            "Use the Office presentation skill: name every slide, author semantic HTML with "
            "inline CSS, batch creation, preview the deck, validate it, and export the "
            "final revision."
        )

    @mcp.prompt(
        name="review_presentation",
        title="Review presentation",
        description="Inspect, preview, and validate an Office presentation.",
        icons=VALIDATE_ICONS,
    )
    def review_presentation(presentation_id: str, focus: str = "") -> str:
        return (
            f"Review Office presentation {presentation_id}. Focus: "
            f"{focus or 'clarity, visual quality, fidelity, and editability'}. "
            "Inspect the outline first, preview the whole deck, inspect only problematic slides, "
            "validate domOXML coverage, "
            "and report or fix issues with element-level edits where appropriate."
        )
