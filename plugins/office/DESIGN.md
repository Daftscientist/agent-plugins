# Office Agent Plugin — Presentation v1 Design

> **Target repository:** `https://github.com/Daftscientist/agent-plugins`  
> **Intended path:** `plugins/office/DESIGN.md`  
> **Status:** implementation design / Codex handoff  
> **Last protocol review:** 2026-08-07  
> **Agent Plugins target:** `1.0.0` Working Draft  
> **MCP target:** `2026-07-28`  
> **Python MCP SDK target:** official `mcp` Python SDK v2 stable line  
> **Presentation engine:** `https://github.com/Daftscientist/domOXML`

---

## 0. Purpose of this document

This document is the implementation contract for the first Office Agent Plugin in the `Daftscientist/agent-plugins` repository.

The first release is intentionally focused on **PowerPoint / PPTX presentations**, backed by domOXML. The plugin is named **Office** rather than **PowerPoint** so future versions can add document and workbook capabilities without creating an unrelated package family.

The implementation must be:

- a valid, portable **Agent Plugin**;
- a high-quality **MCP server**, not merely a collection of tools that happen to speak MCP;
- built with the **official Python MCP SDK v2**;
- strongly and comprehensively typed with Pydantic / JSON Schema;
- designed around domOXML's actual HTML/CSS → canonical IR → PPTX architecture;
- usable standalone before any custom multi-user AI-agent harness exists;
- deliberately prepared for an optional future host/harness artifact integration;
- safe to deploy later in a multi-user SaaS environment without changing the model-facing Office contract;
- pleasant for an AI model to use repeatedly for create → inspect → edit → preview → validate → export workflows.

This is **not** a specification for the future AI-agent harness itself. The plugin must not require that harness to exist.

### Normative language

The words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are used intentionally in this design.

When implementation and this document disagree, Codex should treat this document as authoritative unless the current Agent Plugins specification, current MCP specification, current official Python MCP SDK, or current domOXML public API proves the requirement impossible or obsolete. In that case, implementation must preserve the intent, document the incompatibility, and update this design rather than silently improvising.

---

# 1. Sources of truth

Implementation must be verified against these authoritative sources before finalising protocol-sensitive code.

## 1.1 Agent Plugins

- Specification: <https://agent-plugins.org/specification>
- Plugin author guide: <https://agent-plugins.org/plugin-authors>
- Home: <https://agent-plugins.org/>

As reviewed on 2026-08-07, Agent Plugins v1.0.0 defines:

- one required root `plugin.json` manifest;
- optional Agent Skills under immediate children of `skills/`;
- optional MCP configuration at root `mcp.json`;
- reverse-domain client extension namespaces in `plugin.json.extensions` and/or matching top-level directories;
- `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` for stdio MCP plugin runtimes;
- `stdio`, `streamable-http`, and legacy `sse` MCP configuration variants;
- client ownership of installation, permission UX, sandboxing, credentials, enablement, and other client-specific behaviour.

The Agent Plugins standard is **open and vendor-neutral**. This repository is a collection of plugins conforming to that standard; it is not itself the standard and must not redefine the portable core.

## 1.2 Model Context Protocol

- MCP specification: <https://modelcontextprotocol.io/specification/2026-07-28>
- MCP 2026-07-28 release overview: <https://blog.modelcontextprotocol.io/posts/2026-07-28/>

The implementation should target modern MCP `2026-07-28` semantics while retaining compatibility with older clients through the official SDK.

Important current-state assumptions:

- the 2026 core is stateless;
- there is no modern connection handshake/session dependency;
- modern discovery is `server/discover`;
- every request is self-describing;
- server-to-client requests were replaced by multi-round-trip request flows;
- formal MCP extensions exist and are opt-in;
- list results are cacheable and ordering matters;
- progress remains useful and is server-to-client;
- modern subscriptions use `subscriptions/listen`;
- roots, sampling, and protocol-level logging are deprecated for new designs;
- `ping` is removed;
- Tasks moved to an extension and should not be implemented until the official stable Python SDK supports the current extension cleanly.

## 1.3 Official Python MCP SDK

- Docs: <https://py.sdk.modelcontextprotocol.io/>
- v2 changes: <https://py.sdk.modelcontextprotocol.io/whats-new/>
- Tools: <https://py.sdk.modelcontextprotocol.io/servers/tools/>
- Structured output: <https://py.sdk.modelcontextprotocol.io/servers/structured-output/>
- Resources: <https://py.sdk.modelcontextprotocol.io/servers/resources/>
- URI templates: <https://py.sdk.modelcontextprotocol.io/servers/uri-templates/>
- Prompts: <https://py.sdk.modelcontextprotocol.io/servers/prompts/>
- Completions: <https://py.sdk.modelcontextprotocol.io/servers/completions/>
- Media/icons: <https://py.sdk.modelcontextprotocol.io/servers/media/>
- Errors: <https://py.sdk.modelcontextprotocol.io/servers/handling-errors/>
- Progress: <https://py.sdk.modelcontextprotocol.io/handlers/progress/>
- Subscriptions: <https://py.sdk.modelcontextprotocol.io/handlers/subscriptions/>
- Pagination: <https://py.sdk.modelcontextprotocol.io/advanced/pagination/>
- Extensions: <https://py.sdk.modelcontextprotocol.io/advanced/extensions/>
- Deployment: <https://py.sdk.modelcontextprotocol.io/run/deploy/>

Use:

```python
from mcp.server import MCPServer
```

Do **not** build new code on the v1 `FastMCP` API.

Use the high-level `MCPServer` for normal tools, prompts, resources, dependency injection, progress, media, and subscriptions. Drop to the low-level `Server` only where the high-level surface genuinely cannot express the protocol requirement, especially **true MCP pagination** or exact mixed-content tool results.

## 1.4 domOXML

- Repository: <https://github.com/Daftscientist/domOXML>
- Architecture: <https://raw.githubusercontent.com/Daftscientist/domOXML/main/spec/architecture.md>

As reviewed on 2026-08-07, domOXML is an alpha parity-first document compiler with PowerPoint as its first target.

Key architectural facts Office MUST respect:

1. HTML/CSS is the primary authoring surface.
2. The canonical internal representation is not HTML or OOXML; it is domOXML's typed IR.
3. Existing PPTX can be ingested and normalised back toward HTML/CSS.
4. Native editable output is preferred where possible.
5. Unsupported visible content must not silently disappear.
6. domOXML reports representation/editability/source-retention coverage.
7. Current render targets include PPTX, PNG, and normalised HTML.
8. Chromium / Playwright is part of the rendering pipeline.
9. Current public presentation presets include `16:9`, `4:3`, and `16:10`, with custom dimensions up to PowerPoint's 56-inch limit.
10. Current transitions include `none`, `fade`, `push`, `wipe`, `cover`, `split`, `cut`, `zoom`, `dissolve`, and `morph`.

---

# 2. Product definition

## 2.1 What Office v1 is

Office v1 is an Agent Plugin that gives AI agents a **document-compiler-style editing environment for PowerPoint presentations**.

The model-facing mental model is:

```text
presentation
    ↓
slides
    ↓
elements
    ↓
HTML + inline CSS
    ↓
domOXML
    ↓
canonical IR
    ↓
editable PPTX + previews + validation
```

The model does not work with DrawingML, OOXML package parts, relationship XML, slide master XML, or raw PowerPoint shape APIs.

## 2.2 What Office v1 is not

Office v1 is NOT:

- a raw OOXML editor;
- a PowerPoint COM automation wrapper;
- a giant set of shape-coordinate micro-tools;
- a screenshot-only presentation generator;
- a filesystem MCP;
- a dependency on the future custom AI-agent harness;
- a remote multi-user storage service by default;
- a chart authoring API pretending domOXML already supports features that it does not;
- a general DOCX/XLSX implementation yet.

## 2.3 Core UX goals

An agent should be able to execute flows such as:

```text
Create a deck
→ preview the whole deck once
→ inspect a problematic slide
→ modify three elements in one call
→ preview that slide
→ validate editability
→ export PPTX
```

or:

```text
Find my Cascade pricing deck
→ inspect its outline
→ inspect the Pricing slide structure
→ change three values
→ export latest revision
```

without repeatedly transmitting entire slides or repeatedly rendering every slide individually.

---

# 3. Repository and package layout

The top-level `Daftscientist/agent-plugins` repository is a catalogue/monorepo containing multiple independent Agent Plugin packages.

Recommended target layout:

```text
agent-plugins/
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── docs/
│   ├── architecture.md
│   ├── development.md
│   └── compatibility.md
└── plugins/
    └── office/
        ├── DESIGN.md                 # this document
        ├── README.md
        ├── CHANGELOG.md
        ├── LICENSE
        ├── plugin.json
        ├── mcp.json
        ├── skills/
        │   └── presentations/
        │       ├── SKILL.md
        │       └── references/
        │           ├── authoring.md
        │           ├── editing.md
        │           ├── capabilities.md
        │           └── examples.md
        ├── server/
        │   ├── pyproject.toml
        │   ├── uv.lock
        │   ├── README.md
        │   ├── src/
        │   │   └── office_mcp/
        │   │       ├── __init__.py
        │   │       ├── __main__.py
        │   │       ├── app.py
        │   │       ├── config.py
        │   │       ├── constants.py
        │   │       ├── errors.py
        │   │       ├── icons.py
        │   │       ├── ids.py
        │   │       ├── models/
        │   │       │   ├── common.py
        │   │       │   ├── presentation.py
        │   │       │   ├── slide.py
        │   │       │   ├── element.py
        │   │       │   ├── preview.py
        │   │       │   ├── validation.py
        │   │       │   └── search.py
        │   │       ├── domain/
        │   │       │   ├── service.py
        │   │       │   ├── mutations.py
        │   │       │   ├── normalization.py
        │   │       │   ├── indexing.py
        │   │       │   └── revisions.py
        │   │       ├── domoxml_adapter/
        │   │       │   ├── compiler.py
        │   │       │   ├── importer.py
        │   │       │   ├── renderer.py
        │   │       │   ├── coverage.py
        │   │       │   └── html.py
        │   │       ├── storage/
        │   │       │   ├── protocols.py
        │   │       │   ├── local.py
        │   │       │   ├── sqlite.py
        │   │       │   ├── blobs.py
        │   │       │   └── scope.py
        │   │       ├── inputs/
        │   │       │   ├── protocols.py
        │   │       │   ├── resolver.py
        │   │       │   ├── data_uri.py
        │   │       │   ├── local_file.py
        │   │       │   └── http.py
        │   │       ├── outputs/
        │   │       │   ├── protocols.py
        │   │       │   └── local.py
        │   │       ├── mcp/
        │   │       │   ├── tools.py
        │   │       │   ├── resources.py
        │   │       │   ├── prompts.py
        │   │       │   ├── completions.py
        │   │       │   ├── pagination.py
        │   │       │   ├── subscriptions.py
        │   │       │   └── middleware.py
        │   │       └── extensions/
        │   │           └── README.md
        │   └── tests/
        │       ├── unit/
        │       ├── integration/
        │       ├── protocol/
        │       ├── security/
        │       ├── golden/
        │       └── fixtures/
        └── assets/
            └── icons/
```

The precise internal module split may evolve, but domain, MCP protocol, storage, domOXML adaptation, and future host integration MUST remain separately testable concerns.

---

# 4. Root repository navigation requirements

Because this repository will contain many plugins, the repository root must not read like a single-product README.

Root `README.md` SHOULD contain:

1. a concise explanation that the repository contains portable plugins for the Agent Plugins standard;
2. a link to `https://agent-plugins.org/`;
3. a plugin catalogue table;
4. status / maturity per plugin;
5. links to each plugin's README;
6. development/contribution links;
7. explicit statement that each `plugins/<name>/` directory is independently packageable.

Example catalogue:

```markdown
## Plugins

| Plugin | Status | Capabilities |
|---|---|---|
| [Office](./plugins/office/) | Alpha | PPTX creation, editing, preview, validation, export |
```

The root `AGENTS.md` SHOULD give Codex/repo agents global repository rules and direct them to read the nearest plugin-level design/AGENTS file before changing a plugin.

---

# 5. Agent Plugin manifest

## 5.1 `plugin.json`

Target initial manifest:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "office",
  "version": "0.1.0",
  "description": "Create, inspect, edit, preview, validate, and export editable Microsoft Office presentations. Initial support focuses on PowerPoint through domOXML.",
  "author": {
    "name": "Daftscientist"
  },
  "repository": "https://github.com/Daftscientist/agent-plugins",
  "license": "MIT",
  "keywords": [
    "office",
    "powerpoint",
    "pptx",
    "presentation",
    "slides",
    "domoxml",
    "mcp"
  ]
}
```

Do not invent extra top-level keys. The Agent Plugins v1 manifest schema is closed.

Do not add the future custom harness extension until that harness namespace and behaviour actually exist.

## 5.2 Future Agent Plugins client extension

A future custom client/harness MAY add manifest data under a reverse-domain namespace it controls:

```json
{
  "extensions": {
    "com.example.agent": {
      "artifacts": true
    }
  }
}
```

This is illustrative only. The real namespace must use a domain controlled by the harness owner, and its semantics must be specified separately.

The portable Office plugin MUST remain fully useful if a client ignores this extension.

---

# 6. MCP configuration

## 6.1 Portable default: stdio

The initial Agent Plugin package should expose one local stdio MCP server.

During source development, a simple configuration may use `uv`:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "office": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--project",
        "${PLUGIN_ROOT}/server",
        "python",
        "-m",
        "office_mcp"
      ],
      "cwd": "${PLUGIN_ROOT}",
      "env": {
        "OFFICE_DATA_DIR": "${PLUGIN_DATA}/office"
      }
    }
  }
}
```

This is acceptable for development but is not the final distribution portability target because a plugin should not casually assume every Agent Plugins client has `uv`, Python 3.12+, Playwright, and Chromium correctly installed.

## 6.2 Release packaging goal

Before calling the plugin broadly portable, release engineering SHOULD provide a plugin-relative executable/launcher or another deterministic installation strategy that:

