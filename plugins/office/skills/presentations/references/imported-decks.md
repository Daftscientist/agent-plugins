# Handling imported decks

Purpose: operational behavior for existing PPTX opened through `presentation_open`, where editability and preservation matter. For the underlying category definitions, see `references/domoxml-fidelity.md` — this file focuses on what to *do*, not what the enums mean.

## Representation decision table

**`native` with semantic editability** — the normal editing path. Prefer element-level edits as usual.

**`decomposed` / components** — content is editable but one source object may be represented as several components. Understand the grouping (`slide_inspect(detail="structure")`) before changing structure, so you don't split something the user perceives as one object.

**`hybrid`** — some content stays semantic/native while other content relies on layered/preserved representation. Edit the semantic parts surgically; leave the preserved parts alone unless the user asked to change them. Validate afterward.

**`layered` / `element_layer`** — appearance is preserved through layers. Visual edits may be possible, but semantic meaning is reduced. Treat reconstruction of this content carefully; don't casually rebuild it into "clean" HTML, since that can lose what made it render correctly.

**`rasterized`** — appearance is image-like; text/object editing is not meaningfully available. Only rebuild this content if the user actually wants a replacement, not a fix.

**`approximated`** — expect visual/fidelity differences from the original. Inspect the preview and decide with the user's intent in mind whether the approximation is acceptable as-is.

**`failed`** — do not pretend this content is editable. Either repair/rebuild it intentionally, or explain the limitation to the user rather than silently producing something broken.

## Source retention

`not_required`, `attached`, `detached`, `ignored`, `lost` describe whether original source bytes needed for exact round-tripping are still available. Understand the consequence, not just the label: once source retention degrades past `attached`, editing that content may make a byte-identical re-export impossible. If a user wants to touch content whose source retention is already `detached`/`ignored`/`lost`, tell them the edit may affect fidelity rather than assuming it's free.

## Untouched imported decks

If no content edit is actually required and Office can preserve the original bytes exactly, do not force a conversion or reconstruction "for cleanliness." An untouched import should export byte-identical to what came in — don't spend a mutation making that no longer true.

## Completion criterion

Imported-deck work is complete when:

- the target content is changed as requested;
- untouched, unsupported content remains preserved where possible;
- validation/preservation warnings have been reviewed, not ignored;
- no fidelity debt is silently hidden from the user.
