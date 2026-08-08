# Office implementation rules

1. Read `DESIGN.md` completely before changing Office architecture.
2. Inspect current domOXML, Agent Plugins, and official MCP Python SDK v2 APIs; never guess.
3. Use `mcp.server.MCPServer`; never use FastMCP v1.
4. Expose HTML with inline CSS, never OOXML or shape micro-tools.
5. Reject active content and caller-controlled `data-office-id` values.
6. Use opaque IDs and hidden request scope for every store and protocol operation.
7. Preserve domOXML warnings, preservation data, and coverage debt.
8. Keep MCP handlers thin and domain/storage/domOXML concerns independently testable.
9. Never require model filesystem access or enable local/network input by default.
10. Run `ruff check`, `ruff format --check`, `pyright`, and `pytest` before pushing.
11. Treat MCP/API schemas as the source of truth for exact operations; skills teach workflow and expertise, not duplicated tool reference.
12. Keep `skills/presentations/SKILL.md` focused and route branch-specific knowledge into one-hop references.
13. Design-atlas material is optional inspiration, never a preset whitelist or mandatory style selector.
14. Do not copy third-party skill text/assets without license verification and provenance recorded in `skills/presentations/SOURCES.md`.
15. When adding a discovered skill, justify its independent invocation branch and context cost. A new discovered Office skill requires at least one of: a distinct independent user trigger that should activate without ordinary presentation creation/editing; a materially different execution lifecycle; a materially different correctness/verification model. Splitting `presentations` into topic-based skills (e.g. a separate typography/reviewing/editing skill) does not qualify — those remain references under the one presentation skill.
