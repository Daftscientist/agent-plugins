# Changelog

All notable changes to the `rostra` plugin.

## [0.1.0] - 2026-09-08

Initial portable package:

- `plugin.json` + `mcp.json` (streamable-http to `https://ask.daft.onl/mcp`), no
  credentials, no client-specific data.
- Eight procedure skills under `skills/<slug>/SKILL.md`, each declaring `allowed-tools`
  over its Rostra subset: topic-research, person-research, investigation, vibe-check,
  repo-intelligence, trend-explainer, video-digest, find-anything-online.
- `DESIGN.md` covering the auth model (Rostra per-key MCP opt-in upstream, client-side
  secret injection) and E2E acceptance steps.
