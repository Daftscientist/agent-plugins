# Creating and substantially redesigning a deck

This file supports the ARC and SYSTEM stages of `SKILL.md` for new decks and full redesigns. It is planning and decision guidance, not a tool reference — see `API_REFERENCE.md` for exact schemas.

## Audience and purpose

Resolve from context rather than interrogating the user when enough is already clear:

```text
Who is the audience, and what do they already know?
What should they believe, decide, or do after seeing this?
Is delivery live, async/self-read, or both?
How much explanation belongs on the slide vs. spoken aloud?
```

A live, presenter-narrated deck can carry lighter slides with more of them. An async memo-deck must be more self-explanatory per slide because there is no narrator to fill gaps.

## Narrative arc

Sequence before layout. Decide the order of ideas before touching composition or visuals.

Useful general shapes — patterns to adapt, not templates to fill in:

```text
context → problem → implication → response → proof → decision
question → evidence → conclusion → next step
status → change → impact → action
vision → opportunity → system → proof → ask
```

Group related slides into short sections rather than cramming everything onto one mega-slide. Remove any slide that repeats a job another slide already does — a redundant slide dilutes the ones around it, it doesn't add safety margin.

## One job per slide

A slide may hold several pieces of evidence, but they should all serve one message. Symptoms of a slide doing two jobs:

- the title needs "and" to describe it;
- there are two unrelated focal areas competing for attention;
- there are two unrelated conclusions;
- a reader can't tell what to look at first.

Split a two-job slide into two slides rather than trying to balance both inside one.

## Title quality

Prefer a stated takeaway over a bare topic label when the takeaway is already known:

```text
"Enterprise revenue grew 42% after the pricing change"   (message)
"Revenue"                                                  (topic — weaker here)
```

Topic labels remain the right choice for section dividers, reference/appendix slides, and navigation slides, where a message title would be noise.

## Slide-count discipline

Do not target a fixed magic number of slides. Use as many as it takes to keep every slide coherent under the one-job rule — no fewer, no more. A live keynote can use more, lighter slides than a dense async report; let delivery context set the count, not a habit.

## Build the whole narrative first

Build every planned slide's first pass before polishing any single one deeply. A common failure mode is spending most of the effort on slide 1 while slides 4 through 10 stay unfinished — SEE and REPAIR are the stages for polish, BUILD is for completeness.

## Completion criterion

Creation planning is complete only when:

- audience and purpose are understood;
- an ordered slide-title sequence exists;
- every slide has one job;
- no obvious duplicate or redundant slide remains;
- relevant specialist references (pitch, imported-deck, design) have been consulted where the branch applies.

Once planning is done, move to SYSTEM (`references/design-foundations.md`, optionally `references/design-atlas.md`) before BUILD.
