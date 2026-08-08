# Office Presentation Skill System Redesign
## Implementation brief for the `agent-plugins` repository

**Status:** implementation handoff  
**Target plugin:** `plugins/office`  
**Scope:** replace and dramatically improve the Office presentation Agent Skill package only  
**Out of scope:** changing the Office MCP tool contract, storage model, domOXML integration, resource model, server architecture, or any of the now-stable v1 implementation unless a skill test exposes a genuine documentation/capability mismatch  
**Primary goal:** make a weak/small agent reliably create, edit, review, and repair genuinely good PowerPoint presentations using the existing Office MCP, while keeping routing context small and making a very large body of presentation expertise available through progressive disclosure

---

# 0. Read this first

The existing Office MCP implementation is substantially more mature than the current skill layer.

The current skill package is valid but underpowered:

```text
plugins/office/skills/presentations/
├── SKILL.md
└── references/
    ├── authoring.md
    ├── capabilities.md
    ├── editing.md
    └── examples.md
```

Its main `SKILL.md` is primarily a tool-selection/workflow cheat sheet:

- inspect before editing;
- use structure before source;
- prefer element updates;
- use slide replacement only for rebuilds;
- preview;
- validate;
- export.

That is useful, but much of it duplicates information already available from the MCP tool descriptions and schemas.

The redesigned skill package must instead teach the agent the expertise that schemas cannot encode:

- how to reason about the purpose and audience of a deck;
- how to form a narrative arc;
- how to choose slide types;
- how to create visual hierarchy;
- how to manage density;
- how to choose typography;
- how to compose a slide;
- how to use imagery;
- how to design data slides;
- how to design tables and diagrams;
- how to use motifs and visual rhythm;
- how to edit an existing deck without destroying its language;
- how to review a whole deck visually;
- how to handle imported domOXML fidelity/preservation states;
- how to make pitch decks stage-appropriate;
- how to seek optional visual inspiration without becoming a template/preset machine;
- how to know when work is actually complete.

The final design must give the model a small mental model at the top and a large body of optional knowledge below it.

---

# 1. Normative constraints

Before editing anything, read:

```text
/AGENTS.md
/plugins/office/AGENTS.md
/plugins/office/DESIGN.md
/plugins/office/API_REFERENCE.md
```

The skill rewrite must remain consistent with the actual Office implementation.

## 1.1 Agent Plugins

The Office package targets Agent Plugins 1.0.0.

Agent Plugins discovers Agent Skills as immediate child directories under:

```text
plugins/office/skills/
```

Each discovered skill must contain:

```text
SKILL.md
```

and conform to the Agent Skills specification.

Do not invent plugin-level skill configuration in `plugin.json`.

Do not move skills outside `skills/`.

Do not introduce client-specific skill semantics into the portable core.

## 1.2 Agent Skills

Follow the current Agent Skills specification:

https://agentskills.io/specification

Important consequences:

- `name` is required and must match the skill directory.
- `description` is required and is always part of skill-discovery context.
- A skill may include `scripts/`, `references/`, `assets/`, and arbitrary additional package files.
- The complete `SKILL.md` body is loaded when the skill activates.
- References/assets are intended for on-demand progressive disclosure.
- Keep the main `SKILL.md` focused; the spec recommends under 500 lines / roughly <5000 tokens.
- Keep references focused.
- Use relative references from the skill root.
- Avoid deep chains where one reference merely points to another reference which points to another.

## 1.3 Do not rely on non-portable frontmatter

Do not make correctness depend on client-specific fields such as:

```yaml
disable-model-invocation: true
```

unless Agent Skills formally standardizes them in the version targeted by the repository.

This plugin is intentionally portable.

---

# 2. Source material and what to learn from it

This task is informed by four external/reference sources plus the existing Office implementation.

Do not blindly copy any source.

Extract useful design reasoning, rewrite it for this plugin, and keep Office's actual tool/capability model authoritative.

## 2.1 Matt Pocock — writing for agents

Source materials supplied with the task:

```text
SKILL.md           # "writing-for-agents"
SKILL-MECHANICS.md # skill-specific mechanics
```

Apply these principles throughout the redesign.

### Context pointers

The wording of the skill description and every reference pointer controls whether the agent reaches the right material.

Every pointer must do two things:

1. state what the referenced material contains;
2. state the distinct task branch(es) that should trigger reading it.

Avoid synonym soup.

Good:

```text
For a fundraising deck, read `references/pitch-decks.md` before planning the slide sequence.
```

Bad:

```text
See pitch-decks.md for more information.
```

### Context load vs cognitive load

Every additional model-discoverable skill adds an always-loaded description.

Do not split one presentation workflow into many discovered skills simply because different reference topics exist.

A split must earn its routing cost.

### Information hierarchy

Put information at the highest level where it is consistently needed:

1. **in-file steps** — behavior required on nearly every run;
2. **in-file reference** — compact rules needed by many branches;
3. **disclosed references** — branch-specific knowledge loaded only when needed.

The top-level skill must remain legible enough that the model can hold the process in its head.

### Completion criteria

Every major procedural step needs a checkable completion criterion.

Avoid:

```text
Review the presentation.
```

Prefer:

```text
Review the whole-deck contact sheet. The step is complete only when every visibly weak slide has been identified and classified, or the entire deck has been explicitly checked with no material issue found.
```

### Leading words

Use a small set of memorable existing concepts to anchor behavior.

For this skill, use:

```text
ORIENT
ARC
SYSTEM
BUILD
SEE
REPAIR
PREFLIGHT
```

These are process anchors, not decorative headings.

### Positive instructions

Prefer describing desired behavior over a wall of prohibitions.

Use hard `MUST NOT` rules only for genuine correctness/safety invariants.

### Single source of truth

Do not copy tool schemas or capability matrices into several skill files.

The environment and `API_REFERENCE.md` are already sources of truth.

Skill references should document:

- expertise;
- process;
- unwritten conventions;
- failure modes;
- reasons;
- decision rules.

Not caches of every enum.

---

# 3. External presentation references

Use the following projects for research/inspiration.

## 3.1 OfficeCLI presentation skill

https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/officecli-pptx

Useful concepts to adapt:

- one communicative idea per slide;
- explicit visual quality floor;
- visual preview as a core QA mechanism;
- whole-deck QA rather than assuming first render is correct;
- typography/layout/spacing discipline;
- use of a coherent recurring visual motif;
- inspect broadly first, narrow only when needed.

Do not copy OfficeCLI command syntax.

Do not introduce OfficeCLI concepts into the MCP surface.

Do not copy fixed centimeter coordinates or CLI recipes.

## 3.2 OfficeCLI pitch-deck skill

https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/officecli-pitch-deck

Useful concepts:

- fundraising is a genuinely specialized branch;
- funding stage materially changes narrative emphasis;
- vertical/business model changes which proof matters;
- a pitch deck is not just a generic presentation with "Problem / Solution / Market" labels;
- data honesty and metric appropriateness need explicit QA.

Do not blindly copy their numerical SaaS heuristics as universal truths.

Any time-sensitive funding/market heuristics must be:

- clearly labelled as heuristics;
- kept modest;
- preferably framed around decision principles rather than magic thresholds.

## 3.3 OfficeCLI Morph skill

https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/morph-ppt

The key lesson for this redesign is its **reference-library lookup philosophy**:

- inspiration library is on-demand;
- design references are not templates;
- borrow design logic;
- do not copy fixed coordinates;
- use mood/palette/gesture as inspiration;
- build for current content.

Do not implement Morph behavior in this skill unless the Office MCP genuinely supports it.

Morph/animation may deserve a separate discovered skill in the future because it has a distinct workflow and distinct lifecycle/verification rules.

## 3.4 OfficeCLI Morph 3D skill

https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/morph-ppt-3d

Use only as evidence for a future splitting rule:

A capability should become another discovered skill when it introduces a materially different planning/execution/verification process.

Do not add 3D instructions for unsupported Office v1 functionality.

## 3.5 `corazzon/pptx-design-styles`

https://github.com/corazzon/pptx-design-styles

