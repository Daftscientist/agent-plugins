# AGENTS.md — rostra plugin

Rules for editing this plugin. Repo root rules (CONTRIBUTING, design conventions) also
apply; this file adds plugin-specific ones.

## What this plugin is

A declaration package: `mcp.json` points at the live Rostra endpoint
(`https://ask.daft.onl/mcp`); `skills/` teaches when and how to use it. There is no
`server/` and no local state. Capability lives upstream.

## Hard rules

- **No credentials, ever.** `mcp.json` headers and all portable files are public repo
  data. Auth is client-managed (see DESIGN.md §4). A grep for secrets is a quality gate.
- **Skills teach workflow, never tool reference.** Tools self-describe on the wire.
  Skill bodies may name `rostra__*` tools as workflow steps, but must not restate their
  parameter contracts or duplicate upstream docs (docs/MCP_TOOLS.md upstream).
- **Every skill needs an independent trigger.** `description` must say when this skill
  is the one, in plain intent language; `allowed-tools` must scope exactly the Rostra
  subset that job needs, all of which must be real catalogue tools.
- **Style:** markdown, no em/en dashes, no curly quotes (repo convention). Frontmatter
  `description` values must be YAML-safe (quote them; a colon+space inside a plain
  scalar breaks parsing).
- **Metering doctrine is standing:** every Rostra call costs 1 credit; skills must tell
  the model to dispatch deliberately and paginate only when the next page changes the
  answer.
- Typed error codes are expected from live upstreams; skills may teach retry-once for
  transient blips and never retry policy errors (`unauthorized`, `not_permitted`,
  `insufficient_credits`, `invalid_args`).

## Validation before commit

1. Every `plugins/rostra/skills/*/SKILL.md` YAML frontmatter parses and yields
   `name` + `description` + `allowed-tools`.
2. `allowed-tools` names all exist in the Rostra catalogue (22 tools); nothing outside
   the set is referenced in the body.
3. No `Authorization`, `Bearer`, key-shaped, or `.env` strings anywhere in the package.
4. Sol's own `parse_skill_metadata` accepts every skill (run where Sol is checked out:
   `python -c` over `src/sol/skills/manifest.py`).
