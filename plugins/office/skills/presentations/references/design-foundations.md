# Design foundations

The core expert visual-design reference for the SYSTEM stage. Read this before `references/design-atlas.md` — foundations are how you judge whether an atlas combination actually works, not just whether it sounds distinctive.

## Hierarchy

Importance should be visible at a glance, built from scale, position, weight, contrast, whitespace, and isolation. A slide with four equally loud elements has no hierarchy at all — the reader has to do the work the designer should have done.

## Composition

Layout is a relationship between elements, not a collection of boxes. Think in terms of a focal region and a supporting region, balance (which can be symmetric or deliberately asymmetric), a grid, edge alignment, controlled overlap, and spatial grouping. See `references/compositions.md` for a catalogue of concrete structures.

## Whitespace

Whitespace communicates grouping, separation, hierarchy, a premium/quiet tone, and focus. It is not unused capacity that needs filling — a slide that "still has room" is not automatically improved by adding another card to it.

## Rhythm

Coherence across a deck comes from repeated margins, spacing values, type roles, alignment logic, motif, and image treatment. Variation should be controlled at the composition level — a deliberate change in structure for a section divider, for example — not accidental drift from slide to slide.

## Contrast

Contrast should answer one question: what matters first? Use more than color to create it — scale, weight, tone, position, whitespace, and shape all create contrast, and often more reliably than color alone.

## Restraint

One strong gesture usually beats six decorative ideas. If a slide has a glow, a gradient, an icon, a card, a pill, and a border all competing, none of them is actually doing work — they're canceling each other out.

## Motif

A recurring design gesture — edge labels, a hairline grid, oversized section numerals, cropped geometry, an accent bar, technical annotation, a consistent image-frame treatment — gives a deck identity. Choose one primary motif for most decks and use it consistently, not mechanically on every single slide. See `references/motifs.md` for a catalogue.

## Design quality is content-dependent

Do not treat fixed geometry as a hard rule — "every title is 42pt," "every margin is 64px," "every slide has 20% whitespace" are useful starting heuristics, not laws, unless there's an actual technical constraint forcing them. Reason relative to slide dimensions, content amount, audience, delivery context, and any existing design already in play, not a memorized number.

## Anti-"AI presentation" diagnostic

The positive principles above (hierarchy, composition, rhythm, content-specific structure, one gesture, restrained repetition) are what to aim for. The list below is a diagnostic for REPAIR and reviewing, not fifty rules to recite while building — most of these read as tells that a deck was built by filling a template rather than composed around its content:

- six identical rounded cards, used because a container was needed, not because six equal-weight items exist;
- every slide using the same centered-hero layout regardless of content;
- gradients or glows applied regardless of topic or tone;
- random decorative icons that don't map to a concept;
- excessive pills/badges;
- everything boxed, nothing given room to breathe;
- a huge title and tiny body with nothing in between to carry mid-level hierarchy;
- charts included for decoration rather than to answer a question;
- the generic cyan-purple "AI tech" gradient aesthetic;
- too many unrelated border-radius values in one deck;
- glassmorphism cards applied to every slide regardless of whether depth serves the content;
- meaningless stock imagery;
- every element sized the same, so nothing is emphasized.

If a repair pass finds several of these on one slide, the fix is usually to remove decoration and rebuild hierarchy from the actual content, not to swap one decorative pattern for another.

## Templates and reference decks take priority

When the user supplies a template, brand guide, or existing deck, it is the primary design reference — inspect representative slides, derive its system, and match it. Do not "improve" it by mixing in atlas aesthetics unless the user explicitly asked for that. For a new slide inside an existing deck, duplicating a nearby matching slide (`references/editing.md`) is usually safer than synthesizing a new layout from foundations or the atlas.
