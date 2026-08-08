# domOXML representation, editability, and preservation

This is the authoritative skill-level explanation of why an apparently correct preview can still carry preservation debt, and how to reason about it. `references/imported-decks.md` covers the operational decision table; this file covers the underlying model. `SKILL.md` points here directly for representation/editability questions so the routing stays one hop, not a chain.

## Why this exists

domOXML compiles HTML/CSS into a typed intermediate representation and back out to PPTX/PNG. When a *human-made* PPTX is imported, domOXML has to normalize arbitrary OOXML back toward that same HTML/CSS model. Not everything in an arbitrary deck maps cleanly. domOXML reports exactly how well each piece of content survived that trip, instead of pretending everything became fully native.

## Representation

How a piece of imported content is currently expressed internally:

| Value | Meaning |
|---|---|
| `native` | Fully expressed in Office's normal HTML/CSS model. Behaves like anything you'd create yourself. |
| `decomposed` | Preserved as multiple components rather than one object. Still editable, but structurally different from the source. |
| `hybrid` | Part native/semantic, part preserved/layered. |
| `layered` | Appearance preserved through stacked layers rather than clean semantic markup. |
| `element_layer` | A narrower case of layered representation scoped to one element. |
| `rasterized` | Preserved as an image. Visually faithful, not editable as text/objects. |
| `approximated` | domOXML produced its closest supported equivalent; some visual difference from the source should be expected. |
| `failed` | domOXML could not produce a usable representation for this content. |

## Editability

Independent of representation, how much the model can actually change:

| Value | Meaning |
|---|---|
| `semantic` | Normal element-level editing works as expected. |
| `components` | Editable, but only through its constituent components — understand the grouping first. |
| `layers` | Editable at the layer level; semantic-level edits (e.g. "change this sentence") may not apply cleanly. |
| `none` | Not editable through Office's model-facing tools. |

## Source retention

Whether the bytes needed to reproduce the original exactly are still available:

| Value | Meaning |
|---|---|
| `not_required` | Content is fully native; no original bytes needed. |
| `attached` | Original source is retained and can support a faithful re-export. |
| `detached` | Original source existed but is no longer attached to this revision. |
| `ignored` | Retention was intentionally skipped for this content. |
| `lost` | Original source is gone; faithful re-export of this content is no longer possible. |

## Interpreting validation

`presentation_validate` reports `native_ratio`, `editable_ratio`, and `layered_ratio` alongside per-element coverage in `full` detail mode. A high native ratio means most content is fully editable; a nontrivial layered/rasterized fraction is not automatically a bug — it may simply be what the source deck required. Read the coverage `reason` field rather than treating any non-`native` value as an error to eliminate.

Office explicitly blocks export after content edits when source-only preservation fragments can no longer be reattached, rather than silently producing a file that looks right but has lost round-trip fidelity. If export is blocked for this reason, that is the system protecting the user from silent data loss — do not look for a workaround that bypasses it; explain the tradeoff instead.

## When to preserve vs. reconstruct

Preserve when: the user didn't ask to change that content, or editability is `layers`/`components`/`none` and a full rebuild isn't clearly wanted.

Reconstruct when: the user explicitly wants a redesign of that content, or representation is `failed` and there is no other way to make it usable.

Everything in between is a judgment call — state the tradeoff to the user rather than silently picking one.