- obeys Agent Plugins command containment rules;
- does not require shell command parsing;
- installs runtime dependencies into `PLUGIN_DATA`, not `PLUGIN_ROOT`;
- obtains the required Chromium runtime deterministically;
- works on supported operating systems;
- never mutates the plugin package contents after installation;
- produces actionable startup errors when prerequisites cannot be satisfied.

This can be a later milestone than the initial implementation.

## 6.3 Optional Streamable HTTP deployment

The same Office server code SHOULD be capable of Streamable HTTP deployment outside the portable package for SaaS use.

Do not put a random production URL into the portable `mcp.json` until a real hosted service exists.

Remote deployment must use current MCP transport security configuration, proper auth, and multi-tenant scoping. See §28.

---

# 7. MCP server identity and instructions

Initial construction should resemble:

```python
from mcp.server import MCPServer

mcp = MCPServer(
    "Office",
    version="0.1.0",
    instructions=(
        "Create and edit Microsoft Office presentations. "
        "Author slides using semantic HTML with inline CSS. "
        "Inspect unfamiliar presentations before modifying them. "
        "Prefer element-level mutations for small edits. "
        "Use presentation_preview for visual verification and "
        "presentation_validate for editability/fidelity verification."
    ),
    icons=OFFICE_ICONS,
)
```

Server instructions must remain short. The full operating procedure belongs in the Agent Skill, not a giant MCP server instruction field.

---

# 8. Design laws

The following are hard design rules for v1.

1. **HTML + inline CSS is the authoring language.**
2. **No OOXML is exposed to the model.**
3. **No JavaScript is accepted from the model.**
4. **Stable opaque IDs exist for presentations, revisions, slides, and elements.**
5. **A slide index is display metadata, never identity.**
6. **Every slide has a required human-readable `name`.**
7. **A short non-rendered `description` is strongly encouraged.**
8. **Small edits happen at element level.**
9. **Full-slide replacement remains an explicit escape hatch.**
10. **Element updates can batch multiple edits into one transaction/revision.**
11. **Mutation calls may include an optional human-readable activity label.**
12. **Long operations emit MCP progress when the client requested progress.**
13. **Whole-deck visual inspection returns contact sheets rather than dozens of independent images.**
14. **Detailed visual inspection returns one slide image.**
15. **Structural/editability validation is separate from visual preview.**
16. **Tool schemas use actual enums/unions/bounds, not prose-only validation.**
17. **Tool results use structured output wherever meaningful.**
18. **Binary files are exposed as resources/resource links rather than dumped into model text.**
19. **MCP resources, prompts, completions, pagination, subscriptions, icons, progress, and annotations are first-class parts of the implementation.**
20. **Features are not invented merely to tick protocol boxes.**
21. **The AI does not need a filesystem.**
22. **Standalone plugin storage is private plugin state, not a universal user filesystem.**
23. **Future host artifact integration plugs into interfaces; it does not fork the tool contract.**
24. **Authorization is never inferred from knowing an opaque object ID.**
25. **Unexpected internal exceptions never leak local paths, stack traces, SQL, secrets, or tokens.**

---

# 9. Type system conventions

All public domain request/response models should derive from a strict base model.

```python
from pydantic import BaseModel, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
    )
```

Use discriminated unions where the shape changes by `type`.

Use `Literal`/`StrEnum` for closed choices.

Use `Field()` constraints for lengths, numeric ranges, and descriptions.

Every model-facing identifier must have a clear regex/prefix.

Illustrative aliases:

```python
from typing import Annotated
from pydantic import Field

PresentationId = Annotated[str, Field(pattern=r"^prs_[A-Za-z0-9_-]{8,}$")]
RevisionId = Annotated[str, Field(pattern=r"^rev_[A-Za-z0-9_-]{8,}$")]
SlideId = Annotated[str, Field(pattern=r"^sld_[A-Za-z0-9_-]{8,}$")]
ElementId = Annotated[str, Field(pattern=r"^el_[A-Za-z0-9_-]{8,}$")]
```

ULID-backed IDs are a good implementation choice, but the wire contract should be opaque; callers must never parse business meaning from IDs.

---

# 10. Shared domain types

## 10.1 Activity

```python
class Activity(StrictModel):
    label: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description=(
                "Short user-facing description of what this operation is doing, "
                "for example 'Updating the latest traction figures'."
            ),
        ),
    ]
```

Activity is optional on mutating or expensive operations.

The model should not need to provide it for correctness.

When absent, Office synthesizes a reasonable fallback from the operation and slide/presentation name.

## 10.2 Slide size

These values mirror domOXML's current public types.

```python
class SlideSizePreset(StrEnum):
    WIDE_16_9 = "16:9"
    STANDARD_4_3 = "4:3"
    WIDE_16_10 = "16:10"

class PresetSlideSize(StrictModel):
    type: Literal["preset"] = "preset"
    preset: SlideSizePreset

class CustomSlideSize(StrictModel):
    type: Literal["custom"] = "custom"
    width_in: float = Field(gt=0, le=56.0)
    height_in: float = Field(gt=0, le=56.0)

SlideSize = Annotated[
    PresetSlideSize | CustomSlideSize,
    Field(discriminator="type"),
]
```

## 10.3 Transitions

```python
class SlideTransition(StrEnum):
    NONE = "none"
    FADE = "fade"
    PUSH = "push"
    WIPE = "wipe"
    COVER = "cover"
    SPLIT = "split"
    CUT = "cut"
    ZOOM = "zoom"
    DISSOLVE = "dissolve"
    MORPH = "morph"
```

## 10.4 Theme

Theme is a typed deck-level source of defaults/tokens. It does not reintroduce external CSS stylesheets.

```python
class ThemePalette(StrictModel):
    background: str = "#ffffff"
    foreground: str = "#0b0b0c"
    accent: str = "#4f46e5"
    muted: str = "#6b7280"

class ThemeFonts(StrictModel):
    heading: str = "Inter"
    body: str = "Inter"

class PresentationTheme(StrictModel):
    palette: ThemePalette = Field(default_factory=ThemePalette)
    fonts: ThemeFonts = Field(default_factory=ThemeFonts)
```

Patch variants should use optional fields and `model_fields_set` / `exclude_unset=True` semantics so omitted fields remain unchanged.

## 10.5 domOXML coverage enums

Mirror domOXML rather than renaming these concepts.

```python
class Representation(StrEnum):
    NATIVE = "native"
    DECOMPOSED = "decomposed"
    HYBRID = "hybrid"
    LAYERED = "layered"
    ELEMENT_LAYER = "element_layer"
    RASTERIZED = "rasterized"
    APPROXIMATED = "approximated"
    FAILED = "failed"

class Editability(StrEnum):
    SEMANTIC = "semantic"
    COMPONENTS = "components"
    LAYERS = "layers"
    NONE = "none"

class SourceRetention(StrEnum):
    NOT_REQUIRED = "not_required"
    ATTACHED = "attached"
    DETACHED = "detached"
    IGNORED = "ignored"
    LOST = "lost"
```

---

# 11. Presentation identity and revision model

Every presentation has:

```text
presentation_id   prs_...
current_revision  rev_...
```

Every meaningful mutation creates a new immutable revision identifier.

A revision should represent a coherent snapshot of:

- presentation metadata;
- slide ordering;
- slide metadata;
- canonical editable representation / normalised HTML;
- element identity mapping;
- preservation payload required for round-tripping imported PPTX constructs;
- references to assets;
- relevant validation metadata.

## 11.1 Optimistic concurrency

All mutating tools SHOULD accept:

```python
expected_revision: RevisionId | None = None
```

If supplied and it is not the current revision, mutation MUST fail with a model-readable `REVISION_CONFLICT` error.

This prevents silent overwrite when multiple agents/tabs/users edit the same document.

Example:

```text
Agent A reads rev_17
Agent B commits rev_18
Agent A tries to mutate expected_revision=rev_17
→ REVISION_CONFLICT; current revision is rev_18
```

Do not automatically merge arbitrary concurrent slide edits in v1.

---

# 12. Slide metadata and element identity

## 12.1 Slide metadata

Each slide MUST have a non-rendered human-readable name.

```python
class SlideMetadata(StrictModel):
    name: str = Field(
        min_length=1,
        max_length=80,
        description="Short human-readable slide name. Not rendered on the slide.",
    )
    description: str | None = Field(
        default=None,
        max_length=240,
        description="Short description of the slide's purpose/content. Not rendered.",
    )
```

Examples:

```text
Cover
Market opportunity
Architecture
Pricing
Competitive landscape
Closing
```

A name is metadata. It must not be confused with a visible `<h1>`.

## 12.2 Stable element IDs

Every editable node exposed to the model receives a server-managed stable ID:

```html
<h2 data-office-id="el_01K..." ...>...</h2>
```

The model MUST NOT be allowed to choose or overwrite `data-office-id`.

When HTML is added/replaced:

- strip caller-supplied `data-office-id` values;
- assign new IDs where needed;
- preserve existing IDs only where the server can prove node continuity.

## 12.3 Semantic element names

The model MAY assign optional slide-scoped semantic aliases:

```html
<h2
  data-office-name="arr-metric"
  style="font-size:40px;font-weight:700"
>
  $1.8M ARR
</h2>
```

`data-office-name` values SHOULD be unique per slide when present.

Element tools may select by `element_id` or `element_name`, but never both in the same selector.

If a name is ambiguous, return `AMBIGUOUS_ELEMENT_NAME` rather than guessing.

---

# 13. HTML/CSS authoring contract

## 13.1 Inline CSS only

The Office MCP authoring contract deliberately narrows domOXML's broader browser authoring capability.

Accepted authoring style:

```html
<section style="width:100%;height:100%;background:#fff;padding:64px">
  <h1 style="font-size:42px;font-weight:700;color:#111">
    Revenue grew 42%
  </h1>
  <p style="font-size:20px;color:#666">
    Driven primarily by enterprise adoption.
  </p>
</section>
```

Disallowed for model-authored source:

```html
<style>...</style>
<link rel="stylesheet" ...>
<script>...</script>
```

JavaScript MUST be disabled/rejected.

No styling may depend on a CSS class selector or external stylesheet.

## 13.2 Why inline CSS is enforced

Element-level AI editing becomes dramatically more reliable when the model can inspect one node and see the styles that govern it on that node.

It avoids:

- hidden stylesheet dependencies;
- selector specificity confusion;
- needing to fetch a second source blob for a small edit;
- breaking unrelated elements through a shared class edit;
- stylesheet order drift during round trips.

## 13.3 Semantic HTML

Prefer normal HTML elements such as:

- `section`, `main`, `div`;
- `h1`–`h6`, `p`, `span`;
- `ul`, `ol`, `li`;
- `img`;
- `table`, `thead`, `tbody`, `tr`, `th`, `td`;
- supported SVG where domOXML has a meaningful parity path.

The MCP layer SHOULD reject clearly unsafe/irrelevant active content including:

- `script`;
- `iframe`;
- `object`;
- `embed`;
- form submission controls;
- external stylesheet links;
- executable event-handler attributes such as `onclick`.

## 13.4 Imported decks

When importing PPTX, domOXML may produce richer normalised source metadata than the model-facing authoring dialect.

Office should maintain two concepts:

1. **canonical internal/preservation state**, which must preserve what domOXML needs for round-trip fidelity;
2. **model-facing editable HTML**, which should be normalised toward the inline-authoring contract.

Do not destroy preservation metadata merely to make the exposed HTML prettier.

## 13.5 CSS support philosophy

Do not invent an Office-specific styling DSL.

CSS properties remain CSS strings.

Typed enums are appropriate for protocol/domain control choices such as transitions or preview modes; they are **not** appropriate for every CSS property value.

Unsupported or lossy CSS must surface through validation/coverage warnings, not disappear silently.

---

# 14. Input / file onboarding model

MCP is not a universal client-file-upload protocol. Office therefore needs an input abstraction that works standalone but does not require the model runtime to have a filesystem.

## 14.1 Stable public input type

Use a URI-oriented source contract:

```python
class PresentationSource(StrictModel):
    uri: str = Field(
        min_length=1,
        description=(
            "URI for a PPTX source. Supported schemes depend on the runtime. "
            "Portable fallback schemes include data:; local deployments may enable file:; "
            "network-enabled deployments may enable https:. Future host integrations may "
            "register additional schemes without changing the tool schema."
        ),
    )
    filename_hint: str | None = Field(default=None, max_length=255)
```

This intentionally keeps the model-facing tool contract stable when future host-specific resolvers are added.

## 14.2 Portable resolver schemes

### `data:`

A `data:` URI containing base64 PPTX bytes is a universal compatibility fallback.

It is not the preferred path for large files because it expands tool arguments and model context.

### `file:`

Local file resolution MAY be available in local/stdio deployments, but it MUST be disabled unless explicitly configured.

The model does not require filesystem access merely because Office supports `file:` in a local deployment.

When enabled:

- use strict path policy;
- define explicit allowed roots;
- canonicalise and containment-check paths;
- reject traversal and symlink escapes;
- never expose arbitrary host filesystem browsing through Office.

### `https:`

Remote HTTPS input MAY be enabled.

If enabled, implement SSRF protection:

- HTTPS by default;
- bounded redirects;
- resolve and reject loopback/private/link-local/metadata-network destinations unless explicitly allowlisted;
- revalidate every redirect destination;
- enforce response byte limits;
- enforce timeouts;
- validate MIME type and PPTX ZIP/package signature;
- do not forward ambient credentials;
- do not reflect fetched secret content in errors.

## 14.3 Future host schemes

A future custom harness may register schemes such as:

```text
artifact://...
conversation-file://...
```

through an `InputResolver` adapter.

The Office tools do not need to change.

---

# 15. Export / file egress model

The model should think in terms of exporting/delivering a presentation, not converting implementation internals.

`presentation_export` materialises an immutable PPTX for a specific revision and returns a resource link.

The canonical exported file resource should be revision-addressed:

```text
office://presentations/{presentation_id}/revisions/{revision_id}/file
```

That makes it immutable and cache-friendly.

Do not return multi-megabyte PPTX bytes as model-readable text.

The exact binary resource should use the standard PPTX MIME type:

```text
application/vnd.openxmlformats-officedocument.presentationml.presentation
```

A host with a richer artifact system may intercept or adapt the export later, but portable standalone behaviour must remain valid without it.

---

