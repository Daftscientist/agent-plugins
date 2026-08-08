# Worked examples

A few tool-flow examples plus reasoning examples, showing when stages of `SKILL.md` are used in full and when they're rightly skipped.

## New deck

```text
ORIENT    understand audience, purpose, and that this is a from-scratch deck
ARC       plan the title sequence; each slide gets one job
SYSTEM    pick typography/palette/motif from references/design-foundations.md
BUILD     presentation_create with every planned slide in one call
SEE       presentation_preview(selection={"type":"all"}), review as a sequence
REPAIR    element_update the weak slides found in SEE
PREFLIGHT presentation_validate, fresh preview, presentation_export
```

## Tiny metric update

`"On slide 4 change ARR from £1.2m to £1.8m."`

`slide_inspect(detail="structure")` on slide 4, then one `element_update` targeting the `arr` semantic name. ARC and SYSTEM are skipped entirely — there is no narrative or visual system decision to make for a single value swap. Preview only slide 4 afterward, not the whole deck.

## Existing slide redesign

`"Slide 6's layout doesn't work for this content, rebuild it."`

Inspect the slide's source and its neighbors to understand the deck's system, then `slide_update(html=...)` to rebuild slide 6 within that system, then preview the slide. Full replacement is appropriate here because the layout itself is what's wrong.

## Add a matching slide

`"Add a slide after pricing summarizing enterprise support. Match the deck."`

`slide_duplicate` the pricing slide (or the closest layout sibling) into position after it, then replace its content with `element_update`. The atlas is not consulted — the deck already defines the visual language.

## Open design brief

`"Make a visually distinctive deck about data-centre security. Surprise me."`

Optionally read `references/design-atlas.md`, then synthesize a direction across several dimensions rather than picking one named entry:

```text
User: "Make a technical deck about a security incident. Clean, not cyberpunk."

Direction:
Swiss/technical schematic foundation
+ monochrome
+ restrained red incident accent
+ mono metadata labels
+ architectural-flow diagrams

Not: select "Cyberpunk Outline preset"
```

## Mixed inspiration

```text
User: "1970s scientific journal but for modern cloud infrastructure."

Direction:
warm/off-white editorial base
+ serif display
+ mono technical labels
+ thin engineering diagrams
+ restrained archival photography
```

The agent synthesizes across dimensions; it never responds "that's not in the style library."

## Review

`"Review this deck and make it look less AI-generated."`

Whole-deck preview first, rubric from `references/reviewing.md`, content-specific repairs — fewer identical rounded cards, fewer pills, no blind restyling of slides that were already fine. See the failure-pattern list in `references/design-foundations.md`.

## Imported low-editability object

`"Fix the wording on this imported PPTX but preserve everything else."`

Inspect, check editability/representation per `references/domoxml-fidelity.md`, make a preservation-aware surgical edit to only the requested text, validate, and confirm untouched content still exports faithfully.

## Pitch

`"Build a Series B deck for a marketplace."`

Read `references/pitch-decks.md`. Weight the narrative toward liquidity, take rate, cohort behavior, and network effects — the Series B B2B SaaS heuristics (retention, unit economics as the headline) do not transfer directly. No generic seed-stage template.
