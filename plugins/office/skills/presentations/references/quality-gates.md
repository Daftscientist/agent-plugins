# Quality gates

The explicit final checklist for PREFLIGHT in `SKILL.md`. A gate passes only after a fresh visual review following the latest material changes — passing a gate from memory, before the last fix was actually previewed, doesn't count.

## Gate A — narrative

- Slide order is coherent.
- Every slide has a job.
- No accidental duplicate slides.
- The conclusion/ask (where applicable) is visible.

## Gate B — visual hierarchy

- The focal point of each slide is obvious.
- The most important content is visually loudest.
- No accidental competing focal points.

## Gate C — typography

- Type roles are used consistently across slides.
- No unreadably small type.
- Titles and body text are clearly distinguishable.
- Line lengths are reasonable, not stretched edge-to-edge.

## Gate D — geometry

- Elements align to a real grid, not near-alignment.
- Margins are consistent.
- Spacing rhythm repeats deliberately.
- No clipping or overflow.

## Gate E — imagery

- Aspect ratios are correct, nothing stretched.
- Crops support the focal point.
- Image quality is adequate at presentation scale.
- Images are relevant, not generic filler.
- Image/text contrast is sufficient where text overlays an image.

## Gate F — data

- Chart or table type fits the question being answered.
- Units are shown.
- Axes are honest (no truncated/manipulated baselines without a stated reason).
- Labels are present where needed.
- Sources are cited where the claim needs one.
- The relevant series/row is actually highlighted, not lost in the rest.

## Gate G — consistency

- Palette is consistent (or deliberately varied with a stated reason).
- Typography is consistent.
- Repeated components look the same everywhere they repeat.
- The chosen motif (if any) recurs coherently rather than mechanically or not at all.
- Image treatment is consistent.
- Slide numbering/footer, if used, is present throughout.

## Gate H — completion

- No placeholder text remains.
- No obvious TODO markers remain.
- No empty or accidental slide exists.
- No hidden accidental content (off-canvas text, leftover elements).
- No unresolved `presentation_validate` error.
- The intended final revision has been exported.

Run `presentation_validate` before this gate whenever fidelity, editability, or preservation matters, or after any substantial creation/editing pass — see `references/domoxml-fidelity.md` for how to interpret its output.
