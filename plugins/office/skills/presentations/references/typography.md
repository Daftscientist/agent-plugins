# Typography

A type system, not a font list — the goal is a working hierarchy of roles, applied consistently.

## Roles

Define these roles for a deck rather than styling each slide's text ad hoc:

```text
display/title      largest, used sparingly (covers, hero statements)
slide title        the per-slide headline role
section label       small, used for section/category markers
body                 the default reading size
supporting label     secondary/caption-weight text near content
data label           numbers/units inside charts and tables
caption/source       smallest, attribution and footnotes
monospace/technical  code, metadata, coordinates, technical labels
```

Every slide's text should map cleanly onto one of these roles. If a slide needs a new role you haven't defined yet, that's a sign the type system is underspecified — fix the system, don't invent a one-off size.

## Principles

- Make hierarchy explicit: a reader should be able to tell role from role by scale and weight alone, without reading the words.
- Control line length — very wide or very narrow text blocks both hurt legibility.
- Build real contrast between roles (size, weight, sometimes family) rather than nudging one role slightly bigger than another.
- Stay consistent: the same role should look the same on every slide it appears on.
- Avoid tiny type; if something must be small (footnotes, sources), keep it legible at the intended viewing distance rather than as small as it can technically go.
- Use weight, size, and letter-spacing intentionally, not by habit — each choice should be doing a job.
- Type itself can be the visual: an oversized numeral or a strong display headline can replace the need for a supporting graphic entirely.

## Treatments

A treatment is a coherent typographic personality applied across roles, not a single font choice:

```text
oversized display        huge numerals/words as the primary visual
editorial serif           serif display + serif or sans body, magazine feel
Swiss grotesk              grotesk sans throughout, precise and neutral
mono technical             monospace for labels/metadata, sans for body
condensed display          narrow display face for high-impact headlines
wide geometric sans         geometric sans, generous tracking
humanist sans               warm, approachable sans throughout
luxury serif                refined serif display, restrained body
all-caps label system       small caps/all-caps used only for labels, never body
mixed serif/sans            serif for display, sans for body (or reversed) as a deliberate contrast
single-family disciplined   one type family for everything, hierarchy from weight/size alone
compressed headline         tightly tracked, tall display type for maximum impact in little space
wide tracked caps           generously letter-spaced all-caps used as a quiet, confident label system
variable-weight display      one word or phrase spanning multiple weights within itself
oversized numeral display    a numeral treated as the dominant graphic, text subordinate to it
slab serif technical         slab serif for headlines paired with mono for data, engineering-adjacent feel
italic emphasis system       a consistent italic cut used only for emphasis, never as a base style
```

Pick one treatment per deck and hold it — mixing treatments slide to slide reads as inconsistency, not variety.

## Font selection

An existing template or brand's fonts always win over anything chosen here. When font choice is genuinely open: choose by tone and readability for the audience, use fonts actually available to the runtime/export pipeline, and provide sensible fallbacks. Never make a deck depend on a font that might not be available when it's rendered or exported — a design that only works with one exact unavailable font isn't a design decision, it's a fragility.