Useful as a seed taxonomy of visual languages.

Its collection includes directions such as:

```text
Glassmorphism
Neo-Brutalism
Bento Grid
Dark Academia
Gradient Mesh
Claymorphism
Swiss International
Aurora Neon Glow
Retro Y2K
Nordic Minimalism
Typographic Bold
Duotone Color Split
Monochrome Minimal
Cyberpunk Outline
Editorial Magazine
Pastel Soft UI
Dark Neon Miami
Hand-crafted Organic
Isometric 3D Flat
Vaporwave
Art Deco Luxe
Brutalist Newspaper
Stained Glass Mosaic
Liquid Blob Morphing
Memphis Pop Pattern
Dark Forest Nature
Architectural Blueprint
Maximalist Collage
SciFi Holographic Data
Risograph Print
```

The repo is useful as inspiration but its behavioral model is NOT our target.

Do not make Office:

```text
pick a style
→ obey exact font
→ obey exact HEX
→ obey exact layout
```

That creates a preset/template ceiling.

Our design atlas must remain optional and generative.

---

# 4. Primary architectural decision: keep ONE discovered presentation skill

Do **not** replace the current skill with five overlapping discovered skills such as:

```text
building-presentations
editing-presentations
presentation-design
reviewing-presentations
imported-presentations
```

That would put multiple presentation-routing descriptions into always-loaded context.

Instead keep:

```text
plugins/office/skills/presentations/
```

as the one primary general presentation skill.

Use references for the internal branches.

Future capabilities may gain separate discovered skills only when they have an independent trigger and a genuinely different procedure, e.g.:

```text
morph-presentations
3d-presentations
```

if/when Office actually supports those features.

---

# 5. Target package layout

Replace the current presentation skill contents with approximately this structure:

```text
plugins/office/skills/presentations/
├── SKILL.md
│
├── references/
│   ├── creating.md
│   ├── editing.md
│   ├── reviewing.md
│   ├── imported-decks.md
│   ├── pitch-decks.md
│   │
│   ├── authoring-html.md
│   ├── domoxml-fidelity.md
│   │
│   ├── design-foundations.md
│   ├── design-atlas.md
│   ├── compositions.md
│   ├── typography.md
│   ├── color.md
│   ├── imagery.md
│   ├── data-design.md
│   ├── tables.md
│   ├── diagrams.md
│   ├── motifs.md
│   ├── genres.md
│   │
│   ├── quality-gates.md
│   └── examples.md
│
├── assets/
│   └── design-atlas/
│       ├── README.md
│       ├── visual-languages/
│       ├── compositions/
│       ├── typography/
│       ├── imagery/
│       ├── data/
│       ├── diagrams/
│       └── motifs/
│
└── SOURCES.md
```

Important:

- `SKILL.md` points directly to the relevant reference files.
- References should not require long nested chains.
- `design-atlas.md` is itself useful as a compact catalogue/router; it must not merely be an index whose only purpose is sending the model down another tree.
- Assets are optional visual examples, not mandatory templates.
- Do not add scripts unless a clear need appears; the MCP already provides execution/validation.

---

# 6. Replace the current `SKILL.md`

The current skill description is too implementation-centric:

> Create, inspect, edit, preview, validate, and export PowerPoint presentations using the Office MCP tools and domOXML-backed HTML/CSS authoring.

That mostly describes the MCP.

Use a task-oriented description.

Recommended frontmatter:

```yaml
---
name: presentations
description: Create, edit, redesign, review, and repair PowerPoint presentations. Use when the user wants slides, a deck, a pitch deck, a presentation, a PPTX file, or changes to an existing presentation.
---
```

Do not stuff a list of every reference topic into the description.

The description is a routing pointer, not a miniature manual.

---

# 7. Required top-level `SKILL.md` process

The complete `SKILL.md` should be concise enough that an agent can hold the workflow at once.

Aim roughly:

```text
150–300 lines
<5000 tokens
```

It should contain:

1. purpose;
2. branch routing;
3. the seven leading-word stages;
4. essential invariant rules;
5. concise Office-tool navigation guidance;
6. direct reference pointers;
7. completion criteria.

It must **not** become a 700-line design textbook.

---

# 8. Proposed `SKILL.md` conceptual skeleton

The implementation agent should write a polished version of the following.

## Presentations

Office is an editable PowerPoint workspace. Use its structured deck/slide/element model to create and change presentations, and use visual preview to judge the result.

### Choose the branch

Before acting, classify the task:

```text
NEW / SUBSTANTIAL REDESIGN
→ read references/creating.md

TARGETED EDIT TO AN EXISTING DECK
→ read references/editing.md

REVIEW / IMPROVE / QA
→ read references/reviewing.md

IMPORTED PPTX OR PRESERVATION/FIDELITY CONCERNS
→ read references/imported-decks.md

FUNDRAISING / INVESTOR DECK
→ also read references/pitch-decks.md

HTML/CSS AUTHORING DETAILS NEEDED
→ read references/authoring-html.md

DOMOXML REPRESENTATION / EDITABILITY / PRESERVATION ISSUE
→ read references/domoxml-fidelity.md
```

For open-ended visual direction:

```text
If the user supplied a brand, template, example deck, or explicit aesthetic, follow that first.

When visual direction is genuinely open and inspiration would materially improve the deck, optionally read references/design-atlas.md.

The atlas is a vocabulary of ideas, not a list of permitted styles. Combine, reinterpret, or ignore entries to fit the content.
```

### ORIENT

Understand:

- what the deck is for;
- who will see it;
- what action/belief it should produce;
- whether an existing deck/template/brand is authoritative;
- whether this is a creation, edit, redesign, or review;
- whether specialist references are required.

For unfamiliar existing decks:

```text
presentation_inspect
```

before modifying.

Do not open every slide source by default.

**Done when:** the purpose, audience, branch, authoritative existing visual constraints, and relevant specialist references are known.

### ARC

Use for new decks and substantial redesigns.

Plan the slide-title sequence before building.

A title should normally state the slide's message/takeaway rather than merely its topic.

Each slide should have one primary communicative job.

The titles alone should form a coherent argument/story.

Read `references/creating.md` for narrative planning and `references/pitch-decks.md` for fundraising-specific arcs.

**Done when:** every planned slide has one clear job and the ordered title sequence makes sense without slide body copy.

For a tiny edit, skip ARC.

### SYSTEM

Before building a substantial deck, derive or choose a coherent visual system:

- typography hierarchy;
- palette;
- spacing rhythm;
- grid/alignment logic;
- image treatment;
- chart/table treatment;
- one primary recurring motif or visual gesture.

Existing deck/brand/template conventions win.

For open-ended design work, use `references/design-foundations.md` and optionally `references/design-atlas.md`.

**Done when:** visual decisions are coherent enough that a second slide can be built without inventing a completely different language.

### BUILD

Create the complete first pass.

Prefer:

- semantic HTML;
- inline CSS;
- stable semantic aliases via `data-office-name`;
- batch slide creation where suitable;
- `slide_duplicate` when repeating an established layout;
- element-level mutations for small existing-slide changes.

Build for the current content, not around hardcoded coordinates copied from an example.

Do not repeatedly render after every tiny operation.

**Done when:** every planned slide exists and communicates its intended idea, even if visual polish remains.

### SEE

Visual inspection is mandatory for substantive presentation work.

Use a whole-deck preview/contact sheet first.

Judge the deck as a sequence before diving into individual slides.

Then preview only specific slides that need diagnosis.

Read `references/reviewing.md` and `references/quality-gates.md`.

**Done when:** every slide has been visually considered and every material issue has either been identified or the deck has passed the complete visual rubric.

### REPAIR

Fix identified issues using the smallest appropriate mutation.

Prefer:

```text
element_update
```

for text/style/attribute/small subtree changes.

Use:

```text
slide_update(html=...)
```

for genuine whole-slide rebuilds.

Re-preview affected slides.

If a `REVISION_CONFLICT` occurs, re-inspect the current revision and intentionally reapply the change.

