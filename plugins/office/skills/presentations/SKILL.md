---
name: presentations
description: Create, edit, redesign, review, and repair PowerPoint presentations. Use when the user wants slides, a deck, a pitch deck, a presentation, a PPTX file, or changes to an existing presentation.
---

# Presentations

Office is an editable PowerPoint workspace: presentations contain slides, slides contain elements, and every mutation produces a new immutable revision. Author with semantic HTML and inline CSS, and use visual preview to judge the result — schemas tell you what a tool accepts, this skill teaches what to do with it.

## Choose the branch

Classify the task before acting, then read the matching reference:

```text
NEW DECK / SUBSTANTIAL REDESIGN     → references/creating.md
TARGETED EDIT TO AN EXISTING DECK   → references/editing.md
REVIEW / IMPROVE / QA A DECK        → references/reviewing.md
IMPORTED PPTX / FIDELITY CONCERNS   → references/imported-decks.md
FUNDRAISING / INVESTOR DECK         → also references/pitch-decks.md
HTML/CSS AUTHORING DETAIL NEEDED    → references/authoring-html.md
REPRESENTATION/EDITABILITY QUESTION → references/domoxml-fidelity.md
```

If the user supplied a brand, template, or example deck, that governs visual direction — follow it before anything else. When direction is genuinely open and inspiration would materially help, optionally read `references/design-atlas.md`. The atlas is a vocabulary to combine or reinterpret, never a list of permitted styles, and it is the last priority, not the first. Do not read it for a tiny edit or when a brand/template already exists.

## The process

Use all seven stages for a new deck or a substantial redesign. Skip ARC and SYSTEM for a small, targeted edit — go straight to the relevant step in `references/editing.md`. Every stage below states what "done" means; do not move on until it is true.

### ORIENT

Work out what the deck is for, who will see it, what belief or action it should produce, and whether an existing deck/template/brand is authoritative. Decide whether this is a creation, edit, redesign, or review, and which specialist references apply.

For an unfamiliar existing deck, call `presentation_inspect` before changing anything. Navigate from its outline; do not open every slide's source by default.

**Done when:** purpose, audience, branch, any authoritative existing visual constraints, and the relevant specialist references are known.

### ARC

For new decks and substantial redesigns, plan the slide-title sequence before building anything. A title should normally state the slide's takeaway, not just its topic — "Enterprise revenue grew 42% after the pricing change," not "Revenue." Each slide gets one primary communicative job, and the ordered titles alone should read as a coherent argument. Read `references/creating.md` for narrative-arc patterns, and `references/pitch-decks.md` for fundraising-specific arcs.

**Done when:** every planned slide has one clear job and the title sequence makes sense without reading slide bodies.

### SYSTEM

Before building a substantial deck, settle a coherent visual system: typography hierarchy, palette, spacing rhythm, grid/alignment logic, image treatment, chart/table treatment, and one primary recurring motif. An existing deck, brand, or template always wins over anything invented here. For open-ended design work, read `references/design-foundations.md`, and optionally `references/design-atlas.md` when inspiration is wanted.

**Done when:** the visual decisions are coherent enough that a second slide can be built without inventing a different language.

### BUILD

Create the complete first pass across every planned slide before polishing any one of them. Prefer semantic HTML, inline CSS, stable `data-office-name` aliases on elements likely to be edited again, batch slide creation in one call, `slide_duplicate` when repeating an established layout, and element-level mutations for small existing-slide changes. Build for the actual content — do not hardcode coordinates copied from an example. Do not render after every tiny operation.

**Done when:** every planned slide exists and communicates its intended idea, even if visual polish remains.

### SEE

Visual inspection is mandatory for any substantive presentation work. Render a whole-deck preview/contact sheet first and judge the deck as a sequence, then preview only the specific slides that need diagnosis. Read `references/reviewing.md` and `references/quality-gates.md`.

**Done when:** every slide has been visually considered and every material issue has been identified, or the whole deck has passed the rubric with nothing found.

### REPAIR

Fix identified issues with the smallest mutation that expresses the intent — `element_update` for text/style/attribute/small-subtree changes, `slide_update(html=...)` only for a genuine whole-slide rebuild. Re-preview affected slides after fixing them. On `REVISION_CONFLICT`, re-inspect the current revision and intentionally reapply the change rather than blindly retrying.

**Done when:** every defect found in SEE is fixed, or consciously accepted for a stated reason.

### PREFLIGHT

Run the final delivery gate from `references/quality-gates.md`: visual quality, narrative order, legibility, overflow/clipping, alignment, density, color/contrast, image treatment, data/table readability, consistency, placeholders, and — when relevant — representation/editability/preservation state. Run `presentation_validate` when fidelity/editability/preservation matters or after substantial creation/editing. Take a fresh final preview after the last material fix, then export the intended revision.

**Done when:** no unresolved error-level issue remains and the final visual pass finds no new material defect.

## Rules that apply on every path

**Stable identity.** Use only IDs Office returns. Never invent, copy, or modify `data-office-id`; use `data-office-name` for elements you expect to target again.

**Inspection discipline.** Deck outline before slide details. Structure before full source. Only read source when exact styling or a rebuild requires it.

**Editing discipline.** Use the smallest mutation that expresses the intent. Batch edits that form one coherent user intent into one call/revision; do not batch unrelated work merely to cut call count.

**Visual discipline.** One primary message per slide. Hierarchy should reveal importance at a glance. Negative space is intentional, not leftover. Repeated systems create coherence; controlled variation prevents monotony.

**Preservation discipline.** Imported source fidelity must be respected — do not casually rebuild source-only or low-editability content. See `references/domoxml-fidelity.md`.

## References

- New deck or substantial redesign → [creating](references/creating.md)
- Existing deck edit → [editing](references/editing.md)
- Visual review or improvement → [reviewing](references/reviewing.md)
- Imported PPTX / fidelity / preservation → [imported decks](references/imported-decks.md) and [domOXML fidelity](references/domoxml-fidelity.md)
- Fundraising deck → [pitch decks](references/pitch-decks.md)
- HTML/CSS source authoring detail → [HTML authoring](references/authoring-html.md)
- Open visual direction → optional [design atlas](references/design-atlas.md), grounded in [design foundations](references/design-foundations.md)
- Need composition ideas → [compositions](references/compositions.md)
- Typography question → [typography](references/typography.md)
- Color question → [color](references/color.md)
- Imagery-heavy slide → [imagery](references/imagery.md)
- Data/chart-heavy slide → [data design](references/data-design.md)
- Table-heavy slide → [tables](references/tables.md)
- Architecture/process/system visualization → [diagrams](references/diagrams.md)
- Recurring visual gesture → [motifs](references/motifs.md)
- Genre-specific conventions (board, sales, technical, etc.) → [genres](references/genres.md)
- Final delivery checklist → [quality gates](references/quality-gates.md)
- Worked examples → [examples](references/examples.md)

Do not read every reference for every deck — that defeats the point of keeping this file small. Read only the branches that apply to the task in front of you.

## Completion

The task is complete only when PREFLIGHT has been run with no unresolved error-level issue, the final export targets the intended revision, and — for anything beyond a trivial edit — the whole deck has been seen at least once after the last material change.
