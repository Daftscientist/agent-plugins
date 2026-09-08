# Rostra Agent Plugin — Daft search & research data layer for agents

> **Target repository:** `https://github.com/Daftscientist/agent-plugins`
> **Intended path:** `plugins/rostra/DESIGN.md`
> **Status:** draft for review (not yet implemented)
> **Agent Plugins target:** `1.0.0`
> **MCP target:** `2026-07-28` (stateless; the live Rostra server speaks this)
> **Transport:** `streamable-http`

## 0. Purpose

`rostra` is a thin, portable Agent Plugin that gives an agent client access to the
Rostra MCP endpoint (`https://ask.daft.onl/mcp`) — the unified sovereign-search and
research data layer (web, page reading, news, markets, Reddit, Hacker News, Mastodon,
Bluesky, X, GitHub, YouTube) behind one typed result shape.

Unlike `plugins/office`, this plugin ships **no server code and no local state**. It is
a *declaration* package: a portable `mcp.json` remote-server entry plus Agent Skills
that teach when and how to use the Rostra tools. All capability lives upstream in the
Rostra service; the plugin makes it discoverable and usable by agent clients.

The plugin must remain a valid, portable Agent Plugin (per agent-plugins.org v1.0.0):
the portable core (`plugin.json`, `mcp.json`, `skills/`) contains **no credentials and
no client-specific enablement data**. Authentication is client-managed by the standard's
design — see §4.

## 1. Sources of truth

- Agent Plugins specification + author guide: <https://agent-plugins.org/specification>, <https://agent-plugins.org/plugin-authors>
- Rostra MCP tool surface spec (per-tool contracts, summary shapes): upstream repo `docs/MCP_TOOLS.md`
- MCP spec `2026-07-28`: <https://modelcontextprotocol.io/specification/2026-07-28>

## 2. Layout

```
plugins/rostra/
├── plugin.json              # portable manifest (no secrets, no Sol data)
├── mcp.json                 # one streamable-http server -> ask.daft.onl/mcp
├── AGENTS.md                # implementation rules for this plugin
├── README.md                # what the plugin is, auth model, client notes
├── CHANGELOG.md
├── LICENSE                  # MIT (repo convention)
└── skills/
    └── rostra/
        ├── SKILL.md         # one discovered skill: tool selection + usage contract
        └── references/      # per-source quirks, result-shape notes, citing rules
```

No `server/` directory: there is nothing to build or run locally. No `on.daft.sol`
extension in the portable files — Sol-specific enablement/auth is injected by the
client at install (see §4), never shipped.

## 3. Portable manifest

`plugin.json` (name rules: lowercase, 1–64 chars; `rostra` is valid):

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "rostra",
  "version": "0.1.0",
  "description": "Daft sovereign search and research data layer: unified web search, page reading, news, markets, and major social + developer sources behind one typed result shape.",
  "author": {"name": "Daftscientist"},
  "repository": "https://github.com/Daftscientist/agent-plugins",
  "license": "MIT",
  "keywords": ["rostra", "daft", "search", "research", "news", "web", "social", "mcp"]
}
```

`mcp.json` (closed format; only `$schema` + `mcpServers`):

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "rostra": {
      "type": "streamable-http",
      "url": "https://ask.daft.onl/mcp"
    }
  }
}
```

**No `headers`.** Agent Plugins requires configured headers to be literal package data
free of credentials, and this repo is public. The portable core must be installable by
any conformant client unchanged; authentication belongs to the client (§4).

## 4. Authentication design (the "global, no opt-in" requirement)

Two orthogonal facts drove this design:

1. Rostra's MCP endpoint authenticates **OAuth bearer tokens** today (per-connection
   tool allowlist, suspension, revocation, rpm, per-call credit debit). That profile is
   per-user: on a multi-user client each user needs their own connect flow.
2. The operator wants Rostra tools **globally available** inside Sol (no per-user
   opt-in), using a **single shared API key** instead of per-user OAuth.

### 4.1 Rostra: API keys become an MCP auth option (upstream change)

Rostra already has programmatic **REST API keys** (`api_keys` table; minted via
`mint()`; validated via `auth_by_key_hash`). MCP auth is currently OAuth-only at two
seams: the `/mcp` gate and the per-tool authorizer.