**Done when:** all defects found in SEE are fixed or consciously accepted for a defensible reason.

### PREFLIGHT

Run the final delivery gate.

Check:

- visual quality;
- narrative order;
- legibility;
- overflow/clipping;
- alignment;
- density;
- color/contrast;
- image treatment;
- data/table readability;
- consistency;
- placeholders/unfinished content;
- representation/editability/preservation when relevant.

Run:

```text
presentation_validate
```

when fidelity/editability/preservation matters or after substantial creation/editing.

Use a fresh final preview after the last material fix.

Export the intended revision.

**Done when:** no unresolved error-level issue remains and the final visual pass finds no new material defect.

---

# 9. Essential rules that belong in `SKILL.md`

Keep only rules that are broadly live.

## Stable identity

- Use IDs returned by Office.
- Never invent/copy/modify `data-office-id`.
- Use `data-office-name` for meaningful future edit targets.

## Inspection discipline

- deck outline before slide details;
- structure before full source;
- only inspect source when needed for exact styling/rebuild.

## Editing discipline

- smallest mutation that expresses intent;
- batch related changes;
- one user intent → one coherent revision where practical.

## Visual discipline

- one primary message per slide;
- title communicates takeaway where appropriate;
- hierarchy must reveal importance rapidly;
- negative space is intentional;
- repeated systems create coherence;
- controlled variation prevents monotony.

## Preservation discipline

Imported source fidelity must be respected.

Do not casually rebuild source-only or low-editability content.

---

# 10. `references/creating.md`

Purpose:

> Planning and building a new deck or substantially redesigning one.

This file should contain procedure + decision rules.

Recommended sections:

## 10.1 Audience and purpose

Questions the agent should resolve from context:

```text
Who is the audience?
What do they already know?
What should they believe/decide/do afterward?
Is the presentation live, async, or both?
How much explanation belongs on-slide vs spoken?
```

Do not force the user through a questionnaire when enough can be inferred.

## 10.2 Narrative arc

Teach:

- sequence before layout;
- message titles;
- tension → evidence → implication;
- grouping related slides through sections rather than mega-slides;
- remove slides that repeat the same job.

Useful general arcs:

```text
context → problem → implication → response → proof → decision
question → evidence → conclusion → next step
status → change → impact → action
vision → opportunity → system → proof → ask
```

They are patterns, not mandatory templates.

## 10.3 One-job slides

A slide may contain several pieces of evidence, but they should support one main message.

Symptoms of a multi-job slide:

- title needs "and";
- two unrelated focal areas;
- two unrelated conclusions;
- audience cannot tell what to look at first.

## 10.4 Title quality

Prefer:

```text
"Enterprise revenue grew 42% after the pricing change"
```

over:

```text
"Revenue"
```

when the takeaway is known.

Topic labels remain appropriate for:

- section dividers;
- reference/appendix;
- navigation.

## 10.5 Slide-count discipline

Do not target a fixed magic count.

Use as many slides as required to keep each slide coherent.

A live deck can use more, lighter slides than an async memo-deck.

## 10.6 First-pass behavior

Build the entire narrative before obsessively polishing one slide.

This prevents slide 1 receiving 70% of the design effort while the rest remain unfinished.

## 10.7 Completion criterion

Creation planning is complete only when:

- audience/purpose are understood;
- slide-title sequence exists;
- every slide has one job;
- no obvious duplicate/redundant slide remains;
- specialist branch references have been consulted.

---

# 11. `references/editing.md`

Replace the current thin editing reference with a strong "preserve" procedure.

Leading concept:

```text
PRESERVE
```

## 11.1 Existing deck is the design system

Before editing:

- inspect the deck outline;
- inspect neighboring/relevant slides;
- derive local typography/spacing/palette/layout behavior;
- respect the deck unless user explicitly requests redesign.

## 11.2 Surgical edits

For tiny changes:

```text
slide_inspect(detail="structure")
→ element_update
→ slide preview
```

Do not read/rewrite the entire slide if unnecessary.

## 11.3 Adding matching slides

Prefer:

```text
slide_duplicate
```

of the closest conceptual/layout sibling, then replace its content.

If no suitable sibling exists, derive layout behavior from the deck before creating a new slide.

## 11.4 Batch semantics

Batch:

- one metric refresh;
- one set of copy changes;
- one coordinated styling fix.

Do not batch unrelated work merely to reduce calls.

## 11.5 Preserve untouched content

An edit request is not permission to:

- restyle every slide;
- rewrite copy;
- reorder the narrative;
- normalize every difference.

Positive target:

> Change the requested surface while preserving established design and unrelated content.

## 11.6 When full slide replacement is appropriate

Use full `slide_update(html=...)` when:

- user requested redesign;
- layout is fundamentally wrong;
- imported/legacy structure cannot support intended change and rebuilding is safe;
- several related changes mean surgical mutation is more fragile than reconstruction.

## 11.7 Completion criterion

An edit is complete when:

- requested change is visible;
- established deck language remains coherent;
- unrelated content is unchanged;
- affected slide has been re-previewed;
- no new visual defect was introduced.

---

# 12. `references/reviewing.md`

Purpose:

> Critical visual and narrative review.

This is a flat expert rubric plus a short procedure.

## 12.1 Review procedure

1. inspect presentation outline;
2. render whole-deck contact sheet;
3. review sequence and consistency;
4. identify suspect slides;
5. inspect those slides individually;
6. classify issues;
7. repair;
8. run fresh final whole-deck pass.

Do not edit slide 1 immediately upon spotting its first issue before seeing the rest of the deck.

## 12.2 Review dimensions

### Narrative

- Does slide order tell a coherent story?
- Does each slide advance it?
- Are there repetitions?
- Are transitions between ideas comprehensible?

### Purpose

- Can the main point of each slide be stated in one sentence?
- Is the focal evidence actually supporting that point?

### Hierarchy

- Is the first thing the eye sees the most important thing?
- Can the slide be understood rapidly?
- Are competing focal points fighting?

### Legibility

- text size;
- line length;
- contrast;
- labels;
- footnotes;
- dense tables.

### Density

- too much content;
- needless card grids;
- excessive labels;
- every pixel filled;
- insufficient negative space.

### Alignment

- edges align;
- grids are intentional;
- baselines/columns feel coherent;
- elements are not "almost aligned."

### Rhythm

- repeated spacing values;
- repeated typography behavior;
- deliberate slide-to-slide variation;
- no accidental random layout switching.

### Contrast

Use:

- scale;
- weight;
- tone;
- position;
- whitespace;
- shape.

Not only color.

### Imagery

- quality;
- crop;
- aspect ratio;
- relevance;
- consistency;
- no stretched logos/screenshots.

### Data

- chart choice;
- axis honesty;
- units;
- labels;
- important series highlighted;
- no decorative chart junk.

### Tables

- readable;
- meaningful column hierarchy;
- comparison highlighted;
- avoid spreadsheet screenshot aesthetic unless intentional.

### Consistency

- palette;
- title positioning;
- margins;
- motif;
- footer/page numbering where used;
- icon/image treatment.

### Technical

- overflow;
- clipping;
- off-slide objects;
- missing images;
- hidden accidental content;
- placeholder text;
- unresolved warnings.

## 12.3 Completion criterion

Review is complete only when **every slide** has been visually accounted for.

"Looks generally good" is not sufficient.

---

# 13. `references/imported-decks.md`

Purpose:

> Handling existing PPTX imported through domOXML where editability/preservation matters.

Do not merely repeat enum definitions.

Teach operational behavior.

## 13.1 Representation decision table

### `native` + semantic editability

Normal editing path.

Prefer element-level edits.

### `decomposed` / components

Content is editable but may represent one source object as several components.

Understand grouping before changing structure.

### `hybrid`

Some content remains semantic/native while other content relies on layered/preserved representation.

Edit the semantic parts surgically.

Validate afterward.

### `layered` / `element_layer`

Appearance is preserved through layers.

Visual edits may be possible, but semantic meaning is reduced.

Treat reconstruction carefully.

### `rasterized`

Appearance is image-like.

