# Data design

Chart and metric choices for slides where data carries the argument. Office v1 does not provide first-class native chart authoring — represent data through supported HTML/CSS/SVG, keeping it safe and editable within current capabilities (see `references/authoring-html.md`). Never instruct or assume an unsupported chart-specific tool exists.

## Decision by question

**Trend over time** — usually a line. An area chart is fine with a specific reason (e.g. emphasizing cumulative volume); don't default to it just because it looks fuller.

**Compare categories** — a bar chart, or a dot plot when precision across many categories matters more than bar-length impact.

**Composition (parts of a whole)** — a stacked bar, or a 100%-stacked bar when the relative share matters more than absolute size.

**Distribution** — a histogram, or a box/violin plot if the runtime can render it and the audience will read it correctly. Don't use a distribution chart on an audience that won't parse it — a few labeled summary stats may serve them better.

**Relationship between two variables** — a scatter plot.

**Single KPI** — often no chart at all. A large number with a comparison line communicates faster than a chart with one data point pretending to be a series.

## Pattern catalogue

Beyond the base chart-type decision above, these named patterns solve specific data-communication problems:

```text
sparkline            tiny inline trend line beside a metric, no axes
waterfall             sequential positive/negative contributions to a total
bullet chart           actual vs. target vs. range, compact and precise
slope chart             two time points connected by a line per category, shows rank change
heatmap                  matrix of values encoded by color intensity
gauge / progress         a single value against a bounded target, used sparingly
ranked bar               bars sorted by value rather than by category order, emphasizes order
dumbbell                 two values per category shown as connected points, for before/after
small multiples          the same simple chart repeated per category for fast comparison
annotated single value    one number with a callout explaining what changed and why
index-to-100              series rebased to a common starting point for fair comparison
cohort grid               retention/behavior shown as a triangular grid over time
diverging bar             bars extending in two directions from a shared zero baseline
range strip               a shaded band showing min/max or confidence range behind a line
step chart                 a line that holds value between changes rather than interpolating
```

Pick the pattern by what comparison the audience needs to make, not by which one looks most sophisticated — a sparkline next to a metric (`references/compositions.md`'s single-metric composition) often communicates faster than any full chart.

## Rules

- A chart exists to answer a specific question — know the question before choosing the chart type.
- The title should state the conclusion where the conclusion is already known (see title guidance in `references/creating.md`), not just label the axis.
- Highlight the series that matters; de-emphasize the rest rather than giving every series equal visual weight.
- Use honest axes — no truncated baselines or rescaled axes that exaggerate a trend without a stated, legitimate reason.
- Show units always.
- Cite sources when a claim's credibility depends on where the number came from, especially in pitch/board contexts (see `references/pitch-decks.md`).
- Avoid 3D chart effects — they distort perceived values and add nothing.
- Avoid a legend when direct labeling on the chart itself is clearer, which it usually is for two or three series.
- Do not chart a tiny table just to seem more visual — a two-row, two-column table of exact numbers is often clearer as a table (`references/tables.md`) or as a single-metric composition than as a chart.

## Completion check

A data slide is done when the chart type matches the question, the takeaway is stated (not just implied), the relevant series is visually distinguishable from the rest at a glance, and the axes/units/labels are honest and complete.
