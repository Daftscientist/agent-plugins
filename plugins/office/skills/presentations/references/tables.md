# Tables

Treat a table as information design, not a spreadsheet dump.

## When a table is the right choice

- Exact values matter, not just the trend.
- The audience needs to compare across more than one dimension at once.
- A reader will actually reference specific cells later (pricing, specs, detailed comparisons).
- A chart would hide the detail the audience actually needs.

If none of these apply, consider whether a metric, comparison, or bar composition (`references/compositions.md`) communicates the point faster.

## Design

- Build real hierarchy into headers — column headers should be visually distinct from body cells, and any grouped/multi-level headers should show the grouping clearly.
- Align by data type: numbers right-aligned (or decimal-aligned), text left-aligned.
- Put units in the header, not repeated in every cell.
- Use subtle rules (thin, low-contrast lines) rather than heavy borders around every cell.
- Highlight the row or column that matters to the point being made — a comparison table with no highlighted "you are here" or "winner" column often fails to make its point despite having all the right data.
- Avoid excessive borders — a fully gridded table with a border on every cell usually reads as a spreadsheet screenshot, not a designed slide.
- Use whitespace between rows/columns instead of only borders to create separation.
- Avoid tiny text — a table dense enough to need 10px text at presentation scale needs to be simplified, split, or moved to an appendix (see the appendix composition in `references/compositions.md`), not shrunk further.

## Alternatives

When a table's content is really driving toward one conclusion, consider converting it into:

```text
a single metric        one number is the whole point
a comparison            two states/options being weighed
a bar chart             magnitude comparison across categories
a ranked list           order matters more than exact values
```

A table is the right tool when the audience needs the grid itself, not just the conclusion it implies.
