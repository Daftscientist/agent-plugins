# End-to-end examples

## New deck

1. `presentation_create` with all named initial slides.
2. `presentation_preview(selection={"type":"all"})` once.
3. `slide_inspect(detail="structure")` for a dense slide.
4. Batch fixes with `element_update`.
5. Preview that slide only.
6. `presentation_validate` and `presentation_export`.

## Tiny metric refresh

Inspect the target slide, then update `arr`, `customers`, and `period` semantic names in one `element_update`. This creates one revision and preserves all untouched element IDs.

## Redesign

Inspect source, replace the slide using `slide_update(html=...)`, preview the slide, then refine with element edits. Full replacement is appropriate here because the layout is fundamentally changing.

## Imported deck

Call `presentation_open` with a supported URI, review warnings, inspect the outline, edit only the necessary elements, preview, validate preservation/editability debt, and export the desired revision.