Text/object editing is not meaningfully available.

Rebuild only if user wants a replacement.

### `approximated`

Expect visual/fidelity differences.

Inspect preview and decide whether approximation is acceptable.

### `failed`

Do not pretend content is editable.

Repair/rebuild intentionally or explain limitation.

## 13.2 Source retention

Teach:

```text
not_required
attached
detached
ignored
lost
```

by consequences.

The agent should understand when editing may make safe export impossible.

## 13.3 Untouched imported deck

If no content edit is required and Office can preserve exact original bytes, do not force conversion/reconstruction.

## 13.4 Completion criterion

Imported-deck work is complete when:

- target content is changed as requested;
- untouched unsupported content remains preserved where possible;
- validation/preservation warnings have been reviewed;
- no fidelity debt is silently hidden.

---

# 14. `references/authoring-html.md`

This replaces current `authoring.md`.

Technical but compact.

Must stay aligned with actual server sanitizer/domOXML behavior.

Cover:

- semantic HTML roots;
- inline CSS;
- meaningful containers;
- headings/paragraphs/lists/images/tables;
- safe inline SVG if supported by current Office implementation;
- `data-office-name`;
- server-owned `data-office-id`;
- no active content;
- no remote rendering dependency;
- bounded data images;
- supported fragment/root expectations.

Do not copy every CSS property list if the runtime is source of truth.

Include several **small reusable HTML recipes**, e.g.:

```text
hero title
split content/image
metric
comparison
simple table
process row
```

Examples should illustrate technique, not become rigid templates.

---

# 15. `references/domoxml-fidelity.md`

This is the authoritative skill-level explanation of:

- representation categories;
- editability categories;
- source-retention categories;
- how to interpret validation;
- when to preserve vs reconstruct;
- why an apparently correct preview may still contain preservation debt.

Do not duplicate it in `imported-decks.md`; the latter should point directly here only if additional enum/fidelity detail is necessary.

Because deep reference chains are discouraged, `SKILL.md` should also directly mention this file for fidelity questions.

---

# 16. `references/pitch-decks.md`

This must be genuinely useful.

Do not make it a generic 12-slide startup template.

## 16.1 First decision: stage and context

Determine:

- seed/pre-seed;
- Series A;
- Series B;
- later growth;
- bridge/extension;
- other/unclear.

Also determine business type:

```text
B2B SaaS / enterprise
consumer
marketplace/network
hardware
deep tech
biotech/clinical
services
other
```

The point is not to force exact financial thresholds.

The point is that **what counts as proof changes with maturity and business model**.

## 16.2 Narrative weighting

Early stage:

- problem insight;
- founder insight;
- product;
- why now;
- early proof.

Later stage:

- growth;
- retention;
- unit economics;
- scalability;
- defensibility;
- financial plan.

Deep tech/biotech:

- technical milestone;
- validation;
- regulatory/scientific path;
- runway to milestone.

Marketplace:

- liquidity;
- take rate;
- cohort behavior;
- network effects.

## 16.3 Evidence honesty

Teach:

- do not invent traction;
- show meaningful denominators;
- label estimates;
- source market claims;
- avoid manipulated axes;
- separate actual vs forecast.

## 16.4 The ask

A fundraising deck must make the ask concrete:

- amount;
- use of funds;
- runway/milestones;
- what the round makes true.

## 16.5 Pitch-specific review

Check:

- stage appropriate;
- evidence appropriate;
- product/traction balance;
- market sizing logic;
- team relevance;
- financial claims;
- ask;
- no generic "pitch-deck boilerplate" slide that contributes nothing.

---

# 17. Design system philosophy

The design references are the biggest expansion.

The skill must not teach:

```text
there are 30 styles
pick exactly one
follow exact fonts/colors/layout
```

Instead teach design as a **multi-dimensional system**.

A deck's visual direction can combine:

```text
VISUAL LANGUAGE
+ COMPOSITION
+ TYPOGRAPHY
+ COLOR
+ IMAGE TREATMENT
+ INFORMATION DESIGN
+ MOTIF
+ GENRE CONSTRAINTS
```

This lets the agent synthesize:

```text
Swiss × technical schematic × monochrome × oversized numerals
```

or:

```text
warm editorial × documentary photography × serif display × asymmetrical composition
```

without needing a predeclared preset.

---

# 18. `references/design-foundations.md`

This is the core expert visual-design reference.

Use compact leading concepts.

## Hierarchy

Importance should be visible.

Tools:

- scale;
- position;
- weight;
- contrast;
- whitespace;
- isolation.

A slide with four equally loud elements has no hierarchy.

## Composition

Layout is a relationship between elements, not a collection of boxes.

Teach:

- focal region;
- supporting region;
- balance;
- asymmetry;
- grid;
- edge alignment;
- controlled overlap;
- spatial grouping.

## Whitespace

Whitespace communicates:

- grouping;
- separation;
- hierarchy;
- premium/quiet tone;
- focus.

It is not unused capacity to fill.

## Rhythm

Coherence comes from repeated:

- margins;
- spacing;
- type roles;
- alignment;
- motif;
- image treatment.

Variation should be controlled at the composition level.

## Contrast

Contrast should answer:

> what matters first?

Use more than color.

## Restraint

One strong gesture often beats six decorative ideas.

## Motif

Choose a recurring design gesture when appropriate, such as:

- edge labels;
- hairline grid;
- oversized section numerals;
- cropped geometry;
- accent bar;
- technical annotation;
- image frame treatment.

Use it consistently but not mechanically.

---

# 19. `references/design-atlas.md`

This is the optional inspiration atlas.

It must explicitly begin with wording like:

> This atlas is optional inspiration. It is not a preset library, template catalogue, whitelist, or required starting point. Existing brand/template/user direction always wins. When direction is open, use entries as vocabulary: borrow, combine, reinterpret, or ignore them. Design for the content rather than copying fixed layouts, coordinates, fonts, or colors.

## 19.1 Atlas role

The atlas should help answer:

```text
What kind of visual language could fit this material?
What movements/styles can I borrow from?
What combinations could feel distinctive?
What visual vocabulary matches the audience?
```

It should **not** answer:

```text
Which of the allowed 30 templates should I use?
```

## 19.2 Minimum breadth

Target at least:

```text
60 visual languages / movements / contemporary design directions
```

Across substantially different categories.

At least 20 should go beyond the corazzon 30-style seed list.

Do not stop at trendy UI aesthetics.

## 19.3 Required seed directions

Include and rewrite useful entries for:

### Modernist / systematic

```text
Swiss / International Typographic
Bauhaus
De Stijl
Constructivist
Modern corporate modernism
Japanese minimalism
Nordic minimalism
Monochrome minimal
Museum / gallery catalogue
Institutional modern
```

### Editorial / print

```text
Editorial magazine
Newspaper
Brutalist newspaper
Luxury editorial
Annual-report editorial
Bookish / literary
Dark academia
Risograph
Screenprint
Zine
Independent publishing
```

### Bold / graphic

```text
Neo-Brutalism
Typographic bold
Duotone
Memphis
Maximalist collage
Pop-art influenced
Geometric poster
Color-block
High-contrast monochrome
```

### Digital / contemporary UI-derived

```text
Bento grid
Glassmorphism
Soft UI / restrained neumorphism
Gradient mesh
Clay-like / soft dimensional
Dashboard / product UI
Modern SaaS
```

### Futurist / technical

```text
Architectural blueprint
Engineering schematic
Cyberpunk outline
HUD / interface
Sci-fi holographic data
Isometric technical
Wireframe / CAD
Scientific instrumentation
Terminal / developer
Security operations / SOC
```

### Retro / cultural

```text
Retro Y2K
Vaporwave
Synthwave / neon Miami
Art Deco
Mid-century modern
70s editorial
80s geometric
90s rave
early-web / webcore
```

### Organic / atmospheric

```text
Hand-crafted organic
Dark forest
Botanical
Earth-tone natural
Liquid organic
Biotech organic-tech
Documentary photographic
Soft humanist
```

### Luxury / refined

