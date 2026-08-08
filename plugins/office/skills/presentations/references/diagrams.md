# Diagrams

Turning a system, process, or relationship into a slide. Represent diagrams through supported HTML/CSS/SVG (`references/authoring-html.md`) — do not assume native diagramming tools exist.

## Diagram families

```text
flow            steps connected by directional arrows
process          discrete sequential steps, often numbered
architecture     technical components and their connections
network          peer relationships without a strict hierarchy
layers           horizontal bands stacked by dependency
stack            similar to layers, emphasizing what sits on what
ecosystem        a hub with surrounding independent participants
funnel           narrowing sequence proportional to volume
flywheel         a reinforcing cycle
decision tree    branching choices and outcomes
swimlane         parallel tracks (e.g. by team/system) over shared stages
timeline         events plotted against real time
roadmap          planned work across phases/quarters
matrix           items classified on two independent axes
hierarchy        a tree of reporting/composition relationships
pipeline         data or work moving through discrete transformation stages
```

Choosing the right family is a decision, not an aesthetic pick — a flywheel drawn for a linear process, or a hierarchy drawn for a genuinely peer-to-peer network, misleads the reader about how the system actually works. Match the family to the real shape of the relationship (see also composition entries in `references/compositions.md` for the containing slide structure).

## Rules

- Define a reading direction (left-to-right, top-to-bottom) and hold it throughout the diagram.
- Reduce line crossings — if two connections must cross, make that crossing visually clear rather than ambiguous.
- Align nodes to a grid; near-aligned nodes read as sloppy, not organic.
- Label relationships, not just nodes, when the relationship itself carries meaning (e.g. "depends on" vs. "informs").
- Group related nodes by a visible boundary (a subtle box or shared background) rather than relying on proximity alone.
- Highlight the path or node that matters to the current point — a diagram with fifteen equally weighted boxes forces the reader to find the point themselves.
- Do not make every box equally loud; the diagram should still have a hierarchy.
- Use text inside nodes sparingly — a node label is not the place for a full sentence.
- Show the system boundary explicitly when internal/external distinction matters (e.g. what's inside vs. outside a security perimeter).

## Technical style variants

```text
clean corporate         rounded rectangles, restrained palette, sans labels
blueprint                 thin white/cyan lines on dark, technical annotation
engineering schematic      precise lines, mono labels, grid-aligned
developer / terminal       monospace throughout, dark background, minimal color
systems map                 dense but organized, small mono metadata labels
```

Match the variant to the deck's overall system (`references/design-foundations.md`, `references/design-atlas.md`) rather than picking one in isolation — a blueprint diagram inside an otherwise warm editorial deck will look like it wandered in from a different presentation.