# 16. Storage architecture

## 16.1 Storage is private plugin state in standalone mode

Standalone Office uses:

```text
${PLUGIN_DATA}/office/
```

This is private persistent state for the installed plugin instance.

It is **not** the user's universal AI file system and must not be presented as such.

Recommended local layout:

```text
${PLUGIN_DATA}/office/
├── office.sqlite3
├── revisions/
├── assets/
├── previews/
├── exports/
├── temp/
└── runtime/
```

## 16.2 Store protocols

Core Office logic must depend on interfaces, not the local implementation.

```python
class PresentationStore(Protocol):
    async def create(...): ...
    async def get(...): ...
    async def search(...): ...
    async def commit(...): ...
    async def delete(...): ...
    async def list_page(...): ...

class InputResolver(Protocol):
    async def resolve(...): ...

class OutputSink(Protocol):
    async def publish(...): ...
```

The local plugin provides:

```text
PresentationStore -> LocalPresentationStore
InputResolver      -> CompositeInputResolver
OutputSink         -> OfficeResourceOutputSink
```

A future harness can provide adapters without changing presentation/slide/element services.

## 16.3 Suggested SQLite schema

The exact schema may change, but the following responsibilities should exist:

### `presentations`

- `presentation_id` primary key;
- scope/owner key (hidden from model-facing APIs);
- `name`;
- `description`;
- `created_at`;
- `updated_at`;
- `current_revision_id`;
- soft-deletion state if used.

### `revisions`

- `revision_id` primary key;
- `presentation_id`;
- parent revision;
- creation timestamp;
- snapshot/blob reference;
- content hash;
- optional validation summary.

### `slides`

May be materialised for indexing/current-state reads:

- `slide_id`;
- `presentation_id`;
- current ordinal;
- name;
- description;
- extracted text;
- current revision visibility.

### search index

Use SQLite FTS5 initially over:

- presentation name;
- presentation description;
- slide names;
- slide descriptions;
- extracted visible text.

Search storage must be replaceable later.

## 16.4 Revision representation

v1 MAY store full snapshots per revision for simplicity and correctness.

Do not prematurely invent a complex CRDT/delta format.

A later version may add delta compression or content-addressed structural sharing while retaining immutable revision IDs.

---

# 17. MCP tool catalogue

The target v1 tool set is:

## Presentation

1. `presentation_create`
2. `presentation_open`
3. `presentation_search`
4. `presentation_inspect`
5. `presentation_update`
6. `presentation_validate`
7. `presentation_preview`
8. `presentation_export`
9. `presentation_delete`

## Slides

10. `slide_add`
11. `slide_inspect`
12. `slide_update`
13. `slide_duplicate`
14. `slide_delete`
15. `slide_reorder`

## Elements

16. `element_inspect`
17. `element_add`
18. `element_update`
19. `element_move`
20. `element_delete`

Twenty tools is acceptable because they are high-level, stable domain operations rather than PowerPoint micro-primitives.

Do not add tools such as:

```text
set_shape_x
set_shape_y
set_shape_fill
set_font_size
add_text_box
write_ooxml
edit_relationship
```

HTML/CSS and element-level mutations are the abstraction.

---

# 18. Tool annotations and UI titles

Every tool MUST define a useful static `title` and `ToolAnnotations`.

Suggested annotations:

| Tool | readOnly | destructive | idempotent | openWorld |
|---|---:|---:|---:|---:|
| presentation_create | false | false | false | false |
| presentation_open | false | false | false | true only if network source enabled |
| presentation_search | true | n/a | n/a | false |
| presentation_inspect | true | n/a | n/a | false |
| presentation_update | false | false | depends on patch; hint false | false |
| presentation_validate | true | n/a | n/a | false |
| presentation_preview | true | n/a | n/a | false |
| presentation_export | true with respect to document state | n/a | n/a | false |
| presentation_delete | false | true | true effect | false |
| slide_add | false | false | false | false |
| slide_inspect | true | n/a | n/a | false |
| slide_update | false | false | false | false |
| slide_duplicate | false | false | false | false |
| slide_delete | false | true | true effect | false |
| slide_reorder | false | false | true for same requested order | false |
| element_inspect | true | n/a | n/a | false |
| element_add | false | false | false | false |
| element_update | false | false | false | false |
| element_move | false | false | false | false |
| element_delete | false | true | true effect | false |

Tool annotations are hints, not authorization controls.

---

# 19. Exact tool contracts — presentation tools

The following models describe the intended wire semantics. Naming may be adjusted to satisfy the final Python module style, but schema meaning must remain stable.

## 19.1 `presentation_create`

**Title:** Create presentation

**Description:**

> Create a new editable PowerPoint presentation. Slides are authored with semantic HTML and inline CSS. Slide names are required metadata and are not rendered.

```python
class NewSlide(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=240)
    html: str = Field(min_length=1)
    transition: SlideTransition | None = None
    size: SlideSize | None = None

class PresentationCreateArgs(StrictModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=500)
    size: SlideSize = PresetSlideSize(preset=SlideSizePreset.WIDE_16_9)
    theme: PresentationTheme = Field(default_factory=PresentationTheme)
    slides: list[NewSlide] = Field(default_factory=list, max_length=100)
    activity: Activity | None = None
```

Result:

```python
class SlideRef(StrictModel):
    slide_id: SlideId
    number: int = Field(ge=1)
    name: str
    description: str | None = None

class PresentationCreateResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    name: str
    slide_count: int = Field(ge=0)
    slides: list[SlideRef]
    resource_uri: str
```

Behaviour:

- validates/sanitises every slide HTML fragment before commit;
- assigns server-owned slide and element IDs;
- creates exactly one initial revision;
- permits zero slides;
- creating many initial slides is one transaction and one revision;
- emits progress only when work is meaningful enough to warrant it.

## 19.2 `presentation_open`

**Title:** Open presentation

**Description:**

> Import an existing PPTX into Office's editable presentation workspace. The source is resolved by URI. Unsupported constructs are preserved where domOXML can preserve them and surfaced through warnings rather than silently dropped.

```python
class PresentationOpenArgs(StrictModel):
    source: PresentationSource
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=500)
    activity: Activity | None = None
```

Result:

```python
class ImportWarning(StrictModel):
    code: str
    message: str
    slide_number: int | None = Field(default=None, ge=1)
    element: str | None = None

class PresentationOpenResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    name: str
    slide_count: int = Field(ge=0)
    slides: list[SlideRef]
    warnings: list[ImportWarning]
    resource_uri: str
```

Behaviour:

- validates package magic/content type, not just filename extension;
- places resolved bytes into isolated temp processing space if domOXML requires a path;
- cleans scratch data after import;
- never returns local temp paths;
- generates human-readable slide names heuristically if imported PPTX lacks Office metadata;
- generated names should prefer visible title text, then concise fallback such as `Slide 4`;
- stores preservation payload needed for round-trip fidelity;
- indexes extracted text after import.

## 19.3 `presentation_search`

**Title:** Search presentations

```python
class PresentationSearchField(StrEnum):
    NAME = "name"
    DESCRIPTION = "description"
    SLIDE_NAMES = "slide_names"
    SLIDE_DESCRIPTIONS = "slide_descriptions"
    SLIDE_TEXT = "slide_text"

class PresentationSearchSort(StrEnum):
    RELEVANCE = "relevance"
    UPDATED_DESC = "updated_desc"
    UPDATED_ASC = "updated_asc"
    CREATED_DESC = "created_desc"
    CREATED_ASC = "created_asc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"

class PresentationSearchArgs(StrictModel):
    query: str | None = Field(default=None, max_length=500)
    search_in: list[PresentationSearchField] = Field(
        default_factory=lambda: [
            PresentationSearchField.NAME,
            PresentationSearchField.DESCRIPTION,
            PresentationSearchField.SLIDE_NAMES,
            PresentationSearchField.SLIDE_TEXT,
        ],
        min_length=1,
    )
    created_after: datetime | None = None
    created_before: datetime | None = None
    updated_after: datetime | None = None
    updated_before: datetime | None = None
    sort: PresentationSearchSort = PresentationSearchSort.RELEVANCE
    limit: int = Field(default=20, ge=1, le=100)
    cursor: str | None = Field(default=None, max_length=2048)
```

Result:

```python
class PresentationSearchMatch(StrictModel):
    slide_id: SlideId | None = None
    slide_name: str | None = None
    snippet: str

class PresentationSearchItem(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    slide_count: int
    matches: list[PresentationSearchMatch]
    resource_uri: str

class PresentationSearchResult(StrictModel):
    items: list[PresentationSearchItem]
    next_cursor: str | None = None
```

Search cursor requirements:

- opaque to caller;
- includes or cryptographically binds query/sort/filter state;
- expires reasonably;
- scope-bound in multi-user deployment;
- cannot be edited to expose another scope's results.

This tool exists even though `resources/list` exists. `resources/list` is a protocol catalogue operation, not a domain full-text search API.

## 19.4 `presentation_inspect`

**Title:** Inspect presentation

```python
class PresentationInspectDetail(StrEnum):
    SUMMARY = "summary"
    OUTLINE = "outline"

class PresentationInspectArgs(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId | None = None
    detail: PresentationInspectDetail = PresentationInspectDetail.OUTLINE
```

Result:

```python
class PresentationInspectResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    name: str
    description: str | None
    size: SlideSize
    theme: PresentationTheme
    created_at: datetime
    updated_at: datetime
    slide_count: int
    slides: list[SlideRef]
```

The inspect tool MUST remain context-efficient. It does not return all slide HTML.

## 19.5 `presentation_update`

**Title:** Update presentation

```python
class ThemePalettePatch(StrictModel):
    background: str | None = None
    foreground: str | None = None
    accent: str | None = None
    muted: str | None = None

class ThemeFontsPatch(StrictModel):
    heading: str | None = None
    body: str | None = None

class PresentationThemePatch(StrictModel):
    palette: ThemePalettePatch | None = None
    fonts: ThemeFontsPatch | None = None

class PresentationUpdateArgs(StrictModel):
    presentation_id: PresentationId
    expected_revision: RevisionId | None = None
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=500)
    size: SlideSize | None = None
    theme: PresentationThemePatch | None = None
    activity: Activity | None = None
```

Important patch semantics:

- omitted field = unchanged;
- `description=null` MAY mean clear description if field was explicitly supplied;
- use Pydantic's field-set tracking rather than conflating omitted with null;
- name may not be cleared;
- theme patches merge recursively, not replace unspecified values.

Result:

```python
class MutationResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
```

## 19.6 `presentation_validate`

**Title:** Validate presentation

```python
class ValidationDetail(StrEnum):
    SUMMARY = "summary"
    FULL = "full"

class PresentationValidateArgs(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId | None = None
    slide_ids: list[SlideId] | None = None
    detail: ValidationDetail = ValidationDetail.SUMMARY
```

Result:

```python
class CoverageItem(StrictModel):
    slide_id: SlideId
    element: str
    representation: Representation
    editability: Editability
    source_retention: SourceRetention
    output_count: int = Field(ge=0)
    raster_area_emu2: int = Field(ge=0)
    reason: str

class ValidationWarning(StrictModel):
    code: str
    message: str
    slide_id: SlideId | None = None
    element: str | None = None

class PresentationValidationResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    valid: bool
    slide_count: int
    native_ratio: float = Field(ge=0, le=1)
    editable_ratio: float = Field(ge=0, le=1)
    layered_ratio: float = Field(ge=0, le=1)
    warning_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)
    warnings: list[ValidationWarning]
    coverage: list[CoverageItem] | None = None
```

`coverage` is populated only in `full` mode.

Validation must map domOXML's actual coverage model faithfully instead of creating fake “100% editable” booleans.

## 19.7 `presentation_preview`

**Title:** Preview presentation

```python
class PreviewAll(StrictModel):
    type: Literal["all"] = "all"

class PreviewRange(StrictModel):
    type: Literal["range"] = "range"
    start: int = Field(ge=1)
    end: int = Field(ge=1)

class PreviewSlides(StrictModel):
    type: Literal["slides"] = "slides"
    slide_ids: list[SlideId] = Field(min_length=1, max_length=100)

PreviewSelection = Annotated[
    PreviewAll | PreviewRange | PreviewSlides,
    Field(discriminator="type"),
]

class PreviewLayout(StrEnum):
    AUTO = "auto"
    SINGLE = "single"
    CONTACT_SHEET = "contact_sheet"

class PreviewQuality(StrEnum):
    STANDARD = "standard"
    HIGH = "high"

class PreviewLabels(StrEnum):
    NONE = "none"
    NUMBER = "number"
    NAME = "name"
    NUMBER_AND_NAME = "number_and_name"

class PresentationPreviewArgs(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId | None = None
    selection: PreviewSelection = Field(default_factory=PreviewAll)
    layout: PreviewLayout = PreviewLayout.AUTO
    quality: PreviewQuality = PreviewQuality.STANDARD
    labels: PreviewLabels = PreviewLabels.NUMBER_AND_NAME
    columns: Literal[2, 3, 4, 5] | None = None
    activity: Activity | None = None
```

Structured metadata:

```python
class PreviewImageDescriptor(StrictModel):
    page: int = Field(ge=1)
    slide_ids: list[SlideId]
    width_px: int = Field(gt=0)
    height_px: int = Field(gt=0)
    mime_type: Literal["image/png"] = "image/png"

class PresentationPreviewResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    layout: PreviewLayout
    images: list[PreviewImageDescriptor]
```

Protocol result:

- return one or more standard MCP `ImageContent` blocks;
- also return structured metadata if the SDK surface allows doing so cleanly;
- if mixed image + structured result needs exact control, use `CallToolResult` / low-level construction rather than abandoning structured metadata.

AUTO behaviour:

- one selected slide → single high-detail image;
- small/normal multi-slide selection → contact sheet;
- large selections → multiple bounded contact sheets, not dozens of independent image blocks.

Suggested defaults:

- contact sheet max ~30 slides per image;
- preserve slide aspect ratio;
- readable labels outside slide content;
- deterministic ordering.

## 19.8 `presentation_export`

**Title:** Export presentation

```python
class PresentationExportArgs(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId | None = None
    format: Literal["pptx"] = "pptx"
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    activity: Activity | None = None
```