```text
Art Deco luxe
Quiet luxury
Fashion editorial
High-end monochrome
Architectural minimal
Premium dark
```

### Artistic / expressive

```text
Stained-glass inspired
Collage
Cut-paper
Riso
Mixed-media
Abstract geometry
Gradient art
Experimental typography
```

The final atlas may exceed 80 directions if quality remains high.

## 19.4 Entry format

Every entry should be compact and useful.

Recommended:

```markdown
### Swiss International

**Character:** precise, rational, high-clarity.
**Useful when:** strategy, finance, technical explanation, consulting, institutional communication.
**Vocabulary:** asymmetric grid, grotesk type, strong alignment, limited palette, factual photography, disciplined whitespace.
**Combine with:** technical schematic, monochrome, editorial photography, oversized numerals.
**Watch:** sterile repetition; every slide becoming the same 2-column grid.
```

Do **not** prescribe exact HEX codes or one exact font pair as mandatory.

Exact palette/font examples may exist as optional examples, never as style law.

## 19.5 Combination examples

Include at least 20 synthesis examples:

```text
Swiss + technical annotation + monochrome
Editorial + warm documentary photography + serif display
Blueprint + fluorescent accent + mono labels
Nordic + organic photography + soft data visualization
Neo-brutalist + restrained palette + typographic hero
Risograph + academic research + simple diagrams
Quiet luxury + financial reporting + thin-rule tables
1970s scientific journal + modern cloud architecture
Museum catalogue + cultural-history timeline
SaaS product UI + editorial typography
```

This explicitly teaches that the atlas is composable.

---

# 20. `references/compositions.md`

The agent needs a vocabulary of slide structures.

Target roughly:

```text
30–50 composition archetypes
```

Do not provide hardcoded coordinates.

Each composition entry:

```text
WHEN
STRUCTURE
VISUAL WEIGHT
GOOD FOR
COMMON FAILURE
```

Required archetypes:

```text
statement
hero
title/cover
section divider
split 50/50
split 40/60
editorial asymmetric
image-led
text-led
single metric
metric + evidence
three metrics
comparison
before/after
two-column argument
three-part argument
grid
bento
process
timeline
roadmap
funnel
flywheel
matrix
quadrant
stack/layers
architecture/system
ecosystem
map/spatial
table
chart + takeaway
chart + annotations
quote
case study
customer proof
team
portfolio/gallery
product screenshot
feature walkthrough
closing/ask
appendix/reference
```

Example:

```markdown
### Single metric

**When:** one number carries the argument.
**Structure:** hero number → short qualifier → one contextual comparison/evidence line.
**Weight:** number dominates.
**Failure:** converting it into three equal KPI cards and losing the point.
```

---

# 21. `references/typography.md`

Teach a type system, not a list of fonts.

## Roles

```text
display/title
slide title
section label
body
supporting label
data label
caption/source
monospace/technical
```

## Principles

- explicit hierarchy;
- line-length control;
- contrast between roles;
- consistency;
- avoid tiny type;
- use weight/size/spacing intentionally;
- type itself can be the visual.

## Treatments

Include:

```text
oversized display
editorial serif
Swiss grotesk
mono technical
condensed display
wide geometric sans
humanist sans
luxury serif
all-caps label system
mixed serif/sans
single-family disciplined
```

## Font selection

Existing template/brand fonts win.

When font choice is open:

- choose by tone/readability;
- use available fonts;
- use fallbacks;
- do not make the deck depend on a font unavailable to runtime/export.

---

# 22. `references/color.md`

Teach color as system.

Sections:

- role palette vs arbitrary colors;
- background/surface/text/accent;
- contrast;
- semantic data colors;
- dark/light;
- brand inheritance;
- monochrome;
- duotone;
- warm/cool;
- restrained accent;
- gradients.

Teach:

> one accent with purpose often has more impact than many decorative colors.

Do not include a global mandatory palette.

The atlas may include optional palette examples.

---

# 23. `references/imagery.md`

Cover:

## Photographs

- crop to support focal point;
- preserve aspect ratio;
- full bleed vs contained;
- use high enough quality;
- consider text contrast.

## Screenshots

- preserve UI readability;
- crop irrelevant chrome;
- do not stretch;
- use frames/background deliberately;
- zoom into meaningful region.

## Logos

- preserve aspect ratio;
- give breathing room;
- avoid arbitrary recoloring unless user/brand permits;
- use vector where available.

## Diagrams/images

- fit when cropping would remove meaning;
- annotate rather than shrink until unreadable.

## Treatments

Catalogue:

```text
full bleed
editorial crop
cutout subject
duotone
monochrome
tinted
masked geometric crop
collage
framed screenshot
floating screenshot
contact-sheet/gallery
documentary
cinematic
```

---

# 24. `references/data-design.md`

This should materially improve analytical slides.

## Decision by question

### trend over time

Usually:

```text
line
area only with reason
```

### compare categories

```text
bar
dot plot
```

### composition

```text
stacked bar
100% stacked
```

### distribution

```text
histogram
box/violin if supported/appropriate
```

### relationship

```text
scatter
```

### single KPI

Often no chart.

Use a large number + comparison.

## Rules

- chart exists to answer a question;
- title states conclusion where known;
- highlight the relevant series;
- de-emphasize scaffolding;
- use honest axes;
- show units;
- show sources where important;
- avoid 3D charts;
- avoid gratuitous legends when direct labels work;
- do not chart tiny tables for decoration.

## Native capability awareness

Office v1 may not provide first-class chart authoring for every case.

Do not instruct the model to use unsupported chart-specific tools.

If visualizing data through HTML/CSS/SVG within current capabilities, keep it safe and editable where possible.

---

# 25. `references/tables.md`

Teach tables as information design.

## Use when

- exact values matter;
- comparison across dimensions;
- user will reference cells;
- chart would hide detail.

## Design

- hierarchy in headers;
- alignment by data type;
- units in headers;
- subtle rules;
- highlight meaningful rows/columns;
- avoid excessive borders;
- use whitespace;
- avoid tiny text.

## Alternatives

When table is mostly one conclusion, convert to:

```text
metric
comparison
bar
ranked list
```

---

# 26. `references/diagrams.md`

Teach how to turn systems into slides.

Diagram families:

```text
flow
process
architecture
network
layers
stack
ecosystem
funnel
flywheel
decision tree
swimlane
timeline
roadmap
matrix
hierarchy
pipeline
```

Rules:

- define reading direction;
- reduce crossings;
- align nodes;
- label relationships;
- group by boundary;
- highlight path that matters;
- do not make every box equally loud;
- use text sparingly inside nodes;
- show system boundary.

Include technical style variants:

```text
clean corporate
blueprint
engineering schematic
developer/terminal
systems map
```

---

# 27. `references/motifs.md`

A motif is a recurring gesture, not a template.

Catalogue at least 30 small motifs:

```text
hairline grid
edge label
oversized numeral
section counter
single accent rule
corner bracket
technical annotation
coordinate ticks
cropped circle
offset frame
floating pill label
small mono metadata
image border treatment
full-width baseline
vertical spine
diagonal slice
underlined keyword
highlight block
side rail
micro-grid
gradient glow
paper texture
riso offset
duotone wash
photo cutout
caption system
chapter tabs
progress marker
connected nodes
thin arrow language
```

Teach:

- choose 0–1 primary motif for most decks;
- motif supports identity;
- motif does not need to appear loudly on every slide;
- existing brand motif wins.

---

# 28. `references/genres.md`

Design conventions vary by deck genre.

Include compact guidance for:

```text
investor
board
executive briefing
consulting/strategy
sales
product launch
technical architecture
research/academic
conference keynote
training
annual review/report
portfolio
nonprofit/public sector
company all-hands
proposal
case study
```

For each:

```text
audience expectation
information density
narrative behavior
visual tone
evidence needs
common trap
```

This reference helps select *behavior* without forcing a named visual style.

---

# 29. `references/quality-gates.md`

This is the explicit final checklist.

The main skill's PREFLIGHT points here.

Make it exhaustive but concise.

