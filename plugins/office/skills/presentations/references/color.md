# Color

Treat color as a system with defined roles, not a palette of favorites applied wherever a slide "needs some color."

## Role palette vs. arbitrary color

Define roles before picking hex values:

```text
background   the dominant surface color
surface      cards/panels distinct from the background
text          primary reading color, high contrast against background
accent        the one color used to draw attention
muted         secondary text, de-emphasized labels
```

Every color used on a slide should map to one of these roles. A color that doesn't map to a role is probably decoration that snuck in, not a decision.

## Contrast

Text must stay legible against its background at the sizes actually used — check this against real content, not just the palette in isolation. Low-contrast text over an image or a busy background is the most common legibility failure in decks that otherwise look polished.

## Semantic data colors

When color encodes meaning in a chart (positive/negative, categories, a highlighted series), keep that mapping consistent across every chart in the deck — don't let "the highlighted series" change color between slide 4 and slide 9.

## Dark and light

Both are valid systems. Decide once per deck (or once per section, deliberately) rather than drifting between them slide to slide without reason. Recheck contrast and image treatment when switching — an image treatment tuned for a light background often looks wrong on dark.

## Brand inheritance

An existing brand or template's palette always wins over anything invented here. Extract it from the source rather than guessing at "similar" colors.

## Monochrome and duotone

Monochrome (one hue family across background/surface/text, with contrast from value and weight alone) reads as disciplined and quiet. Duotone (two colors mapped across an image or across a whole deck) reads as bold and editorial. Both are strong choices when applied consistently — weak when applied to only some slides.

## Warm / cool

Warm palettes read as approachable, human, energetic. Cool palettes read as technical, calm, precise. Match the choice to the content's tone, not to a trend.

## Restrained accent

One accent color used with purpose almost always has more impact than several decorative colors used without one. If a deck has an accent for "important," it should not also have three other bright colors competing for the same attention.

## Gradients

A gradient is a legitimate tool for depth or mood, not a default background treatment. Applied to every slide regardless of content, it reads as decoration rather than a decision — see the anti-"AI presentation" list in `references/design-foundations.md`.

There is no global mandatory palette in this skill. `references/design-atlas.md` may include optional palette examples tied to specific visual directions — treat those as illustrations of a direction, never as required hex values.