Change (upstream spec, separate document): add **explicit per-key MCP opt-in at mint**
(a key is MCP-capable only when flagged, so no existing REST key silently widens to
MCP). An MCP-capable key is presented as `Authorization: Bearer <key>` and runs the
same policy/metering path as an OAuth connection. Keys minted for this plugin's use:
MCP-enabled, no tool allowlist (all tools), account/credit controls as usual.

### 4.2 Client: Sol injects the key from its own secrets (Sol-side change)

Sol is an Agent Plugins client with its own `on.daft.sol` client-extension namespace
carrying enablement + authorization. For a *global* remote server whose transport
cannot carry a secret, Sol resolves the key from Sol's own configuration at connect
time and injects `Authorization: Bearer <key>` into that one connection's headers —
the same pattern as Sol's model-provider API keys. The portable files stay clean; the
key lives in Sol's environment, never in a plugin file.

The Sol-side contract (implemented in Sol's ADR for global server-secret injection):
- plugin declares `on.daft.sol` in its own install copy: `enablement: "global"` and a
  server-auth requirement naming the config key;
- `enable()` resolves the secret and merges the header before the shared session is
  opened; GLOBAL remote servers already connect once at boot with fixed headers;
- per-user OAuth remains available to Sol for OTHER remote plugins — it is orthogonal
  and untouched.

### 4.3 Other clients

Any other Agent Plugins client can install `rostra` unchanged and choose its own auth
(OAuth flow, its own key storage, etc.). This repo never locks the plugin to Sol.

## 5. Skills

One discovered skill, `skills/rostra/SKILL.md` (office precedent: one skill + one-hop
references; a new discovered skill needs an independent invocation branch — here the
whole surface is one coherent "research/data lookup" capability):

- **SKILL.md**: when to reach for Rostra vs the client's native tools; tool-selection
  guidance per intent (web vs news vs market vs social source vs page fetch); the
  unified result shape; hard rule to cite returned source URLs inline; error-code
  handling (typed errors are expected from live upstreams — retry before blaming the
  tool; `unauthorized`/`not_permitted` mean connection/key policy, never retry);
  pagination via `next_cursor`.
- **references/** (authored from the grounded upstream tool spec — never duplicated
  tool reference, only workflow/expertise):
  - `tool-selection.md` — which tool for which intent and source;
  - `source-quirks.md` — per-source caveats (e.g. X people results need screen names;
    some surfaces ignore region controls; detail tools take explicit ids);
  - `citing.md` — inline citation + provenance-field rules.

## 6. Quality gates

- Manifest JSON validates against the agent-plugins.org `1.0.0` schemas.
- No credentials, `.env`, or client-specific data anywhere under `plugins/rostra`
  (grep gate in CI if added).
- Skill markdown loads (frontmatter name/description valid per Agent Skills).
- Live E2E (see §8) is the acceptance bar — a config-only plugin is *verified* only by
  a real client calling real tools through it.

## 7. Milestones

- **M1 — Package**: files above + repo README row + CI schema-validation job. Done
  when manifests validate and the package is installable by a conformant client.
- **M2 — Rostra API-key MCP opt-in** (upstream): spec approved → implement mint flag +
  two auth seams → live probe (fresh MCP-enabled key: tools/list, real calls, deny for
  non-MCP keys, policy checks).
- **M3 — Sol global injection**: Sol ADR → extension field + `enable()` secret
  resolution + adapter header merge → symlink-enable on LeoVM → E2E.
- **M4 — Skills + polish**: author SKILL.md + references from grounded tool spec;
  CHANGELOG; final review.

## 8. E2E acceptance (before "done")

1. Mint an MCP-enabled key on Rostra; verify a non-MCP key is rejected at `/mcp`.
2. Install `rostra` in Sol as GLOBAL with the key in Sol's env.
3. All Rostra tools register under `rostra__*`; `rostra__search_web` and one
   source-specific tool return real results with `status:ok`; credits debit to the
   key's account.
4. No per-user connect step exists; every Sol user's chat can call the tools.
5. Skills: `skill_search` returns the skill; `skill_load` reads it.
