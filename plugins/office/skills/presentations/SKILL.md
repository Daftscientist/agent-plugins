---
name: presentations
description: Create, inspect, edit, preview, validate, and export PowerPoint presentations using the Office MCP tools and domOXML-backed HTML/CSS authoring. Use for PPTX or slide-deck work.
---

# Presentations

Use Office as a small typed presentation IDE. It stores editable decks by opaque IDs and revisions; it does not expose PowerPoint XML or require filesystem access.

## Workflow

1. For an unfamiliar deck, call `presentation_inspect` before modifying it. Navigate using its outline; do not open every slide.
2. Call `slide_inspect(detail="structure")` before requesting source. Use source only when exact styles or a redesign require it.
3. Prefer `element_update` for text, style, attribute, and small subtree changes. Batch related edits into one call and revision.
4. Use `slide_update(html=...)` only for a genuine full-slide rebuild.
5. Use `slide_duplicate` followed by element edits to reuse a layout.
6. Name every new slide descriptively and add concise descriptions to non-trivial slides.
7. Author semantic HTML with inline CSS only. Give important future-edit targets unique `data-office-name` aliases.
8. Never invent, copy, or modify `data-office-id`; Office owns it.
9. After broad edits, preview the full deck once. For detailed visual debugging, preview only the affected slide. Do not repeatedly preview unchanged slides.
10. Validate when editability, representation fidelity, or preservation matters.
11. Export the final intended revision.

If `REVISION_CONFLICT` occurs, re-inspect the current revision and intentionally reapply the change. Do not blindly retry stale edits.

See [authoring](references/authoring.md), [editing](references/editing.md), [capabilities](references/capabilities.md), and [examples](references/examples.md) when the task needs more detail.
