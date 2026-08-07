"""Generate API reference from the live MCP registry."""

import argparse
import asyncio
import json
from pathlib import Path

from office_mcp.app import mcp


async def generate() -> str:
    tools = await mcp.list_tools()
    templates = await mcp.list_resource_templates()
    prompts = await mcp.list_prompts()
    lines = [
        "# Office API reference",
        "",
        "Generated from the live typed MCP registry.",
        "",
        "## Tools",
        "",
    ]
    for tool in tools:
        lines.extend(
            [
                f"### `{tool.name}` — {tool.title or tool.name}",
                "",
                tool.description or "",
                "",
                "Input schema:",
                "",
                "```json",
                json.dumps(tool.input_schema, indent=2, sort_keys=True),
                "```",
                "",
                "Output schema:",
                "",
                "```json",
                json.dumps(tool.output_schema or {}, indent=2, sort_keys=True),
                "```",
                "",
                "Annotations:",
                "",
                "```json",
                json.dumps(
                    tool.annotations.model_dump(mode="json", by_alias=True)
                    if tool.annotations
                    else {},
                    indent=2,
                    sort_keys=True,
                ),
                "```",
                "",
            ]
        )
    lines.extend(["## Resource templates", ""])
    for template in templates:
        lines.append(f"- `{template.uri_template}` — {template.title or template.name}")
    lines.extend(["", "## Prompts", ""])
    for prompt in prompts:
        arguments = ", ".join(argument.name for argument in prompt.arguments or []) or "none"
        lines.append(f"- `{prompt.name}` — {prompt.title or prompt.name}; arguments: {arguments}")
    lines.extend(
        [
            "",
            "## Completion-enabled arguments",
            "",
            "- `presentation_id`",
            "- `slide_id` (dependent on `presentation_id`)",
            "- `element_id` (dependent on `presentation_id` and `slide_id`)",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, nargs="?", default=Path("../API_REFERENCE.md"))
    args = parser.parse_args()
    args.output.write_text(asyncio.run(generate()), encoding="utf-8")


if __name__ == "__main__":
    main()