Result metadata:

```python
class PresentationExportResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    filename: str
    mime_type: Literal[
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ]
    size_bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    resource_uri: str
```

The tool result SHOULD include an MCP `ResourceLink` content block pointing to the immutable revision file resource in addition to structured metadata.

Do not introduce PDF export until it is intentionally supported by the underlying implementation.

## 19.9 `presentation_delete`

**Title:** Delete presentation

```python
class PresentationDeleteArgs(StrictModel):
    presentation_id: PresentationId
    expected_revision: RevisionId | None = None
    activity: Activity | None = None

class PresentationDeleteResult(StrictModel):
    presentation_id: PresentationId
    deleted: Literal[True] = True
```

Deletion policy must be documented in the plugin README.

For standalone v1, hard delete is acceptable if explicitly documented. A recoverable trash layer may be added later.

---

# 20. Exact tool contracts — slide tools

## 20.1 Insertion position

```python
class InsertStart(StrictModel):
    type: Literal["start"] = "start"

class InsertEnd(StrictModel):
    type: Literal["end"] = "end"

class InsertBefore(StrictModel):
    type: Literal["before"] = "before"
    slide_id: SlideId

class InsertAfter(StrictModel):
    type: Literal["after"] = "after"
    slide_id: SlideId

SlideInsertionPosition = Annotated[
    InsertStart | InsertEnd | InsertBefore | InsertAfter,
    Field(discriminator="type"),
]
```

## 20.2 `slide_add`

**Title:** Add slides

```python
class SlideAddArgs(StrictModel):
    presentation_id: PresentationId
    expected_revision: RevisionId | None = None
    slides: list[NewSlide] = Field(min_length=1, max_length=50)
    position: SlideInsertionPosition = Field(default_factory=InsertEnd)
    activity: Activity | None = None

class SlideAddResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    added: list[SlideRef]
    slide_count: int
```

Adding 10 slides should be one tool call, one transaction, one revision.

## 20.3 `slide_inspect`

**Title:** Inspect slide

```python
class SlideInspectDetail(StrEnum):
    SUMMARY = "summary"
    STRUCTURE = "structure"
    SOURCE = "source"

class SlideInspectArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    revision: RevisionId | None = None
    detail: SlideInspectDetail = SlideInspectDetail.STRUCTURE
```

Summary result:

```python
class SlideSummary(StrictModel):
    slide_id: SlideId
    number: int
    name: str
    description: str | None
    transition: SlideTransition | None
    size: SlideSize | None
    element_count: int
```

Structure result nodes:

```python
class ElementStructureNode(StrictModel):
    element_id: ElementId
    element_name: str | None
    tag: str
    text: str | None
    child_ids: list[ElementId]

class SlideInspectResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    summary: SlideSummary
    structure: list[ElementStructureNode] | None = None
    html: str | None = None
```

`summary` mode returns no structure/source.

`structure` returns a context-efficient tree overview without full CSS.

`source` returns the normalised model-facing inline-styled HTML.

## 20.4 `slide_update`

**Title:** Update slide

This tool is the full-slide escape hatch plus metadata update path. It is not the normal way to change one label.

```python
class SlideUpdateArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    expected_revision: RevisionId | None = None
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=240)
    transition: SlideTransition | None = None
    size: SlideSize | None = None
    html: str | None = None
    activity: Activity | None = None
```

Patch semantics use explicit field presence:

- omitted transition/size = unchanged;
- explicit null transition = clear transition;
- explicit null size = inherit presentation size;
- explicit HTML = replace entire slide authoring tree, reminting/preserving element IDs according to continuity rules.

At least one mutable field must be explicitly supplied.

## 20.5 `slide_duplicate`

**Title:** Duplicate slide

```python
class SlideDuplicateArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    expected_revision: RevisionId | None = None
    name: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=240)
    position: SlideInsertionPosition | None = None
    activity: Activity | None = None

class SlideDuplicateResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slide: SlideRef
```

Default position SHOULD be immediately after the source slide.

Duplicated slides receive:

- a new slide ID;
- new element IDs;
- copied semantic names where safe;
- copied preservation/source state as appropriate.

## 20.6 `slide_delete`

**Title:** Delete slides

```python
class SlideDeleteArgs(StrictModel):
    presentation_id: PresentationId
    slide_ids: list[SlideId] = Field(min_length=1, max_length=100)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None

class SlideDeleteResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    deleted_slide_ids: list[SlideId]
    slide_count: int
```

Reject duplicate IDs in the request.

## 20.7 `slide_reorder`

**Title:** Reorder slides

Use a declarative full-order operation rather than a series of ambiguous moves.

```python
class SlideReorderArgs(StrictModel):
    presentation_id: PresentationId
    slide_ids: list[SlideId] = Field(min_length=1, max_length=500)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None

class SlideReorderResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slides: list[SlideRef]
```

Validation:

- every current slide ID must occur exactly once;
- no unknown slide IDs;
- no duplicates;
- no omission.

---

# 21. Exact tool contracts — element tools

## 21.1 Element selector

```python
class ElementById(StrictModel):
    type: Literal["id"] = "id"
    element_id: ElementId

class ElementByName(StrictModel):
    type: Literal["name"] = "name"
    element_name: str = Field(min_length=1, max_length=100)

ElementSelector = Annotated[
    ElementById | ElementByName,
    Field(discriminator="type"),
]
```

## 21.2 `element_inspect`

**Title:** Inspect element

```python
class ElementInspectArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    element: ElementSelector
    revision: RevisionId | None = None
    depth: int = Field(default=1, ge=0, le=10)
    include_html: bool = True
    include_styles: bool = True

class ElementInspectResult(StrictModel):
    presentation_id: PresentationId
    revision: RevisionId
    slide_id: SlideId
    element_id: ElementId
    element_name: str | None
    tag: str
    text: str | None
    attributes: dict[str, str]
    styles: dict[str, str] | None
    html: str | None
    child_ids: list[ElementId]
```

Never return server-owned preservation payloads or unsafe internal metadata through attributes.

## 21.3 `element_add`

**Title:** Add element

```python
class ElementInsertPosition(StrEnum):
    BEFORE = "before"
    AFTER = "after"
    PREPEND = "prepend"
    APPEND = "append"

class ElementAddArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    relative_to: ElementSelector
    position: ElementInsertPosition
    html: str = Field(min_length=1)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None

class AddedElement(StrictModel):
    element_id: ElementId
    element_name: str | None
    tag: str

class ElementAddResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slide_id: SlideId
    roots: list[AddedElement]
```

The server strips caller-provided `data-office-id` and assigns its own IDs.

## 21.4 Style and attribute mutations

```python
class StyleMutation(StrictModel):
    set: dict[str, str] = Field(default_factory=dict, max_length=100)
    remove: list[str] = Field(default_factory=list, max_length=100)

class AttributeMutation(StrictModel):
    set: dict[str, str] = Field(default_factory=dict, max_length=100)
    remove: list[str] = Field(default_factory=list, max_length=100)
```

Rules:

- cannot set/remove `data-office-id`;
- cannot add event-handler attributes;
- cannot add active scripting URLs;
- style keys are normal CSS property names;
- style removal is by property name;
- duplicate `set` and `remove` entries for the same key are invalid.

## 21.5 `element_update`

**Title:** Update elements

```python
class ElementMutation(StrictModel):
    element: ElementSelector
    text: str | None = None
    inner_html: str | None = None
    replace_html: str | None = None
    styles: StyleMutation | None = None
    attributes: AttributeMutation | None = None

class ElementUpdateArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    elements: list[ElementMutation] = Field(min_length=1, max_length=100)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None

class ElementUpdateResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slide_id: SlideId
    updated_element_ids: list[ElementId]
```

Per mutation:

- `text`, `inner_html`, and `replace_html` are mutually exclusive content operations;
- style and attribute patches may accompany one content operation;
- at least one operation must be present;
- `text` replaces child content with a text node while retaining the target element;
- `inner_html` replaces children while retaining the target element and target ID;
- `replace_html` must contain exactly one root element and replaces the target node while transferring the stable target ID to the new root if structurally valid;
- newly introduced descendants receive new IDs;
- batch operations apply atomically and produce one revision.

Example:

```json
{
  "presentation_id": "prs_01K...",
  "slide_id": "sld_01K...",
  "elements": [
    {
      "element": {"type": "name", "element_name": "arr"},
      "text": "$1.8M ARR"
    },
    {
      "element": {"type": "name", "element_name": "customers"},
      "text": "12,900 customers"
    },
    {
      "element": {"type": "name", "element_name": "period"},
      "text": "July 2026"
    }
  ],
  "activity": {
    "label": "Updating the latest traction figures"
  }
}
```

## 21.6 `element_move`

**Title:** Move elements

This changes DOM/tree ordering/hierarchy, not pixel geometry. Pixel geometry remains CSS.

```python
class ElementMoveOperation(StrictModel):
    element: ElementSelector
    relative_to: ElementSelector
    position: ElementInsertPosition

class ElementMoveArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    moves: list[ElementMoveOperation] = Field(min_length=1, max_length=50)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None

class ElementMoveResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slide_id: SlideId
    moved_element_ids: list[ElementId]
```

Moves are applied in request order inside one transaction. Reject cycles and moving a node relative to its own descendant in an invalid way.

## 21.7 `element_delete`

**Title:** Delete elements

```python
class ElementDeleteArgs(StrictModel):
    presentation_id: PresentationId
    slide_id: SlideId
    elements: list[ElementSelector] = Field(min_length=1, max_length=100)
    expected_revision: RevisionId | None = None
    activity: Activity | None = None

class ElementDeleteResult(StrictModel):
    presentation_id: PresentationId
    previous_revision: RevisionId
    revision: RevisionId
    slide_id: SlideId
    deleted_element_ids: list[ElementId]
```

Reject attempts to delete the synthetic/root slide container if the implementation relies on one.


---

# 22. MCP resources

Resources are not an afterthought. They are the application-controlled representation layer of the Office server.

General rule:

```text
TOOLS      = actions / mutations / deliberate operations
RESOURCES  = addressable representations of current or immutable state
PROMPTS    = user-selected conversation templates
```

## 22.1 Static resources

### `office://capabilities`

MIME: `application/json`

Purpose:

- concise machine-readable Office/domOXML capability summary;
- current presentation features;
- known limitations;
- current source dialect policy;
- supported transitions and size presets;
- preview/export formats;
- server/plugin version.

This should be generated from code/constants and domOXML capability information where practical, not maintained as an unrelated stale prose list.

Suggested shape:

```json
{
  "office_version": "0.1.0",
  "presentation": {
    "input": ["pptx", "html"],
    "output": ["pptx", "png", "html"],
    "authoring": {
      "html": true,
      "inline_css_only": true,
      "javascript": false
    },
    "slide_sizes": ["16:9", "4:3", "16:10", "custom"],
    "transitions": [
      "none", "fade", "push", "wipe", "cover",
      "split", "cut", "zoom", "dissolve", "morph"
    ]
  }
}
```

Do not overpromise unsupported authored charts, arbitrary animation authoring, notes, video/audio insertion, or other gaps.

## 22.2 Presentation resource templates

Canonical URI tree:

```text
office://presentations/{presentation_id}
office://presentations/{presentation_id}/outline
office://presentations/{presentation_id}/validation
office://presentations/{presentation_id}/preview{?quality,labels,columns}

office://presentations/{presentation_id}/revisions/{revision_id}
office://presentations/{presentation_id}/revisions/{revision_id}/file

office://presentations/{presentation_id}/slides/{slide_id}
office://presentations/{presentation_id}/slides/{slide_id}/source
office://presentations/{presentation_id}/slides/{slide_id}/preview{?quality}

office://presentations/{presentation_id}/slides/{slide_id}/elements/{element_id}
```

All template parameters must be validated and scope-checked.

Use the official SDK's RFC 6570 URI-template support rather than custom regex routing unless a low-level paginated resource implementation requires sharing the parser manually.

The Python SDK currently supports typed parameter conversion, simple placeholders, multi-segment captures, query parameters, and list-segment operators. Its default URI-template security rejects traversal, absolute paths, and null bytes. Retain those defaults; do not weaken them globally.

## 22.3 Resource semantics

### Presentation root

`office://presentations/{presentation_id}`

MIME: `application/json`

Returns compact metadata similar to `presentation_inspect(summary)`.

### Outline

`office://presentations/{presentation_id}/outline`

MIME: `application/json`

Returns ordered slide references with names/descriptions.

### Validation

`office://presentations/{presentation_id}/validation`

MIME: `application/json`

Returns the latest validation summary for the current revision; if not cached, it MAY run a validation operation subject to resource-read latency policy. Prefer cache-and-invalidate over unexpectedly expensive reads.

### Presentation preview

`office://presentations/{presentation_id}/preview?...`

MIME: `image/png`

Returns a contact sheet for the current revision.

### Revision metadata

`office://presentations/{presentation_id}/revisions/{revision_id}`

MIME: `application/json`

Returns immutable revision metadata.

### Revision file

`office://presentations/{presentation_id}/revisions/{revision_id}/file`

MIME: PPTX MIME type

Returns binary resource contents (`BlobResourceContents` on the wire).

### Slide root

`office://presentations/{presentation_id}/slides/{slide_id}`

MIME: `application/json`

Returns slide summary/structure metadata.

### Slide source

`office://presentations/{presentation_id}/slides/{slide_id}/source`

MIME: `text/html`

Returns model-facing normalised HTML using inline styles and server-managed IDs.

### Slide preview

`office://presentations/{presentation_id}/slides/{slide_id}/preview`

MIME: `image/png`

Returns one rendered slide.

### Element resource

`office://presentations/{presentation_id}/slides/{slide_id}/elements/{element_id}`

MIME: `application/json`

Returns element inspection information.

## 22.4 `resources/list`

`resources/list` should list **presentation root resources**, not every slide and element in every deck.

That keeps the catalogue useful and bounded.

Child objects are discoverable through resource templates, completions, outline data, and Office tools.

Each resource list entry SHOULD expose:

- URI;
- presentation name;
- concise description;
- MIME type `application/json`;
- Office/presentation icon metadata if appropriate.

