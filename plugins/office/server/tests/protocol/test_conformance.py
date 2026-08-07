import json
import re
from pathlib import Path

import jsonschema
import yaml

from office_mcp.generate_docs import generate

PLUGIN_ROOT = Path(__file__).parents[3]

PLUGIN_SCHEMA = {
    "type": "object",
    "properties": {
        "$schema": {"const": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"},
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 64,
            "pattern": r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$",
        },
        "version": {"type": "string"},
        "description": {"type": "string"},
        "author": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "url": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "homepage": {"type": "string"},
        "repository": {"type": "string"},
        "license": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "extensions": {"type": "object", "additionalProperties": {"type": "object"}},
    },
    "required": ["$schema", "name"],
    "additionalProperties": False,
}

MCP_SCHEMA = {
    "type": "object",
    "properties": {
        "$schema": {"const": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"},
        "mcpServers": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "type": {"const": "stdio"},
                    "command": {"type": "string", "minLength": 1},
                    "args": {"type": "array", "items": {"type": "string"}},
                    "env": {
                        "type": "object",
                        "propertyNames": {"not": {"enum": ["PLUGIN_ROOT", "PLUGIN_DATA"]}},
                        "additionalProperties": {"type": "string"},
                    },
                    "cwd": {
                        "type": "string",
                        "pattern": r"^(?:\./|\$\{PLUGIN_ROOT\}(?:/|$)|\$\{PLUGIN_DATA\}(?:/|$))",
                    },
                },
                "required": ["type", "command"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["$schema", "mcpServers"],
    "additionalProperties": False,
}


def test_agent_plugin_manifests_validate_against_pinned_1_0_schema() -> None:
    plugin = json.loads((PLUGIN_ROOT / "plugin.json").read_text())
    mcp = json.loads((PLUGIN_ROOT / "mcp.json").read_text())
    jsonschema.validate(plugin, PLUGIN_SCHEMA)
    jsonschema.validate(mcp, MCP_SCHEMA)
    assert plugin["$schema"].split("/")[-2] == mcp["$schema"].split("/")[-2] == "1.0.0"
    server = mcp["mcpServers"]["office"]
    assert server["command"] == "uv"
    assert "PLUGIN_ROOT" not in server.get("env", {})
    assert "PLUGIN_DATA" not in server.get("env", {})


def test_agent_skill_frontmatter_and_discovery_path_are_valid() -> None:
    skill_path = PLUGIN_ROOT / "skills" / "presentations" / "SKILL.md"
    source = skill_path.read_text()
    frontmatter = source.split("---", 2)[1]
    metadata = yaml.safe_load(frontmatter)
    assert metadata["name"] == skill_path.parent.name
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"])
    assert 1 <= len(metadata["description"]) <= 1024
    assert len(source.splitlines()) < 500


def test_plugin_paths_are_self_contained() -> None:
    mcp = json.loads((PLUGIN_ROOT / "mcp.json").read_text())["mcpServers"]["office"]
    assert all("../" not in value for value in mcp["args"])
    assert mcp["cwd"].startswith("${PLUGIN_ROOT}")


async def test_generated_api_reference_matches_live_registry() -> None:
    assert (PLUGIN_ROOT / "API_REFERENCE.md").read_text() == await generate()