## Gate A — narrative

- slide order coherent;
- every slide has a job;
- no accidental duplicates;
- conclusion/ask visible.

## Gate B — visual hierarchy

- focal point obvious;
- important content loudest;
- no accidental competing focal points.

## Gate C — typography

- roles consistent;
- no unreadably small type;
- titles/body distinguishable;
- line lengths reasonable.

## Gate D — geometry

- alignment;
- margins;
- spacing rhythm;
- no clipping/overflow;
- no accidental near-alignments.

## Gate E — imagery

- aspect ratio;
- crop;
- quality;
- relevance;
- image/text contrast.

## Gate F — data

- chart/table choice;
- units;
- axis honesty;
- labels;
- sources where needed;
- highlighted takeaway.

## Gate G — consistency

- palette;
- typography;
- repeated components;
- motif;
- image treatment;
- slide numbering/footer if used.

## Gate H — completion

- no placeholders;
- no obvious TODO;
- no empty accidental slide;
- no hidden accidental text;
- no unresolved validation error;
- final intended revision exported.

A gate passes only after a fresh visual review after the latest material changes.

---

# 30. `references/examples.md`

The existing examples file is too API-centric.

Retain a few tool-flow examples, but add reasoning examples.

Examples should include:

## New deck

```text
ORIENT
ARC
SYSTEM
BUILD
SEE
REPAIR
PREFLIGHT
```

## Tiny metric update

Show why ARC/SYSTEM are skipped.

## Existing slide redesign

Show inspect → source → rebuild → preview.

## Add matching slide

Show duplicate closest sibling → update content.

## Open design brief

Show optional atlas lookup and synthesis rather than style selection.

Example:

```text
User: "Make a technical deck about a security incident. Clean, not cyberpunk."

Direction:
Swiss/technical schematic foundation
+ monochrome
+ restrained red incident accent
+ mono metadata labels
+ architectural-flow diagrams

Not:
select "Cyberpunk Outline preset"
```

## Mixed inspiration

```text
User: "1970s scientific journal but for modern cloud infrastructure"

Direction:
warm/off-white editorial base
+ serif display
+ mono technical labels
+ thin engineering diagrams
+ restrained archival photography
```

## Imported low-editability object

Show preserve vs rebuild decision.

---

# 31. Design atlas assets

The plugin may bundle visual examples under:

```text
assets/design-atlas/
```

These assets are **optional reference material**.

They are not imported into every created deck.

They are not a template library the model must choose from.

## 31.1 Useful asset types

Potential:

```text
PNG/JPEG reference images
small SVG motif samples
HTML slide examples using our own authoring model
contact-sheet visual galleries
```

## 31.2 Prefer our own examples

Create original examples from abstract principles.

Do not vendor random internet screenshots.

Avoid dependence on copyrighted presentation screenshots unless licensing clearly allows distribution.

## 31.3 Asset naming

Use descriptive IDs:

```text
swiss-asymmetric-grid.png
editorial-serif-photo.png
technical-hairline-diagram.png
metric-hero.png
comparison-split.png
```

No meaningless `style-01.png`.

## 31.4 Asset optionality

The skill must work when the client cannot visually inspect skill assets.

Text references remain sufficient.

Assets enhance, not gate, behavior.

---

# 32. `SOURCES.md`

Create:

```text
plugins/office/skills/presentations/SOURCES.md
```

Purpose:

- provenance;
- inspiration;
- license notes;
- prevent accidental unattributed copying;
- let future maintainers see where ideas came from.

Include:

```text
Agent Plugins Specification
Agent Skills Specification
OfficeCLI officecli-pptx
OfficeCLI officecli-pitch-deck
OfficeCLI morph-ppt
OfficeCLI morph-ppt-3d
corazzon/pptx-design-styles
Matt Pocock writing-for-agents / skill mechanics source supplied by project owner
```

For external GitHub sources include:

```text
URL
license observed at time of research
what concepts were adapted
what was NOT copied
```

Known at time of this brief:

```text
iOfficeAI/OfficeCLI — Apache-2.0
corazzon/pptx-design-styles — MIT
```

Still verify license files in the repositories before importing any actual source text/assets.

Prefer independently written prose even when copying would be legally permitted.

---

# 33. Licensing / copying rule

Research broadly.

Do not bulk-copy third-party skill prose into this repository.

Do not copy third-party screenshots/assets without confirmed redistribution rights and attribution requirements.

Named design movements such as:

```text
Swiss International
Bauhaus
Art Deco
Risograph
```

are concepts/styles, not proprietary templates.

Explain them in original language.

If any exact third-party asset or meaningful textual portion is intentionally reused:

- verify license;
- preserve required notices;
- record it in `SOURCES.md`.

---

# 34. Keep the design atlas optional

This is non-negotiable.

The skill must encode priority:

```text
1. explicit user direction
2. supplied brand/template/reference deck
3. existing deck's language
4. task/content requirements
5. optional design-atlas inspiration
```

The atlas is fifth.

If user says:

```text
use this company template
```

do not choose "Art Deco Luxe."

If user asks:

```text
change the price on slide 6
```

do not read the atlas.

If user says:

```text
surprise me, make it visually strong
```

the atlas is appropriate.

---

# 35. Never constrain creativity to atlas entries

Write explicitly:

> The atlas is incomplete by design. A visual direction does not need to match any named entry. If the content or user direction suggests a better approach, invent or synthesize one.

And:

> Named entries are vocabulary, not allowed values.

This prevents a dumb agent from interpreting the atlas as an enum.

---

# 36. Atlas dimensions, not presets

Include a compact framework in `design-atlas.md`:

```text
Visual language
Typography
Composition
Palette
Imagery
Information density
Data language
Diagram language
Motif
```

When creating an open-ended system, the agent can choose one answer for several dimensions.

Example:

```text
Visual language: editorial scientific
Typography: serif display + mono labels
Composition: asymmetric
Palette: warm neutral + one red
Imagery: archival documentary
Data: thin rules + annotated numbers
Diagram: engineering schematic
Motif: small coordinate labels
```

This is a design system.

It is not a style preset.

---

# 37. Anti-"AI presentation" guidance

Put this mainly in `design-foundations.md` and `reviewing.md`.

Positive target:

> Slides should feel intentionally composed around their content.

Common failure patterns to catch:

- six identical rounded cards;
- every slide uses the same centered hero layout;
- gradients/glows everywhere regardless of topic;
- random icon decorations;
- excessive pills;
- all content boxed;
- huge title + tiny body with no middle hierarchy;
- decorative charts;
- generic "AI tech" cyan-purple aesthetic;
- too many unrelated radii;
- glass cards on every slide;
- meaningless stock imagery;
- evenly sized everything.

Do not turn this into 50 repeated "do not" instructions.

Teach the positive principles first:

```text
hierarchy
composition
rhythm
content-specific structure
one gesture
restrained repetition
```

Then use the failure list as a review diagnostic.

---

# 38. Design quality is content-dependent

Do not enforce global fixed geometry such as:

```text
every title is 42pt
every margin is 64px
every slide has 20% whitespace
```

These may be useful heuristics/examples but should not become hard rules unless there is a technical constraint.

A visual quality system should reason relative to:

- slide dimensions;
- content amount;
- audience;
- delivery context;
- existing design.

OfficeCLI's quality-floor approach is useful as inspiration, but Office should not blindly inherit every fixed measurement.

---

# 39. Templates and reference decks

When the user supplies a template or existing deck:

- it is the primary design reference;
- inspect representative slides;
- derive its system;
- match it.

Do not "improve" it by mixing atlas aesthetics unless explicitly requested.

For a new slide in an existing deck:

```text
duplicate a nearby matching slide
```

is often safer than synthesizing a new layout from the atlas.

---

# 40. Tool knowledge vs skill knowledge

Keep this separation explicit.

## MCP/API owns

- exact tool names;
- exact schemas;
- allowed enum values;
- ID syntax;
- resource URI behavior;
- revision mechanics;
- pagination;
- errors.

## Skill owns