Ordering MUST be deterministic. Recommended default:

```text
updated_at DESC, presentation_id ASC
```

Do not let a database query's accidental ordering become protocol behaviour.

---

# 23. True MCP pagination

The MCP high-level resource decorator returns a full resource catalogue and does not expose true list pagination controls. If presentation counts can grow large, use the low-level list handler for `resources/list`.

Protocol requirements:

- input cursor is opaque;
- server chooses page size;
- result uses `next_cursor`;
- `next_cursor=None` means end;
- there is no protocol `total`, `page`, or `has_more` field;
- client cannot request arbitrary page size through the core list method.

Recommended resource page size: 100–250 compact presentation resources.

Cursor design SHOULD include/bind:

- last deterministic sort key;
- store/scope identifier;
- schema/version marker;
- optional expiry;
- integrity signature when a cursor crosses a trust boundary.

Never trust a caller-controlled cursor as a raw SQL offset or primary-key namespace without validation.

Other list families (`tools/list`, `prompts/list`, `resources/templates/list`) are small/static enough to remain one page initially. Do not add pagination complexity where there are only tens of objects.

---

# 24. MCP completions

Completions apply to **prompt arguments and resource-template parameters**, not arbitrary tool arguments.

Implement completion support because it improves host UIs and demonstrates proper MCP behaviour.

## 24.1 Presentation ID completion

When completing `{presentation_id}`:

- search only presentations visible to the current scope/principal;
- match prefixes against presentation ID and presentation name;
- return concise display-friendly suggestions;
- never enumerate another user's IDs.

Conceptually:

```text
prs_... — Cascade Pitch
prs_... — Q3 Review
prs_... — Hosting Launch
```

## 24.2 Slide ID completion

When `presentation_id` is already resolved, completing `{slide_id}` should be dependent on that presentation.

Suggestions SHOULD include:

```text
sld_... — Cover
sld_... — Problem
sld_... — Architecture
```

## 24.3 Element ID completion

Optional but useful for developer/debug UIs.

When presentation and slide are resolved, element completion may surface:

```text
el_... — h1 — Architecture
el_... — arr-metric — $1.8M ARR
```

Cap completion result sizes aggressively. Completion is a suggestion UI, not a data dump.

---

# 25. MCP prompts

MCP prompts are user-controlled templates. They are not substitutes for tools and are not the same thing as the Agent Skill.

Initial prompts:

## 25.1 `create_presentation`

Title: `Create presentation`

Arguments should stay flat strings because MCP prompt arguments are not arbitrary Pydantic tool schemas.

Suggested arguments:

- `topic` required;
- `audience` optional;
- `purpose` optional;
- `style` optional;
- `slide_count` optional string hint.

Prompt output should tell the model to use Office tools and the presentation skill workflow.

## 25.2 `review_presentation`

Title: `Review presentation`

Arguments:

- `presentation_id` required and completion-enabled;
- `focus` optional.

Prompt should seed a workflow using inspect → preview → validate and then report/fix issues as appropriate.

Do not create dozens of redundant prompts. Prompts are UI affordances, not an alternate tool namespace.

---

# 26. Agent Skill

Path:

```text
plugins/office/skills/presentations/SKILL.md
```

Agent Plugins discovers immediate children of `skills/`; the skill must conform to the Agent Skills specification.

Initial frontmatter:

```yaml
---
name: presentations
description: Create, inspect, edit, preview, validate, and export PowerPoint presentations using the Office MCP tools and domOXML-backed HTML/CSS authoring.
---
```

The skill body SHOULD teach the agent the workflow, not reproduce the entire protocol schema.

Essential skill rules:

1. Inspect an unfamiliar existing presentation before modifying it.
2. Use presentation outline metadata to navigate rather than opening every slide source.
3. Use `slide_inspect(detail="structure")` before source when structure is enough.
4. Prefer `element_update` for text/style tweaks.
5. Batch related element edits.
6. Use `slide_update(html=...)` only for a genuine slide redesign/rebuild.
7. Name every newly created slide descriptively.
8. Add concise descriptions to non-trivial slides.
9. Author semantic HTML with inline CSS only.
10. Use `data-office-name` for important elements likely to be edited later.
11. Never invent/modify `data-office-id`.
12. Preview the whole deck after broad changes.
13. Use a single-slide preview for detailed visual debugging.
14. Validate when fidelity/editability matters.
15. Export the final desired revision.
16. Avoid gratuitous tool spam; batch where safe.
17. Avoid repeatedly previewing unchanged slides.
18. Respect revision conflicts; re-inspect and reapply intentionally.

References in the skill directory should include:

- `authoring.md` — HTML/CSS policy and examples;
- `editing.md` — element-oriented workflows;
- `capabilities.md` — domOXML support/gaps;
- `examples.md` — end-to-end examples.

---

# 27. Progress and human-readable activity

The MCP progress mechanism must be used for operations where progress is meaningful.

Tools can accept optional:

```json
{
  "activity": {
    "label": "Rebuilding the architecture diagram"
  }
}
```

The server should echo/surface that intent through progress messages when progress was requested by the client.

Examples:

```text
Importing the investor deck
Parsing PowerPoint · 1/4
Normalising slides · 2/4
Building editable workspace · 3/4
Indexing presentation · 4/4
```

or:

```text
Rendering presentation preview · 12/18 slides
```

Rules:

- progress values MUST increase monotonically;
- do not repeat or decrease progress values;
- report a known `total` when meaningful;
- no fake percentage loops for operations that take 80 ms;
- progress reporting should be a no-op when the client did not request it;
- rate-limit updates to avoid notification spam;
- activity labels are user-facing and must not contain paths/internal implementation details.

Mutation tools that complete almost instantly generally need only the host's normal tool activity indicator, not granular progress.

---

# 28. Error model

## 28.1 Stable domain error codes

Define a structured internal taxonomy at minimum:

```text
PRESENTATION_NOT_FOUND
SLIDE_NOT_FOUND
ELEMENT_NOT_FOUND
AMBIGUOUS_ELEMENT_NAME
INVALID_PRESENTATION_SOURCE
UNSUPPORTED_SOURCE_SCHEME
SOURCE_TOO_LARGE
INVALID_PPTX
INVALID_HTML
UNSAFE_HTML
UNSUPPORTED_CSS
REVISION_CONFLICT
INVALID_SLIDE_ORDER
INVALID_ELEMENT_MOVE
IMPORT_FAILED
RENDER_FAILED
VALIDATION_FAILED
EXPORT_FAILED
RESOURCE_TOO_LARGE
ACCESS_DENIED
RATE_LIMITED
INTERNAL_ERROR
```

## 28.2 Model-recoverable tool errors

Errors the model can correct should be returned as MCP **tool errors** (`is_error=True`) with a concise actionable message.

Examples:

```text
REVISION_CONFLICT: presentation changed since rev_17; current revision is rev_18. Re-inspect before applying the mutation.
```

```text
AMBIGUOUS_ELEMENT_NAME: 3 elements are named 'metric'. Inspect the slide structure and use an element_id.
```

```text
INVALID_HTML: <script> is not allowed in Office slide authoring.
```

Do not `return` error strings as successful results.

## 28.3 Protocol errors

Use `MCPError` for genuine protocol/request-method failures that the model cannot fix as an ordinary domain action.

Do not turn every domain exception into `MCPError`; doing so prevents the model from seeing and recovering from the tool failure cleanly.

## 28.4 Unexpected exceptions

Unexpected exceptions must:

- be logged through ordinary application logging/telemetry, not deprecated MCP protocol logging;
- return a sanitised generic failure;
- include a trace/correlation ID in client `_meta` where useful;
- never leak:
  - stack traces;
  - local filesystem paths;
  - database DSNs;
  - SQL;
  - environment variables;
  - auth headers;
  - tokens;
  - source URLs containing secrets.

---

# 29. MCP media and icons

## 29.1 Images

Presentation previews are a real use of standard MCP image content.

Use the SDK's image helpers or direct `ImageContent` construction from **in-memory PNG bytes**.

Do not require the model to know a filesystem path merely to view a preview.

## 29.2 Audio

MCP supports `AudioContent`, and the Office server must not be architected in a way that makes audio content impossible in the future.

However, Office v1 has no meaningful audio-returning feature that needs to exist merely to tick a protocol box.

Current policy:

```text
AudioContent protocol compatibility: yes
Office v1 audio feature: none
```

If domOXML later supports extracting/authoring presentation audio meaningfully, add media resources/tools then.

## 29.3 Icons

Use standard MCP `Icon` metadata on:

- the Office server;
- major tool families;
- resource families;
- prompts.

Icons SHOULD use self-contained `data:` SVG URIs so clients need no network fetch.

Provide light/dark variants where the mark requires it.

Suggested icon families:

- Office/server;
- presentation;
- slide;
- element/edit;
- preview;
- validate;
- export.

Do not overdecorate every minor tool with a unique visual language if it makes the plugin visually noisy.

---

# 30. Structured tool results and `_meta`

Every conventional data-returning tool should use a typed Pydantic result so the official SDK produces an output schema and structured content.

Remember the MCP split:

- `content` is model-readable content;
- `structured_content` is typed application-readable data;
- `_meta` is application metadata not intended to be part of the model answer.

Use `_meta` sparingly for things such as:

- trace IDs;
- render cache hit/miss;
- UI-specific non-semantic presentation information;
- diagnostic identifiers.

Do not hide information the model needs to make the next decision solely in `_meta`.

For tools that need mixed content blocks (e.g. images + typed metadata or ResourceLink + typed metadata), construct the MCP result explicitly if necessary rather than flattening everything into text.

---

# 31. Resource subscriptions and invalidation

Office should support modern MCP `subscriptions/listen` behaviour through the SDK.

Clients can ask to watch exact resource URIs or list-change categories. The server publishes what changed; the client refetches.

## 31.1 Mutation invalidation matrix

### Any presentation mutation

Notify update for:

```text
office://presentations/{id}
office://presentations/{id}/outline
office://presentations/{id}/validation
office://presentations/{id}/preview
```

### Slide mutation

Additionally notify:

```text
office://presentations/{id}/slides/{slide_id}
office://presentations/{id}/slides/{slide_id}/source
office://presentations/{id}/slides/{slide_id}/preview
```

### Element mutation

Additionally notify exact element resource when one exists:

```text
office://presentations/{id}/slides/{slide_id}/elements/{element_id}
```

### Create/delete presentation

Publish resource-list changed.

### Export

An immutable revision file resource does not “change”; once created it stays identical. Creating a new latest revision may invalidate any mutable latest-file convenience resource if one is exposed.

## 31.2 Subscription security

In future multi-user/remote mode, the same authorization decision used for resource reads must gate subscriptions.

Do not allow a caller to subscribe to an otherwise inaccessible URI and infer activity from notifications.

Use a uniform not-found/denied behaviour to avoid resource existence leaks.

## 31.3 Multi-worker deployment

The SDK's default subscription bus is process-local.

A multi-replica remote deployment must provide a shared `SubscriptionBus` implementation (for example Redis/NATS/Postgres pubsub) so a mutation on replica B reaches a subscription stream held by replica A.

This is not required for initial local stdio mode, but the seam must remain clean.

---

# 32. Modern MCP vs legacy clients

The official Python SDK v2 can serve current and older MCP clients from the same server.

Office should test both.

Modern `2026-07-28` expectations:

- stateless request semantics;
- optional discovery via `server/discover`;
- no reliance on session identity;
- modern extension negotiation;
- `subscriptions/listen` where supported;
- multi-round-trip request mechanism for client input where ever used.

Legacy expectations:

- official SDK compatibility without separate server code;
- no assumption that modern extensions are visible;
- older subscription mechanisms may be SDK-managed;
- features unavailable on the old protocol must degrade cleanly.

Do not fork Office business logic into “legacy” and “modern” implementations.

---

# 33. MCP features deliberately not used in v1

A high-quality MCP implementation does not implement a feature merely because the protocol once had it.

| MCP feature | Office v1 decision |
|---|---|
| Tools | **Yes** |
| Structured output | **Yes** |
| Resources | **Yes** |
| Resource templates | **Yes** |
| Prompts | **Yes** |
| Completions | **Yes** |
| Progress | **Yes** |
| Image content | **Yes** |
| Audio content | Protocol-compatible, no Office feature yet |
| Icons | **Yes** |
| Cursor pagination | **Yes**, where catalogue size warrants it |
| Subscriptions | **Yes** |
| Tool annotations | **Yes** |
| MCP extensions | Extension-ready; no required custom extension in portable v1 |
| Elicitation / Resolve | Use only if a genuine user-only input requirement appears |
| Multi-round-trip | Architecture-compatible through SDK |
| Authorization | Optional remote deployment profile; not required for local stdio |
| OpenTelemetry | Recommended optional instrumentation |
| MCP Apps | Not required for v1; evaluate separately later |
| Tasks extension | Defer until official current SDK support is ready/needed |
| Roots | **Do not build on it; deprecated** |
| Sampling | **Do not build on it; deprecated for new designs** |
| Protocol logging | **Do not build on it; deprecated** |
| Ping | **No; removed** |
| Legacy SSE transport | Do not configure for new plugin deployments unless compatibility requires it |

---

# 34. Search architecture

## 34.1 Search is presentation-semantic

`presentation_search` remains part of Office even if a separate Files MCP exists in the future.

Examples that belong to Office:

```text
Find the deck where the pricing slide mentions £19.
Find the presentation with a slide about Gremlin cross-tenancy.
Find the Cascade deck I updated recently.
```

A Files MCP may search filenames/paths/generic contents, but it should not replace Office's domain-aware presentation search.

## 34.2 Standalone FTS

Use SQLite FTS5 initially.

Index extracted plain text, never raw HTML markup.

Recommended searchable fields:

- presentation name (high weight);
- presentation description;
- slide name (high weight);
- slide description;
- visible slide text.

Search snippets must:

- be short;
- be HTML-free/plain text;
- not contain preservation payloads;
- not leak inaccessible presentation existence.

## 34.3 Semantic search later

Embedding/semantic search may be added later behind the same search service if useful. Do not require an embedding provider for portable v1.

---

# 35. Preview architecture

## 35.1 Why preview is both a tool and a resource

The preview is a representation, so it naturally exists as a resource.

