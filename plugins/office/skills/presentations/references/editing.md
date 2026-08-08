# Editing an existing deck

Leading concept: **PRESERVE**. An edit request is permission to change the requested surface, not to restyle, rewrite, reorder, or "improve" everything around it.

## The existing deck is the design system

Before editing anything:

- inspect the deck outline (`presentation_inspect`);
- inspect neighboring or otherwise relevant slides;
- derive the local typography, spacing, palette, and layout conventions already in use;
- respect those conventions unless the user explicitly asked for a redesign.

Do not consult `references/design-atlas.md` for a targeted edit — the deck itself is the authoritative design reference here, not inspiration material.

## Surgical edits

For a small, well-scoped change:

```text
slide_inspect(detail="structure")
→ element_update
→ preview only the affected slide
```

Do not read or rewrite an entire slide's source when a structural inspection already tells you enough to target the right element.

## Adding a matching slide

Prefer `slide_duplicate` of the closest conceptual/layout sibling, then replace its content with element edits. This inherits the established visual language for free and is far safer than synthesizing a new layout from scratch. Only derive a new layout from the deck's conventions if no suitable sibling exists.

## Batch semantics

Batch edits that form one coherent user intent — one metric refresh, one set of copy changes, one coordinated styling fix — into a single `element_update` call and revision. Do not batch unrelated changes merely to reduce the number of calls; unrelated batching makes a revision harder to reason about and harder to revert.

## Preserve untouched content

An edit request is not permission to:

- restyle every slide;
- rewrite copy the user didn't ask about;
- reorder the narrative;
- normalize every stylistic difference you notice along the way.

Positive target: change the requested surface while preserving established design and unrelated content exactly as it was.

## When full slide replacement is appropriate

Use `slide_update(html=...)` — the full-slide escape hatch — when:

- the user explicitly requested a redesign of that slide;
- the layout is fundamentally wrong for the content it now needs to hold;
- imported/legacy structure cannot support the intended change and rebuilding is safe (see `references/domoxml-fidelity.md` before rebuilding imported content);
- several related changes together make surgical mutation more fragile than a clean rebuild.

Otherwise, element-level mutation is the default, not full replacement.

## Revision conflicts

If `element_update`, `slide_update`, or any other mutation returns `REVISION_CONFLICT`, re-inspect the presentation's current revision and intentionally reapply the change against it. Do not blindly retry the stale call — another edit landed in between, and blind retry can silently clobber it.

## Completion criterion

An edit is complete when:

- the requested change is visibly present;
- the deck's established design language remains coherent;
- unrelated content is unchanged;
- the affected slide has been re-previewed;
- no new visual defect was introduced.