- when to call what;
- how much to inspect;
- how to reason;
- design expertise;
- review methodology;
- narrative behavior;
- failure diagnosis.

Do not create stale copies of `API_REFERENCE.md`.

---

# 41. Existing files to replace/rename

Current:

```text
references/authoring.md
references/capabilities.md
references/editing.md
references/examples.md
```

Recommended:

```text
authoring.md
→ replace with authoring-html.md

capabilities.md
→ split useful expertise:
   - domoxml-fidelity.md
   - keep technical factual limits in API_REFERENCE/DESIGN
   - only retain skill-relevant limits in direct references

editing.md
→ rewrite fully

examples.md
→ rewrite fully
```

Delete obsolete references after all links are updated.

Do not leave stale duplicate files "just in case."

---

# 42. Update Office README

Update:

```text
plugins/office/README.md
```

briefly to explain that Office ships a presentation skill with progressive expert references.

Do not dump the design atlas list into README.

Something concise:

```text
The presentation skill teaches creation, editing, visual review, imported-deck handling, presentation design, and optional design-atlas inspiration while the MCP provides the typed execution surface.
```

---

# 43. Update plugin-local `AGENTS.md`

Add skill-specific implementation rules, e.g.:

```text
11. Treat MCP/API schemas as the source of truth for exact operations; skills teach workflow and expertise, not duplicated tool reference.
12. Keep `skills/presentations/SKILL.md` focused and route branch-specific knowledge into one-hop references.
13. Design-atlas material is optional inspiration, never a preset whitelist or mandatory style selector.
14. Do not copy third-party skill text/assets without license verification and provenance in `skills/presentations/SOURCES.md`.
15. When adding a discovered skill, justify its independent invocation branch and context cost.
```

---

# 44. Tests / validation

Add automated tests for the skill package.

Possible file:

```text
plugins/office/tests/test_skill_bundle.py
```

or existing suitable test area.

Tests should not attempt to judge aesthetics.

They should enforce package quality/invariants.

## 44.1 Skill discovery/frontmatter

Assert:

```text
skills/presentations/SKILL.md exists
name == presentations
directory == name
description non-empty
description <= 1024
```

If `skills-ref` is available in CI, run:

```text
skills-ref validate plugins/office/skills/presentations
```

Otherwise add a lightweight local structural test and document optional official validation.

## 44.2 Reference integrity

Parse Markdown references from `SKILL.md`.

Assert every referenced file exists.

Do the same for direct file references inside references where practical.

No dangling links.

## 44.3 Main skill size

Enforce a sensible upper bound:

```text
<= 500 lines
```

and optionally token/character budget.

This prevents future sediment.

## 44.4 No non-portable frontmatter

Assert portable skill does not rely on:

```text
disable-model-invocation
```

or unknown fields unless explicitly added to spec/client extension with rationale.

## 44.5 No tool-schema cache

Optional static checks can flag huge copied blocks such as complete generated JSON schemas.

Do not over-engineer.

## 44.6 Design atlas optionality

Test the text contains clear language equivalent to:

```text
optional inspiration
not a template catalogue
existing/user direction wins
combine/reinterpret/ignore
```

This is important enough to make regression-resistant.

## 44.7 Source/provenance

Assert `SOURCES.md` exists.

---

# 45. Manual behavioral evaluation

Automated file tests are insufficient.

Create a small evaluation document or test plan with prompts.

Target at least:

## Creation

```text
"Make a 10-slide deck explaining zero-trust networking to a nontechnical executive team."
```

Expected:

- presentation skill triggers;
- ARC before detailed slide authoring;
- content-specific structure;
- coherent system;
- preview + repair.

## Surgical edit

```text
"On slide 4 change ARR from £1.2m to £1.8m."
```

Expected:

- no design atlas;
- no narrative replan;
- inspect relevant slide;
- element-level edit;
- targeted preview.

## Existing deck addition

```text
"Add a slide after pricing summarising enterprise support. Match the deck."
```

Expected:

- derive/duplicate existing visual language;
- atlas not used unless needed.

## Open design

```text
"Make a visually distinctive deck about data-centre security. Surprise me."
```

Expected:

- atlas may be consulted;
- synthesis, not preset selection;
- design system clearly tied to content.

## Mixed aesthetic

```text
"Make it feel like a 1970s scientific journal crossed with a modern cloud-infrastructure diagram."
```

Expected:

- agent synthesizes dimensions;
- does not say "this isn't in the style library."

## Review

```text
"Review this deck and make it look less AI-generated."
```

Expected:

- whole deck preview first;
- rubric;
- content-specific repairs;
- less repeated cards/pills;
- no blind restyling.

## Imported deck

```text
"Fix the wording on this imported PPTX but preserve everything else."
```

Expected:

- inspect;
- preservation-aware surgical edit;
- validation.

## Pitch

```text
"Build a Series B deck for a marketplace."
```

Expected:

- pitch reference;
- maturity/business-model appropriate proof;
- no generic seed deck.

---

# 46. Behavioral acceptance criteria

A dumb model using this skill should reliably understand:

## Creation

```text
understand → plan narrative → define system → build whole pass → see whole deck → repair → preflight
```

## Editing

```text
understand existing deck → preserve its language → change minimum surface → verify
```

## Review

```text
see whole deck first → identify defects → targeted repair → fresh whole-deck review
```

## Design

```text
content/user/brand first → optional inspiration → synthesize dimensions → build for content
```

## Imported content

```text
editability/preservation state affects what is safe to change
```

If the model instead behaves like:

```text
choose style #12
copy layout
fill cards
export
```

the redesign failed.

---

# 47. Reference quality criteria

Every reference file should answer:

```text
What decision does this file help the agent make?
When should it be loaded?
What behavior changes after reading it?
What completion/quality condition does it improve?
```

Delete any file that is merely generic design exposition with no effect on behavior.

---

# 48. Writing style for references

Use:

- concise declarative guidance;
- tables where comparison is useful;
- compact examples;
- leading concepts;
- explicit decision rules;
- checkable completion criteria.

Avoid:

- motivational prose;
- repeated slogans;
- encyclopedic history of design movements;
- copied API docs;
- 10 synonyms for one instruction;
- fake precision.

---

# 49. Reference size discipline

A huge body of expertise is allowed.

But split by real branch/topic.

Guidance:

```text
SKILL.md                 <= 500 lines
creating.md              focused
editing.md               focused
reviewing.md             focused
pitch-decks.md           can be larger
design-atlas.md          can be large but highly scannable
compositions.md          catalogue/reference
typography.md            focused
...
```

The point is not minimizing total repository tokens.

The point is ensuring any one model path loads only relevant material.

---

# 50. Design atlas target content volume

The atlas should be **wide**.

Suggested target:

```text
60–100 visual-language entries
30–50 composition archetypes
15–25 typography treatments
15–25 image treatments
15–25 data-design patterns
15–25 diagram languages
30+ motif ideas
12–20 deck genre notes
20+ synthesis examples
```

Do not pad with low-quality synonyms just to hit counts.

Breadth must be meaningful.

---

# 51. Visual-language research expansion

The implementation agent may research additional public design movements/reference systems beyond the supplied repos.

Good research topics:

```text
International Typographic Style
Bauhaus
Constructivism
De Stijl
mid-century corporate graphics
Japanese editorial/minimalism
museum/catalogue design
scientific journals
architectural diagrams
consulting presentations
annual reports
fashion editorial
information design
newspaper graphics
data journalism
technical documentation
wayfinding
poster design
zines
riso/screenprint
modern product design systems
```

Do not import proprietary templates.

Use public factual descriptions to write original guidance.

---

# 52. Search/reference behavior must remain optional

Do not make the main skill say:

```text
Always read all design references before creating a deck.
```

That defeats progressive disclosure.

Use trigger-specific pointers.

Example:

```text
When the design direction is open, read `references/design-atlas.md` for optional visual vocabulary.
```

Example:

```text
When a slide needs a diagram, read `references/diagrams.md` before designing it.
```

Example:

```text
When the deck contains substantial charts/KPIs, read `references/data-design.md`.
```

