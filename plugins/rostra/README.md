# Rostra

Rostra is a portable Agent Plugin for the unified sovereign-search and research data
layer behind the Rostra MCP endpoint (`https://ask.daft.onl/mcp`): web search, page
reading, news, prediction markets, Reddit, Hacker News, Mastodon, Bluesky, X, GitHub,
and YouTube behind one typed result shape, metered per call.

This plugin ships **no server code and no local state**. It is a declaration package:
one `mcp.json` remote-server entry plus eight Agent Skills that teach *when and how* to
use the Rostra tools. All capability lives upstream; the plugin makes it discoverable
and usable by agent clients.

## Skills

| Skill | What it is for |
|---|---|
| topic-research | deep research: strands, primary sources, verification, synthesis |
| person-research | identity-first briefs on people, orgs, projects, products |
| investigation | trace a claim to its origin; grade what the receipts support |
| vibe-check | how different communities actually received something |
| repo-intelligence | OSS due diligence: maintained, adoptable, worth it? |
| trend-explainer | why something is blowing up, and whether it is real |
| video-digest | video to usable knowledge, currency-checked |
| find-anything-online | recover the exact thing from messy half-remembered clues |

Each skill declares `allowed-tools` scoping exactly the Rostra subset its job needs.

## Authentication

The portable files contain **no credentials** (Agent Plugins v1.0.0: configured
headers must be literal, secret-free package data). Rostra's MCP endpoint is
OAuth-authenticated today; a shared API key path is being added upstream with an
explicit MCP opt-in per key. Clients choose their own auth (see `DESIGN.md` §4).

## Sources of truth

- Agent Plugins spec + author guide: <https://agent-plugins.org/specification>, <https://agent-plugins.org/plugin-authors>
- Rostra tool contracts: `docs/MCP_TOOLS.md` (upstream Rostra repo)
- Design + auth model + milestones: [`DESIGN.md`](./DESIGN.md)