The model also frequently needs to **deliberately request a visual check**, so `presentation_preview` is a useful convenience tool.

Canonical behaviour:

```text
Tool call
  presentation_preview(...)
       ↓
Preview service/cache
       ↓
standard ImageContent result

Resource read
  office://.../preview
       ↓
same Preview service/cache
```

Do not maintain two render implementations.

## 35.2 Contact sheet algorithm

Contact sheets should:

- preserve each slide's exact aspect ratio;
- add consistent spacing;
- place labels outside slide pixels;
- choose columns deterministically in `auto`;
- stay within practical max image dimensions;
- split large decks across several sheets;
- include returned structured mapping from sheet/page to slide IDs;
- never shrink slides to the point text becomes entirely useless if splitting would be better.

Suggested auto column policy can start approximately:

```text
1 slide    → single
2–4        → 2 columns
5–9        → 3 columns
10–20      → 4 columns
21–30      → 5 columns
>30        → multiple sheets
```

Tune empirically with model vision tests.

## 35.3 Preview caching

Cache key should include:

- presentation ID;
- immutable revision ID;
- slide selection;
- quality;
- labels;
- columns/layout;
- renderer version when output can change across renderer upgrades.

Because revision IDs are immutable, preview cache invalidation is straightforward.

---

# 36. domOXML adapter requirements

Office must isolate domOXML-specific details behind an adapter.

Business/MCP code should not import deep domOXML internals everywhere.

Adapter responsibilities:

- create domOXML `Presentation`/`Slide` instances;
- map Office `SlideSize` to domOXML current `SlideSize` / `CustomSize`;
- map transitions;
- import PPTX through domOXML's reverse path;
- render PPTX/PNG/HTML;
- convert coverage reports into Office validation models;
- preserve warnings;
- preserve unsupported reverse constructs according to domOXML's retention facilities;
- translate model-facing inline HTML into domOXML-compatible source;
- translate domOXML normalised HTML into model-facing inline source;
- isolate temporary files if domOXML currently requires `Path` APIs.

If domOXML's public API changes, only this adapter and compatibility tests should require broad modification.

## 36.1 No silent loss

Office should inherit domOXML's parity-first invariant.

Any visible construct that cannot be represented natively should become:

- decomposed/hybrid/layered/rasterised where domOXML supports it;
- preserved source plus explicit warning/debt;
- or explicit failure.

It must never silently vanish.

---

# 37. Temporary filesystem use

The AI/model does **not** need a filesystem.

The Office server MAY internally use isolated temporary filesystem space because domOXML/Playwright/PPTX ZIP processing may require it.

Rules:

- unique temporary directory per operation;
- restrictive permissions where the platform supports them;
- no predictable user-controlled directory names;
- no use of presentation name as an unsanitised path;
- hard byte/file count quotas;
- cleanup in `finally`/context manager;
- crash-recovery garbage collection for stale temp directories;
- never return temp paths to the model;
- never accept arbitrary output paths from the model.

Long-term, prefer byte/file-like-object domOXML APIs where practical, but do not block v1 on removing every internal temp file.

---

# 38. Asset and external content policy

Slides can contain images and potentially remote assets. This creates security and reproducibility concerns.

## 38.1 Model-authored image sources

Initially allow:

- `data:` images within reasonable size limits;
- `https:` images if network asset fetch is enabled and SSRF-safe;
- Office-managed internal asset URIs if the adapter introduces them.

Do not permit arbitrary `file:` images by default.

## 38.2 Asset snapshotting

When an external image is successfully used in a committed presentation, Office SHOULD snapshot the bytes into presentation-managed storage rather than depending forever on a mutable third-party URL.

This ensures:

- deterministic future exports;
- offline reopening;
- protection from source URL changes;
- stable revision semantics.

Record source provenance separately if useful.

## 38.3 Fonts

Font handling must follow domOXML reality. Do not promise arbitrary web-font download/embedding unless tested.

If font fetch is supported, apply the same network/size/security rules as other assets.

---

# 39. Future harness / artifact integration

The custom multi-user AI agent/harness does not exist yet. Office must therefore define seams, not hard dependencies.

## 39.1 What the future harness owns

The future harness may own:

- users/tenants/workspaces;
- a general artifact/file library;
- blob storage;
- global search;
- upload/download UX;
- permissions;
- plugin installation/runtime;
- host-level file attachment semantics.

None of these belongs in the Agent Plugins portable standard itself.

## 39.2 What Office owns

Office owns:

- presentation semantics;
- PPTX import/export;
- slide/element editing;
- presentation search semantics;
- previews;
- validation;
- standalone private persistence.

## 39.3 Integration seams to create now

Create these abstract seams before writing the local implementation:

```python
PresentationStore
InputResolver
OutputSink
RequestScopeProvider
```

A future harness adapter can implement them.

Do not scatter calls to `${PLUGIN_DATA}` throughout business logic.

## 39.4 Agent Plugins client extension

When the harness exists, it may advertise a reverse-domain Agent Plugins client extension in `plugin.json.extensions` and/or a matching extension directory.

That extension could describe host capabilities such as:

- artifact bridge availability;
- supported input URI schemes;
- automatic export attachment;
- host-managed persistent store integration.

The extension is optional and client-owned.

## 39.5 MCP extension

If wire-level runtime cooperation is genuinely needed, MCP 2026 provides an opt-in extension framework.

A future extension must:

- use a reverse-DNS `vendor-prefix/name` identifier;
- be off by default;
- be capability-negotiated;
- augment Office rather than becoming the only way Office works;
- remain invisible to legacy clients that cannot negotiate it;
- not expose cross-user storage merely because a client advertises support.

Do **not** invent the final artifact extension protocol in v1. Keep the internal seams ready and design that extension when the host architecture is concrete.

---

# 40. Multi-user and remote deployment safety

Although the portable plugin starts as stdio/private state, the codebase must not make shared remote deployment unsafe by construction.

## 40.1 Principal is hidden from model inputs

No tool should accept:

```text
user_id
tenant_id
workspace_owner
```

for authorization purposes.

In remote mode, request identity comes from authenticated request context/middleware/dependency injection.

The model cannot choose whose namespace it operates in.

## 40.2 IDs are not capabilities

Knowing:

```text
prs_...
sld_...
el_...
rev_...
```

grants no access by itself.

Every store/resource/search/completion/subscription operation must be scoped by hidden request scope/principal.

Prefer APIs that structurally require scope:

```python
store.get(scope, presentation_id)
```

rather than:

```python
presentation = store.get(presentation_id)
if presentation.owner != current_user:
    ...
```

The latter can be secured, but the former makes accidental unscoped reads harder to write.

## 40.3 Scope every protocol surface

Future multi-user deployments must scope:

- `presentation_search`;
- `resources/list`;
- `resources/read`;
- resource template reads;
- completion suggestions;
- revision reads;
- preview reads;
- exported files;
- subscription requests;
- notification delivery;
- caches;
- pagination/search cursors;
- temporary workspaces where shared infrastructure is used.

## 40.4 Existence leakage

For inaccessible IDs/URIs, prefer behaviour equivalent to “not found” rather than revealing:

```text
You don't have access to Alice's presentation.
```

Do not expose another user's object existence through:

- different error text;
- timing where practical to avoid;
- autocomplete;
- resource counts;
- subscription acceptance;
- cursor tampering.

## 40.5 Remote storage

For a shared deployment, do not use one unscoped `${PLUGIN_DATA}` directory as the user database.

Use an actual multi-tenant backing store adapter (e.g. Postgres/object store), with principal-scoped access.

## 40.6 MCP HTTP deployment

Use the official SDK's modern Streamable HTTP deployment surface.

Configure transport security explicitly:

- host allowlist;
- origin allowlist when browser clients are used;
- TLS at deployment edge;
- current OAuth/resource-server support where authentication is required;
- no dependency on sticky sessions for modern 2026 traffic;
- legacy-client considerations documented separately.

When scaling replicas:

- share any request-state security keys required by the SDK for modern multi-round-trip flows;
- provide shared subscription bus;
- keep application state in shared storage, not process memory.

---

# 41. Caching

Use immutable revision IDs to make caching simple.

Suitable immutable caches:

```text
rev → PPTX export
rev + slide → PNG preview
rev + preview options → contact sheet
rev → validation summary
```

Mutable “latest” representations should resolve to a revision and then use immutable cache keys.

List-result caching must preserve deterministic order.

Never cache cross-principal results under keys missing scope identity in multi-user mode.

---

# 42. Observability

Do not build new systems on deprecated MCP protocol logging.

Use normal application observability:

- Python `logging`;
- OpenTelemetry spans/metrics when enabled;
- structured event fields;
- operation IDs;
- durations;
- render/import/export byte sizes;
- cache hit/miss;
- domOXML warning counts;
- revision IDs;
- presentation IDs (subject to privacy/log retention policy).

Never log raw presentation source or binary content by default.

Potential spans:

```text
office.tool.presentation_open
office.domoxml.import
office.domoxml.render
office.preview.contact_sheet
office.storage.commit
office.search.query
```

---

# 43. Limits and quotas

Even local software should have sane limits; remote deployments absolutely require them.

Make limits configurable with safe defaults.

Suggested initial categories:

- max PPTX input bytes;
- max slides per presentation;
- max slides in one add call;
- max HTML bytes per slide;
- max element mutations per call;
- max remote asset bytes;
- max total assets per presentation/revision;
- max preview dimensions;
- max contact-sheet slides per image;
- max search query length;
- max search results per call;
- max concurrent Chromium render operations;
- operation timeout;
- max decompressed ZIP size / ZIP bomb protection.

PPTX is a ZIP-based package; import code must protect against decompression bombs and pathological archive entries.

---

# 44. Security requirements

## 44.1 HTML sanitisation

Reject or strip:

- scripts;
- event handlers;
- iframe/object/embed active content;
- dangerous URL schemes;
- external stylesheet injection;
- unsafe browser navigation mechanisms.

Run Chromium in a locked-down context suitable for untrusted authored markup.

## 44.2 Network isolation

Default should be no unrestricted network access during render.

If remote assets are supported, intercept requests and apply allow/deny/size policies explicitly.

Do not let authored HTML use Chromium as an SSRF proxy into:

- `localhost`;
- RFC1918/private networks;
- link-local addresses;
- cloud metadata IPs;
- Unix/file schemes;
- internal DNS names where policy disallows them.

## 44.3 PPTX package safety

Treat imported Office files as untrusted archives/XML.

Requirements:

- ZIP bomb defenses;
- bounded XML parsing;
- no external entity resolution;
- no execution of embedded macros/code;
- relationship target validation;
- sane media size limits;
- no trusting package filenames as paths.

If `.pptm` or macro-enabled content is unsupported, reject explicitly rather than silently stripping macros and claiming lossless import.

## 44.4 Local path safety

If `file:` inputs are enabled, use explicit allowed roots and safe join/canonicalisation. Do not treat MCP URI-template path prefilters as the final filesystem containment boundary.

## 44.5 Output filenames

User/model-provided export filenames are display names, not filesystem paths.

Sanitise path separators and reserved names. Never allow `../../foo.pptx` to choose an output location.

---

# 45. Tool descriptions

Tool descriptions are part of agent usability. They must be short but decision-oriented.

Examples:

### `presentation_inspect`

> Inspect presentation metadata and slide outline without loading slide HTML. Use this first to understand an existing deck and locate the right slide.

### `slide_inspect`

> Inspect one slide. `structure` returns a compact element tree; `source` returns the full normalised inline-styled HTML. Prefer `structure` unless you need to redesign or inspect exact styles.

### `element_update`

> Atomically update one or more elements on one slide. Use for normal text, style, attribute, or subtree edits instead of replacing the whole slide.

### `presentation_preview`

> Render selected slides for visual inspection. A single slide returns a detailed image; multiple slides default to compact contact sheets to avoid image spam.

### `presentation_validate`

> Validate the current revision and report domOXML representation/editability/source-retention coverage, warnings, and failures. This checks conversion quality, not visual aesthetics.

Descriptions should tell the model **when to use the tool relative to adjacent tools**.

---

# 46. Implementation architecture

Recommended layering:

```text
MCP handlers
    │
    ▼
PresentationService
    │
    ├── PresentationStore
    ├── InputResolver
    ├── OutputSink
    ├── PreviewService
    ├── SearchService
    └── DomOXMLAdapter
            │
            ▼
          domOXML
```

MCP handlers should be thin:

1. receive validated typed arguments;
2. resolve hidden request scope/dependencies;
3. call domain service;
4. map known errors to tool errors;
5. publish resource invalidations;
6. return structured/mixed MCP result.

Do not place SQL, Playwright page manipulation, or raw XML logic inside tool functions.

---

# 47. Lifespan and process resources

Use MCP server lifespan for expensive process-wide resources that should be created once:

- SQLite connection pool/manager;
- Chromium browser process/pool;
- domOXML adapter configuration;
- HTTP client used by safe input resolver;
- preview cache;
- optional telemetry provider.

The current Python SDK v2 runs Streamable HTTP lifespan once at application startup, not once per modern request. Design pools accordingly.

Per-request temporary directories and page contexts still belong to the request/operation, not global lifespan.

---

# 48. Protocol compliance implementation notes

## 48.1 High-level vs low-level server

Default to `MCPServer`.

Use low-level `Server` only for:

- true `resources/list` pagination if needed;
- exact result composition not supported conveniently by `MCPServer`;
- future custom extension methods where high-level extension binding does not suffice.

If a low-level handler is used, remember:

- it does not automatically validate arbitrary tool argument JSON against advertised schemas the same way high-level decorated tools do;
- unexpected exceptions become sanitised protocol errors;
- model-recoverable errors need explicit `CallToolResult(is_error=True)`;
- exact output schemas/structured content become implementation responsibility.

## 48.2 Pydantic schema tests

Snapshot or assert important generated JSON Schema properties:

- enum values;
- required fields;
- discriminators;
- bounds;
- `additionalProperties` behaviour where generated;
- output schemas.

The stated goal is “fully typed”; tests should make schema regressions visible.

---

# 49. Testing strategy

A serious Office MCP requires more than unit tests for Python functions.

## 49.1 Unit tests

Cover:

- ID generation/validation;
- patch semantics;
- slide reorder validation;
- selector ambiguity;
- element mutation validation;
- HTML sanitisation;
- CSS style parsing/mutation;
- cursor encoding/decoding;
- search query filters;
- filename sanitisation;
- source URI policy;
- SSRF address classification;
- ZIP size guards;
- contact-sheet layout calculation.

## 49.2 domOXML adapter integration tests

Cover:

```text
HTML → PPTX
HTML → PNG
PPTX → normalised HTML
PPTX → edit → PPTX
HTML → PPTX → HTML → PPTX
```

Use real fixtures and compare:

- no crash;
- expected element counts;
- expected warnings;
- stable IDs where Office promises them;
- package validity;
- visual/golden evidence where appropriate.

Reuse domOXML's own fidelity/capability philosophy rather than duplicating a contradictory test definition.

## 49.3 Protocol tests with official MCP Client

Use in-memory:

```python
from mcp import Client

async with Client(mcp) as client:
    ...
```

Test current protocol by default.

Also run a compatibility suite against legacy mode supported by the SDK.

Test:

- server info/instructions/icons;
- tool listing;
- tool schemas;
- structured outputs;
- tool error behaviour;
- resource listing;
- pagination;
- resource reads;
- binary resource reads;
- resource templates;
- prompts;
- completions;
- preview ImageContent;
- export ResourceLink/resource bytes;
- progress callbacks;
- subscription/listen invalidation;
- list-changed notifications;
- unsupported modern feature graceful behaviour on legacy mode.

## 49.4 Agent Plugins conformance tests

Validate:

- `plugin.json` against the pinned Agent Plugins 1.0.0 schema;
- `mcp.json` against the matching schema;
- both schemas declare the same Agent Plugins version;
- plugin-relative paths remain inside plugin root;
- no forbidden manifest fields;
- skill discovery path is valid;
- `SKILL.md` validates against Agent Skills;
- `mcp.json` uses valid command token/args/cwd/env semantics;
- no attempt to set reserved `PLUGIN_ROOT` or `PLUGIN_DATA` in `env`.

Do not fetch schemas dynamically at plugin runtime. Test tooling may vendor/pin them or retrieve them in CI under controlled build logic, but runtime loading follows the Agent Plugins client contract.

## 49.5 Golden visual tests

Fixtures should cover:

- typography;
- multi-line text;
- gradients;
- borders;
- shadows;
- images;
- SVG/custom geometry where supported;
- tables;
- groups;
- imported unsupported/preserved constructs;
- transitions metadata;
- 16:9 / 4:3 / 16:10 / custom sizes.

For preview/contact-sheet code, golden images should test:

- slide ordering;
- labels;
- aspect ratio;
- multi-sheet splitting;
- high/standard quality sizing.

## 49.6 Mutation tests

Examples:

1. Create slide with named elements.
2. Inspect structure.
3. Update three elements in one call.
4. Confirm one new revision.
5. Confirm unchanged element IDs remain stable.
6. Confirm changed values appear in source and preview.
7. Export and re-import.
8. Confirm expected source/semantic continuity.

## 49.7 Revision conflict tests

Run two logical editors:

```text
A reads rev1
B updates → rev2
A writes expected rev1 → conflict
A re-inspects rev2
A retries → rev3
```

## 49.8 Security tests

Fuzz/test:

- `../../` paths;
- symlink escape;
- null bytes;
- Windows drive paths;
- `file:///etc/passwd` when file resolver disabled;
- HTTP redirect to `127.0.0.1`;
- DNS that resolves to private IP;
- `169.254.169.254` metadata target;
- ZIP bomb-like ratios;
- XXE payloads;
- `<script>`;
- `onclick=`;
- `javascript:` URLs;
- CSS URL to internal host;
- model-supplied `data-office-id` spoofing;
- duplicate semantic element names;
- invalid move cycles;
- cursor tampering;
- resource subscription to inaccessible URI.

## 49.9 Multi-user isolation tests

Even if the local store is single-scope, build a test in-memory multi-scope store adapter.

Create scope A and scope B and assert that B cannot:

- search A presentations;
- read A resource URI;
- complete A IDs;
- subscribe to A resources;
- preview A slide;
- export A revision;
- use A cursor;
- access A by guessing opaque IDs.

This makes future SaaS deployment safer before it exists.

---

# 50. Quality gates

At minimum CI should run:

```text
ruff check
ruff format --check
pyright
pytest
```

Match domOXML's quality baseline where practical.

Additional recommended gates:

- JSON schema validation of Agent Plugin manifests;
- Agent Skill validation;
- `mcp` in-memory protocol tests;
- generated schema snapshot tests;
- package import/start smoke test;
- Chromium presence/render smoke test;
- vulnerability/dependency scan;
- secret scan.

Do not make slow external Graph fidelity tests mandatory for every local commit if they require credentials/network. Keep credentialed fidelity checks opt-in or CI-secret protected.

---

# 51. Performance goals

There are no fake microsecond promises, but the architecture should avoid obvious context/compute waste.

## 51.1 Context efficiency

- presentation inspect returns outline, not HTML;
- slide structure returns compact tree, not CSS;
- full source is opt-in;
- element updates batch;
- slide creation batches;
- contact sheets reduce image-tool spam;
- export bytes travel as resource content, not model text.

## 51.2 Runtime efficiency

- keep Chromium/browser process warm where safe;
- isolate per-render pages/contexts;
- cache immutable revision renders;
- index search incrementally per revision;
- avoid re-exporting identical revision/options;
- use bounded concurrency to prevent Chromium stampedes;
- avoid repeated PPTX re-import for every element edit when canonical working state is already persisted.

---

# 52. Capability truthfulness

Office must distinguish:

- what MCP supports;
- what the Office plugin implements;
- what domOXML can represent natively;
- what domOXML can preserve/rasterise;
- what remains unsupported.

Do not write tool descriptions claiming features merely because PowerPoint can theoretically do them.

In particular, v1 should not fabricate first-class authoring APIs for features that domOXML currently does not genuinely support end-to-end.

Potential future features include:

- native chart authoring/editing;
- richer animation authoring;
- speaker notes;
- embedded video/audio authoring;
- full master/layout authoring;
- DOCX Flow IR;
- XLSX Grid/Data IR.

Expose them only when backed by tested implementation.

---

# 53. Office v2/vFuture namespace evolution

When document/workbook support arrives, keep the same Office Agent Plugin and add sibling tool families rather than overloading presentation tools.

Expected shape:

```text
presentation_create
presentation_inspect
...

document_create
document_inspect
...

workbook_create
workbook_inspect
...
```

Likewise resources:

```text
office://presentations/...
office://documents/...
office://workbooks/...
```

Do not rename v1 presentation tools later just because Office grew.

---

# 54. Codex implementation plan

Codex should implement in staged, reviewable phases. Do not attempt a giant single-pass implementation with half-tested protocol surfaces.

## Phase 0 — repository/plugin scaffold

Deliver:

- `plugins/office/` package root;
- `plugin.json`;
- `mcp.json` development launcher;
- plugin README;
- this DESIGN.md;
- presentation Agent Skill skeleton;
- Python server package;
- lint/type/test configuration;
- basic CI integration.

Acceptance:

- Agent Plugins JSON files validate;
- server starts;
- official MCP Client connects in memory;
- server exposes identity/instructions/icon.

## Phase 1 — core models, IDs, storage abstractions

Deliver:

- strict common Pydantic models;
- enums/unions in this design;
- opaque ID generator;
- revision model;
- `PresentationStore`, `InputResolver`, `OutputSink`, `RequestScopeProvider` protocols;
- local SQLite/blob implementation;
- FTS index scaffolding.

Acceptance:

- schema tests pass;
- create/get/commit/search/delete store tests pass;
- optimistic revision conflicts pass;
- multi-scope fake adapter isolation tests pass.

## Phase 2 — domOXML adapter

Deliver:

- create/render/import adapter;
- size/transition/theme mapping;
- normalised HTML adapter;
- coverage/warning adapter;
- temp workspace management;
- PPTX/PNG/HTML integration fixtures.

Acceptance:

- simple deck round-trip works;
- imported deck yields slide source + warnings;
- output PPTX opens/validates;
- PNG preview generated;
- no temp path leaks.

## Phase 3 — HTML policy and element identity

Deliver:

- sanitiser;
- inline CSS enforcement;
- `data-office-id` assignment;
- semantic `data-office-name` support;
- model-facing source normaliser;
- element tree service;
- element selectors.

Acceptance:

- scripts/event handlers rejected;
- ID spoofing impossible;
- named-element lookup works;
- ambiguous names fail explicitly;
- identity survives ordinary small edits.

## Phase 4 — presentation/slide/element tools

Deliver all conventional domain tools except preview/export special content wiring if needed.

Acceptance:

- all tool schemas match design;
- tool annotations/titles present;
- batch edits atomic;
- one mutation = one revision;
- full-slide escape hatch works;
- search works.

## Phase 5 — preview, validation, export

Deliver:

- validation mapping;
- single-slide preview;
- contact-sheet preview;
- preview cache;
- immutable PPTX export;
- ResourceLink result.

Acceptance:

- preview returns standard ImageContent;
- contact sheet does not emit one block per slide for normal decks;
- validation reflects domOXML coverage;
- exported resource bytes hash to metadata SHA-256;
- exact revision export is immutable.

## Phase 6 — resources, pagination, completions

Deliver:

- static capability resource;
- resource templates;
- binary file resources;
- resource-list true cursor pagination;
- presentation/slide dependent completions.

Acceptance:

- official MCP Client reads every resource type;
- cursor drain returns every presentation exactly once;
- tampered cursor rejected;
- completions are scope-safe;
- URI traversal/security tests pass.

## Phase 7 — subscriptions, prompts, icons, progress

Deliver:

- invalidation matrix;
- modern subscription publishing;
- MCP prompts;
- icons;
- progress on long operations;
- completed presentation skill/reference docs.

Acceptance:

- subscribed preview/slide resources notify after mutation;
- resource list change notified after create/delete;
- prompts list/get correctly;
- completions work for prompt args where relevant;
- progress monotonicity test passes;
- no deprecated protocol logging used.

## Phase 8 — security hardening

Deliver:

- SSRF-safe HTTPS resolver if enabled;
- file resolver containment if enabled;
- ZIP bomb limits;
- XML hardening;
- render network policy;
- output filename sanitisation;
- rate/concurrency limits;
- structured safe logging.

Acceptance:

- security test corpus passes;
- no secrets/paths in model-facing unexpected errors;
- malicious source fixtures cannot access forbidden local/internal resources.

## Phase 9 — compatibility and release packaging

Deliver:

- modern + legacy MCP protocol tests;
- packaged launcher strategy;
- reproducible dependency/runtime installation;
- Chromium bootstrap/docs;
- final plugin README;
- root repo catalogue entry.

Acceptance:

- clean checkout/install instructions work;
- plugin starts from Agent Plugins `mcp.json`;
- modern and supported legacy MCP clients work;
- no assumptions about the future custom harness.

---

# 55. Codex rules / non-negotiables

When handing this to Codex, include or copy these rules into the nearest `AGENTS.md`:

1. Read this entire design before changing Office architecture.
2. Inspect current domOXML code/API before writing adapters; never guess its API from memory.
3. Inspect current Agent Plugins spec/schema before changing `plugin.json` or `mcp.json`.
4. Inspect current official Python MCP SDK v2 docs/API before implementing protocol features.
5. Use official `mcp` Python SDK v2.
6. Do not introduce FastMCP v1 imports.
7. Do not expose OOXML/XML primitives as agent tools.
8. Do not introduce shape-level micro-tools.
9. Do not silently loosen inline-CSS/HTML sanitisation.
10. Do not make `data-office-id` caller-controlled.
11. Do not use slide numbers as persistent identities.
12. Do not skip output/result typing because “it works”.
13. Do not return giant binary/base64 blobs as text.
14. Do not bypass MCP native resources/completions/progress/subscriptions when they fit.
15. Do not implement deprecated MCP roots/sampling/logging as new dependencies.
16. Do not add the future harness as a required dependency.
17. Do not assume the AI/model has filesystem access.
18. Do not make local file access enabled by default.
19. Do not make arbitrary outbound HTTP fetch unrestricted.
20. Do not store user/tenant identity in model-supplied arguments.
21. Do not use object IDs as authorization.
22. Do not swallow domOXML warnings/coverage debt.
23. Do not claim unsupported Office capabilities.
24. Do not remove tests to get the build green.
25. Prefer a small correct implementation with explicit unsupported errors over a fake broad implementation.

---

# 56. Detailed acceptance scenarios

The following scenarios should all work before calling presentation v1 complete.

## Scenario A — create from scratch

User asks for a seven-slide pitch deck.

Agent can:

1. call `presentation_create` with seven named slides;
2. receive one presentation ID and revision;
3. call `presentation_preview` once;
4. visually identify one dense slide;
5. inspect its structure;
6. modify elements;
7. preview only that slide;
8. validate;
9. export PPTX.

No filesystem path is required in the model conversation.

## Scenario B — tiny edit

Existing slide contains:

```text
$1.2M ARR
8,400 customers
December 2025
```

Agent should update all three using one `element_update`, not send the entire slide HTML.

Expected:

- one new revision;
- stable untouched element IDs;
- one activity label;
- no full slide replacement.

## Scenario C — redesign one slide

A slide is fundamentally bad.

Agent may:

1. inspect source;
2. call `slide_update(html=...)`;
3. preview slide;
4. refine elements.

Full-slide replacement is valid here.

## Scenario D — duplicate layout

Agent wants a second metrics slide based on an existing slide.

Use:

```text
slide_duplicate
→ element_update
```

not inspect-copy-recreate-all-markup manually.

## Scenario E — imported PPTX

Input PPTX contains native editable content plus unsupported construct.

Expected:

- import succeeds if visible preservation is possible;
- warnings describe unsupported/preserved behaviour;
- model-facing source is editable;
- export retains preserved source according to domOXML capability;
- validation reports actual representation/editability.

## Scenario F — huge deck preview

80-slide deck.

`presentation_preview(all)` should return bounded multiple contact sheets, not 80 image blocks.

Structured metadata maps sheets to slide IDs.