---

# 53. Suggested direct pointers in `SKILL.md`

The main file may include a compact section:

```markdown
## References

- New deck or substantial redesign → [creating](references/creating.md)
- Existing deck edit → [editing](references/editing.md)
- Visual review or improvement → [reviewing](references/reviewing.md)
- Imported PPTX / fidelity / preservation → [imported decks](references/imported-decks.md) and [domOXML fidelity](references/domoxml-fidelity.md)
- Fundraising deck → [pitch decks](references/pitch-decks.md)
- HTML/CSS source authoring → [HTML authoring](references/authoring-html.md)
- Open visual direction → optional [design atlas](references/design-atlas.md)
- Need composition ideas → [compositions](references/compositions.md)
- Typography question → [typography](references/typography.md)
- Imagery-heavy slide → [imagery](references/imagery.md)
- Data/chart-heavy slide → [data design](references/data-design.md)
- Table-heavy slide → [tables](references/tables.md)
- Architecture/process/system visualization → [diagrams](references/diagrams.md)
- Final delivery → [quality gates](references/quality-gates.md)
```

This is one-hop progressive disclosure.

---

# 54. Do not over-trigger references

A model should not read:

```text
typography.md
color.md
imagery.md
data-design.md
tables.md
diagrams.md
genres.md
design-atlas.md
```

for every deck.

That is just a 10-file monolithic skill with extra filesystem calls.

The main process should point selectively.

---

# 55. Reference cross-links

Avoid deep routing chains.

A reference may mention another reference when genuinely necessary, but the main `SKILL.md` should directly point to all important branch files so the model need not discover them transitively.

---

# 56. Capability honesty

The design references may discuss general presentation forms that Office v1 cannot always produce natively.

Never tell the model to rely on:

- arbitrary PowerPoint native chart authoring;
- animation authoring;
- speaker notes;
- video/audio insertion;
- master/layout authoring;

unless the actual current Office implementation supports them.

If a design concept can be represented with supported HTML/CSS/SVG, explain that approach.

If not, describe the limitation honestly.

---

# 57. Future skills rule

Document this principle in `AGENTS.md`:

A new discovered Office skill requires at least one of:

1. a distinct independent user trigger that should activate without ordinary presentation creation/editing;
2. a materially different execution lifecycle;
3. a materially different correctness/verification model.

Examples that may qualify later:

```text
morph-presentations
3d-presentations
document-writing
spreadsheet-modeling
```

Examples that do not qualify:

```text
presentation-typography
presentation-reviewing
presentation-editing
```

Those remain branches/references of `presentations`.

---

# 58. Implementation plan

The agent performing this task should execute in this order.

## Phase 1 — audit current skill references

Read every current file.

Map any still-useful behavior into the new system.

Do not lose:

- stable-ID rules;
- structure-before-source;
- element-update preference;
- revision conflict behavior;
- input/render security facts;
- current fidelity terminology.

## Phase 2 — create source/provenance doc

Create `SOURCES.md`.

Research/verify licenses.

## Phase 3 — write main `SKILL.md`

Keep it process-centric.

Implement:

```text
ORIENT
ARC
SYSTEM
BUILD
SEE
REPAIR
PREFLIGHT
```

with branch conditions and completion criteria.

## Phase 4 — write operational references

```text
creating
editing
reviewing
imported-decks
authoring-html
domoxml-fidelity
pitch-decks
quality-gates
examples
```

## Phase 5 — write design knowledge

```text
design-foundations
design-atlas
compositions
typography
color
imagery
data-design
tables
diagrams
motifs
genres
```

Research broadly.

Use original prose.

## Phase 6 — add optional assets

Only if they materially improve the skill and can be created/licensed cleanly.

Do not block the skill rewrite on a giant image-gallery effort.

Textual atlas is mandatory.

Visual assets are enhancement.

## Phase 7 — delete stale references

Remove old files after new pointers work.

## Phase 8 — update README/AGENTS

Explain new architecture.

## Phase 9 — tests

Add structural/reference/validation tests.

## Phase 10 — behavior review

Run several representative agent prompts mentally or through available harness/model tests.

Fix routing/sprawl issues.

---

# 59. Definition of done

This work is complete only when all of the following are true.

## Package

- [ ] exactly one general discovered `presentations` skill remains;
- [ ] skill conforms to Agent Skills;
- [ ] main `SKILL.md` is focused and under 500 lines;
- [ ] all direct references resolve;
- [ ] stale old references removed.

## Process

- [ ] main skill clearly teaches ORIENT → ARC → SYSTEM → BUILD → SEE → REPAIR → PREFLIGHT;
- [ ] branch conditions are explicit;
- [ ] each major stage has a completion criterion;
- [ ] tiny edits naturally skip irrelevant creation stages.

## Editing

- [ ] existing-deck edits prioritize preservation;
- [ ] small changes use element-level mutation;
- [ ] matching-slide creation favors duplication/derivation from deck;
- [ ] revision conflicts handled intentionally.

## Review

- [ ] whole-deck visual review comes before slide-by-slide repair;
- [ ] rubric covers narrative, hierarchy, legibility, density, alignment, consistency, imagery, data, tables, and technical defects;
- [ ] final fresh review is required after material fixes.

## Imported decks

- [ ] representation/editability/source-retention terminology is correct;
- [ ] operational consequences are taught;
- [ ] unsupported content is not silently rebuilt.

## Design expertise

- [ ] design foundations reference exists;
- [ ] optional design atlas exists;
- [ ] atlas explicitly says it is not a template/preset whitelist;
- [ ] user/brand/existing deck takes priority;
- [ ] atlas supports mixing/reinterpretation;
- [ ] at least 60 meaningful visual directions;
- [ ] composition catalogue is substantial;
- [ ] typography/color/imagery/data/tables/diagrams/motifs/genres references exist.

## Pitch

- [ ] fundraising branch is specialized;
- [ ] stage and business-model context affect narrative/evidence;
- [ ] no universal magic metrics are stated as laws;
- [ ] evidence honesty is explicit.

## Source quality

- [ ] `SOURCES.md`;
- [ ] external licenses verified;
- [ ] external text/assets not blindly copied;
- [ ] original prose.

## Portability

- [ ] no client-specific invocation field required;
- [ ] no filesystem assumptions added;
- [ ] no MCP changes required for skill correctness.

## Tests

- [ ] skill structural tests;
- [ ] link integrity;
- [ ] main file line limit;
- [ ] optional official `skills-ref` validation if practical;
- [ ] lint/type/test suite still passes.

---

# 60. Final mental model

When this redesign is successful, even a weak model should understand Office presentation work as:

```text
ORIENT
What am I making/changing and for whom?

ARC
What is the argument/story?

SYSTEM
What visual language makes that argument coherent?

BUILD
Make the whole first pass.

SEE
Look at the actual deck as a whole.

REPAIR
Fix what is wrong, surgically.

PREFLIGHT
Fresh visual + structural delivery check.
```

And design should feel like:

```text
user/brand/content
        ↓
design requirements
        ↓
optional inspiration
        ↓
synthesized visual system
        ↓
content-specific compositions
```

Never:

```text
user asks for deck
        ↓
choose preset #17
        ↓
copy coordinates/fonts/colors
        ↓
fill boxes
```

The point of the skill layer is to make the existing Office MCP behave like it is being driven by a presentation designer rather than by a model that merely knows which API function to call.

That is the deliverable.

---

# 61. Reference URLs

Use these during implementation and record verified licenses/commit context in `SOURCES.md`.

```text
Agent Plugins
https://agent-plugins.org/specification
https://agent-plugins.org/plugin-authors

Agent Skills
https://agentskills.io/specification

OfficeCLI
https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/officecli-pptx
https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/officecli-pitch-deck
https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/morph-ppt
https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/morph-ppt-3d

Design-style seed taxonomy
https://github.com/corazzon/pptx-design-styles
```

The Matt Pocock-style writing mechanics supplied by the project owner are summarized directly in this brief; implement their principles rather than requiring those external attachment files to exist in the repository.
