# Sources and provenance

This skill package was redesigned from a brief that drew on the projects and
specifications listed below. This file exists so future maintainers can see
where ideas originated, what was and was not reused, and what licenses apply.

**Rule applied throughout:** named design movements (Swiss International,
Bauhaus, Art Deco, Risograph, and similar) are public design concepts, not
proprietary templates. All explanations in this skill package are written in
original prose from first-hand knowledge of those movements, not copied from
any single source. No third-party skill text, screenshots, or asset files
were copied into this repository.

## Specifications

### Agent Plugins specification
- URL: https://agent-plugins.org/specification, https://agent-plugins.org/plugin-authors
- Used for: skill discovery rules (`skills/<name>/SKILL.md`), portability constraints, the rule against non-portable frontmatter fields such as `disable-model-invocation`.
- Adapted: package layout and discovery expectations only. No text copied.

### Agent Skills specification
- URL: https://agentskills.io/specification
- Used for: `SKILL.md` frontmatter shape (`name`, `description`), progressive-disclosure model for `references/` and `assets/`, the ~500 line / ~5000 token size guidance for the main file.
- Adapted: structural rules only. No text copied.

### Matt Pocock — "writing for agents" / skill mechanics
- Source: materials supplied directly by the project owner for this task (not a public URL to fetch).
- Used for: context-pointer discipline (every reference pointer states what it contains and which task branch triggers it), context load vs. cognitive load, information hierarchy (in-file steps > in-file reference > disclosed references), checkable completion criteria, leading words as process anchors, preferring positive instructions over prohibition walls, single-source-of-truth (skills teach expertise, not tool schemas).
- Adapted: the principles are implemented throughout `SKILL.md` and every reference file. No source file exists in this repository to link to; the principles are applied, not quoted.

## External projects (research / inspiration only)

### iOfficeAI/OfficeCLI — `officecli-pptx` skill
- URL: https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/officecli-pptx
- License observed: Apache-2.0 (verify current LICENSE file before any future direct reuse)
- Concepts adapted: one communicative idea per slide, an explicit visual quality floor, visual preview as the core QA mechanism, whole-deck QA before slide-level QA, typography/layout/spacing discipline, coherent recurring motif, inspect-broadly-then-narrow.
- Explicitly NOT copied: command syntax, CLI recipes, fixed centimeter coordinates, tool names. Office's own MCP tool surface (`presentation_*`, `slide_*`, `element_*`) is unrelated and unchanged by this research.

### iOfficeAI/OfficeCLI — `officecli-pitch-deck` skill
- URL: https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/officecli-pitch-deck
- License observed: Apache-2.0
- Concepts adapted: fundraising as a genuinely specialized branch, funding stage changing narrative emphasis, vertical/business model changing which proof matters, evidence-honesty QA for pitch decks.
- Explicitly NOT copied: any numerical SaaS heuristics presented as universal law. `references/pitch-decks.md` in this package frames maturity/model effects as decision principles, not fixed thresholds.

### iOfficeAI/OfficeCLI — `morph-ppt` skill
- URL: https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/morph-ppt
- License observed: Apache-2.0
- Concepts adapted: the reference-library lookup philosophy reused for `design-atlas.md` — inspiration is on-demand, design references are not templates, borrow design logic rather than fixed coordinates, build for current content.
- Explicitly NOT copied: no morph/animation authoring behavior was added anywhere in this package. Office v1 does not support Morph transitions as a first-class authoring feature beyond the `morph` transition enum value already documented in `DESIGN.md`; this skill does not claim more than that.

### iOfficeAI/OfficeCLI — `morph-ppt-3d` skill
- URL: https://github.com/iOfficeAI/OfficeCLI/tree/main/skills/morph-ppt-3d
- License observed: Apache-2.0
- Used only as evidence for the future-skill-splitting rule recorded in `plugins/office/AGENTS.md`: a capability earns its own discovered skill only when it has an independent trigger and a materially different planning/execution/verification lifecycle. No 3D content was added; Office v1 has no 3D capability.

### corazzon/pptx-design-styles
- URL: https://github.com/corazzon/pptx-design-styles
- License observed: MIT
- Used for: a seed taxonomy of ~30 visual-language names as a starting checklist when building `design-atlas.md`.
- Explicitly NOT copied: the repository's behavioral model (pick one named style, obey its exact font/HEX/layout) is the opposite of this skill's design. `design-atlas.md` treats every named direction as combinable vocabulary, not a preset, and expands well beyond the seed list with independently written character/vocabulary/combination notes.

## Public design-history research

`design-atlas.md`, `typography.md`, `color.md`, `diagrams.md`, and `motifs.md` also draw on general, publicly documented knowledge of design movements and information-design practice (International Typographic Style / Swiss design, Bauhaus, Constructivism, De Stijl, mid-century corporate graphics, Japanese editorial minimalism, museum/catalogue design, scientific-journal layout, architectural/engineering diagram conventions, consulting-deck conventions, annual-report design, fashion editorial, newspaper/data-journalism graphics, wayfinding, poster design, zine/riso/screenprint culture, and contemporary product-design systems). These are general facts about design history and practice, not any single copyrighted work, and are described here in original language.

## Office implementation (authoritative, not external)

- `plugins/office/DESIGN.md` — tool contracts, domOXML enums (`Representation`, `Editability`, `SourceRetention`), revision/concurrency model.
- `plugins/office/API_REFERENCE.md` — generated, exact tool schemas.
- `plugins/office/AGENTS.md` — implementation rules for this plugin.

These are the single source of truth for tool names, schemas, and capability limits. No reference file in this skill duplicates their content; they teach when/why/how to use what the tools already expose.

## Validation

`plugins/office/server/tests/unit/test_skill_bundle.py` enforces the package's structural invariants (frontmatter shape, portability, reference-link integrity, size limits, atlas/composition breadth, single-skill invariant) locally via `pytest`. No `skills-ref` CLI (the official Agent Skills validator referenced in the redesign brief) is wired into this repository's CI at this time — if `skills-ref` becomes available, run `skills-ref validate plugins/office/skills/presentations` as an additional, complementary check; it is not currently a required or automated gate here.

## Assets

No third-party images, SVGs, or screenshots were vendored into `assets/`. This package ships without bundled visual assets — the textual design atlas is the required deliverable; visual examples are treated as a future enhancement rather than a blocker, per the brief.