## Scenario G — search later

After restart, standalone Office finds a persistent presentation by name/slide text through `presentation_search`.

No conversation memory is required to remember where the file was.

## Scenario H — revision conflict

Two editors update the same presentation concurrently.

Stale expected revision fails safely instead of overwriting newer work.

## Scenario I — resource-native host

A client lists presentations through `resources/list`, autocompletes a presentation ID, reads outline/source/preview resources, and receives resource updates after a tool mutation.

## Scenario J — malicious source

A slide attempts:

```html
<script>fetch('http://169.254.169.254/latest/meta-data')</script>
```

It is rejected/neutralised before execution and cannot perform the request.

---

# 57. README requirements for `plugins/office/`

The plugin README should be user/operator-facing and significantly shorter than this design.

Recommended structure:

```text
# Office
Short value proposition

## Capabilities
Presentation create/open/search/edit/preview/validate/export

## How it works
HTML/CSS → domOXML → editable PPTX

## Installation
Agent Plugins package / development setup

## Usage
A few agent examples

## Tools
Compact table

## Resources
Compact URI table

## Storage
What PLUGIN_DATA means

## Security
Inline CSS / untrusted files / optional network access

## Current limitations
Honest domOXML gaps

## Development
uv / Chromium / tests

## License
```

Do not make README the canonical tool schema. Link to this design or generated reference docs.

---

# 58. Generated documentation

Because tool schemas are strongly typed, generate a reference document from the live Pydantic/MCP registry in CI or a script.

Generated docs can include:

- tool name/title/description;
- input JSON Schema;
- output JSON Schema;
- annotations;
- resource templates;
- prompt arguments;
- completion-enabled fields;
- current capability enum values.

This prevents handwritten docs from drifting away from implementation.

Do not generate `DESIGN.md`; this design expresses intent and architectural reasoning. Generate API/reference docs separately.

---

# 59. Naming conventions

Use snake_case MCP tool names:

```text
presentation_create
slide_update
element_inspect
```

Tool names satisfy MCP's recommended portable character set.

Human UI titles use title case/verb phrases:

```text
Create presentation
Inspect slide
Update elements
```

Python model names use PascalCase.

Resource URIs use lowercase plural nouns.

Opaque IDs use short type prefixes:

```text
prs_
rev_
sld_
el_
```

Do not make IDs sequential database integers on the public surface.

---

# 60. Open questions intentionally deferred

These should not block v1 unless implementation proves they are essential.

1. **Packaged Python/Chromium distribution:** final cross-platform launcher/install story.
2. **MCP Apps UI:** whether Office should later ship a richer interactive slide navigator/editor UI.
3. **Host artifact extension:** exact future harness contract.
4. **Native chart authoring:** only when domOXML supports it robustly.
5. **Animation authoring:** only when domOXML supports it robustly.
6. **Speaker notes:** only when supported intentionally.
7. **Audio/video media:** meaningful Office feature later.
8. **DOCX/XLSX:** future Office capability families.
9. **Semantic/vector presentation search:** optional future enhancement.
10. **Revision pruning/history UX:** full snapshots are acceptable initially.
11. **Soft delete/trash:** may be added later.
12. **Collaborative merge/CRDT:** optimistic concurrency is enough for v1.
13. **Cloud-hosted Office service:** separate deployment profile, same domain contract.

---

# 61. Definition of done

Presentation v1 is done when all of the following are true:

### Agent Plugins

- valid `plugin.json`;
- valid matching `mcp.json`;
- valid Agent Skill;
- plugin lives as a self-contained directory;
- no dependence on undocumented package paths;
- `PLUGIN_ROOT`/`PLUGIN_DATA` used correctly.

### MCP

- official Python SDK v2;
- tools are typed and annotated;
- structured outputs work;
- resources/templates work;
- binary PPTX resource works;
- image preview content works;
- icons work;
- completions work;
- true resource pagination works when store size exceeds one page;
- progress works;
- subscriptions/invalidation work;
- prompts work;
- modern protocol passes;
- supported legacy compatibility passes;
- no new dependency on deprecated roots/sampling/protocol logging;
- no removed ping assumption.

### Office/domain

- create;
- import/open;
- persistent search;
- outline inspect;
- presentation metadata update;
- slide add/inspect/update/duplicate/delete/reorder;
- element inspect/add/update/move/delete;
- stable IDs;
- optimistic revisions;
- preview single/contact-sheet;
- validation/coverage;
- PPTX export;
- inline-CSS model-facing source;
- safe HTML policy;
- honest unsupported-feature reporting.

### Engineering

- unit/integration/protocol/security/golden tests;
- lint/type checks;
- no obvious path/SSRF/ZIP/XML vulnerabilities;
- clean architecture seams for future harness integration;
- no requirement that the AI itself has a filesystem;
- no cross-scope leakage in multi-scope test adapter;
- useful README and generated reference docs.

---

# 62. Final architectural summary

```text
                        AGENT PLUGINS CLIENT
                                │
                                │ loads plugin.json / mcp.json / skill
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         OFFICE AGENT PLUGIN                         │
│                                                                     │
│  skills/presentations                                               │
│                                                                     │
│                       Official MCP SDK v2                           │
│                               │                                     │
│      ┌──────────────┬─────────┼──────────┬──────────────┐            │
│      │              │         │          │              │            │
│    Tools        Resources   Prompts   Completions  Subscriptions     │
│      │              │         │          │              │            │
│      └──────────────┴─────────┴──────────┴──────────────┘            │
│                               │                                     │
│                     PresentationService                             │
│                               │                                     │
│      ┌────────────────────────┼──────────────────────────┐           │
│      │                        │                          │           │
│ PresentationStore        InputResolver               OutputSink      │
│      │                        │                          │           │
│      └────────────────────────┼──────────────────────────┘           │
│                               │                                     │
│                        DomOXMLAdapter                               │
│                               │                                     │
│              HTML/CSS ↔ canonical IR ↔ PPTX/PNG                    │
│                               │                                     │
│                     Playwright / Chromium                           │
└─────────────────────────────────────────────────────────────────────┘

Standalone Agent Plugin:
    Store         → ${PLUGIN_DATA}/office
    Input         → safe configured URI resolvers
    Output        → office:// resources / ResourceLink

Future custom harness:
    Store         → optional harness adapter
    Input         → optional artifact URI resolver
    Output        → optional host artifact sink
    Identity      → hidden authenticated request scope

The MCP tool contract remains the same.
```

The central design idea is simple:

> **Office should feel to an agent like a tiny typed IDE/compiler for presentations, not like remote-control PowerPoint.**

HTML/CSS expresses design. domOXML handles representation. Stable Office IDs make repeated edits cheap. MCP's native primitives make the server discoverable, visual, reactive, and host-friendly. Agent Plugins packages the whole thing portably. A future AI-agent harness may add richer storage and file integration, but it should enhance this plugin rather than be required to make it work.

---

# Appendix A — Suggested tool registry table

| Tool | Static title | Normal use |
|---|---|---|
| `presentation_create` | Create presentation | New deck |
| `presentation_open` | Open presentation | Import existing PPTX |
| `presentation_search` | Search presentations | Find persistent deck |
| `presentation_inspect` | Inspect presentation | Read deck outline/settings |
| `presentation_update` | Update presentation | Rename/theme/size |
| `presentation_validate` | Validate presentation | Fidelity/editability report |
| `presentation_preview` | Preview presentation | Single slide/contact sheets |
| `presentation_export` | Export presentation | Materialise PPTX revision |
| `presentation_delete` | Delete presentation | Remove deck |
| `slide_add` | Add slides | Create one/many slides |
| `slide_inspect` | Inspect slide | Summary/tree/source |
| `slide_update` | Update slide | Metadata/full redesign |
| `slide_duplicate` | Duplicate slide | Reuse layout/content |
| `slide_delete` | Delete slides | Remove slides |
| `slide_reorder` | Reorder slides | Declarative final ordering |
| `element_inspect` | Inspect element | Focused subtree/style read |
| `element_add` | Add element | Insert HTML subtree |
| `element_update` | Update elements | Normal batch edits |
| `element_move` | Move elements | DOM hierarchy/order |
| `element_delete` | Delete elements | Remove elements |

---

# Appendix B — Suggested resource registry

| URI | MIME | Mutability |
|---|---|---|
| `office://capabilities` | `application/json` | version-dependent |
| `office://presentations/{id}` | `application/json` | latest/current |
| `office://presentations/{id}/outline` | `application/json` | latest/current |
| `office://presentations/{id}/validation` | `application/json` | latest/current |
| `office://presentations/{id}/preview` | `image/png` | latest/current |
| `office://presentations/{id}/revisions/{rev}` | `application/json` | immutable |
| `office://presentations/{id}/revisions/{rev}/file` | PPTX MIME | immutable |
| `office://presentations/{id}/slides/{slide}` | `application/json` | latest/current |
| `office://presentations/{id}/slides/{slide}/source` | `text/html` | latest/current |
| `office://presentations/{id}/slides/{slide}/preview` | `image/png` | latest/current |
| `office://presentations/{id}/slides/{slide}/elements/{el}` | `application/json` | latest/current |

---

# Appendix C — Suggested error table

| Code | Recoverable by model? | Typical response |
|---|---:|---|
| `PRESENTATION_NOT_FOUND` | Yes | Search/inspect again |
| `SLIDE_NOT_FOUND` | Yes | Refresh outline |
| `ELEMENT_NOT_FOUND` | Yes | Inspect structure |
| `AMBIGUOUS_ELEMENT_NAME` | Yes | Use element ID |
| `INVALID_PRESENTATION_SOURCE` | Yes | Supply supported source |
| `UNSUPPORTED_SOURCE_SCHEME` | Yes | Use supported URI mechanism |
| `SOURCE_TOO_LARGE` | Sometimes | Reduce/use host artifact bridge |
| `INVALID_PPTX` | Usually | Correct source file |
| `INVALID_HTML` | Yes | Fix markup |
| `UNSAFE_HTML` | Yes | Remove active content |
| `UNSUPPORTED_CSS` | Yes | Use supported styling/fallback |
| `REVISION_CONFLICT` | Yes | Re-inspect latest revision |
| `INVALID_SLIDE_ORDER` | Yes | Supply every slide once |
| `INVALID_ELEMENT_MOVE` | Yes | Correct hierarchy operation |
| `IMPORT_FAILED` | Sometimes | Inspect message/source |
| `RENDER_FAILED` | Sometimes | Simplify/fix slide |
| `VALIDATION_FAILED` | Sometimes | Retry/report implementation issue |
| `EXPORT_FAILED` | Sometimes | Inspect validation/errors |
| `RESOURCE_TOO_LARGE` | Sometimes | Use bounded operation |
| `ACCESS_DENIED` | No details | Treat as not found where appropriate |
| `RATE_LIMITED` | Yes later | Back off |
| `INTERNAL_ERROR` | No | Report trace ID |

---

# Appendix D — Protocol feature checklist for pull requests

Before merging a protocol-affecting change, reviewers should ask:

- [ ] Does this use the official Python MCP SDK v2 API?
- [ ] Does it preserve modern `2026-07-28` behaviour?
- [ ] Does it still behave acceptably for supported older clients?
- [ ] Is the tool input represented by actual JSON Schema types/enums/bounds?
- [ ] Is the tool result typed/structured where appropriate?
- [ ] Does the tool have a useful title?
- [ ] Are `ToolAnnotations` correct?
- [ ] Is a resource a better representation than a tool for this read?
- [ ] Should a resource update notification be published?
- [ ] Should a list-change notification be published?
- [ ] Is there a completion opportunity for a prompt/resource template argument?
- [ ] Is progress meaningful for this operation?
- [ ] Is binary/media content using MCP native content blocks/resources?
- [ ] Are icons useful and standards-compliant?
- [ ] Is cursor pagination using MCP semantics rather than page numbers?
- [ ] Does the change accidentally rely on roots/sampling/protocol logging?
- [ ] Does it introduce hidden session/process-local state that breaks stateless remote scaling?
- [ ] Is every read/write scoped safely for future multi-user deployment?
- [ ] Can opaque IDs/cursors/resource URIs be used to cross scope boundaries?
- [ ] Does any error leak local paths/secrets/internal data?
- [ ] Does it require the model to have a filesystem unnecessarily?
- [ ] Does it preserve domOXML warnings and fidelity debt?

---

# Appendix E — Authoritative links captured for this design

These links were reviewed while producing this document on 2026-08-07. Protocol and SDK behaviour can evolve; re-check them before large future revisions.

## Agent Plugins

- <https://agent-plugins.org/>
- <https://agent-plugins.org/specification>
- <https://agent-plugins.org/plugin-authors>

## MCP

- <https://modelcontextprotocol.io/specification/2026-07-28>
- <https://blog.modelcontextprotocol.io/posts/2026-07-28/>

## Official Python MCP SDK

- <https://py.sdk.modelcontextprotocol.io/>
- <https://py.sdk.modelcontextprotocol.io/whats-new/>
- <https://py.sdk.modelcontextprotocol.io/servers/tools/>
- <https://py.sdk.modelcontextprotocol.io/servers/structured-output/>
- <https://py.sdk.modelcontextprotocol.io/servers/resources/>
- <https://py.sdk.modelcontextprotocol.io/servers/uri-templates/>
- <https://py.sdk.modelcontextprotocol.io/servers/prompts/>
- <https://py.sdk.modelcontextprotocol.io/servers/completions/>
- <https://py.sdk.modelcontextprotocol.io/servers/media/>
- <https://py.sdk.modelcontextprotocol.io/servers/handling-errors/>
- <https://py.sdk.modelcontextprotocol.io/handlers/progress/>
- <https://py.sdk.modelcontextprotocol.io/handlers/subscriptions/>
- <https://py.sdk.modelcontextprotocol.io/advanced/pagination/>
- <https://py.sdk.modelcontextprotocol.io/advanced/extensions/>
- <https://py.sdk.modelcontextprotocol.io/run/deploy/>

## domOXML

- <https://github.com/Daftscientist/domOXML>
- <https://raw.githubusercontent.com/Daftscientist/domOXML/main/spec/architecture.md>
- <https://raw.githubusercontent.com/Daftscientist/domOXML/main/domoxml/types.py>

