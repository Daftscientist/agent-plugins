# Office

Office is a portable Agent Plugin for creating, importing, inspecting, editing, previewing, validating, searching, and exporting editable PowerPoint presentations. It uses semantic HTML with inline CSS as the authoring surface and [domOXML](https://github.com/Daftscientist/domOXML) as the presentation compiler.

## Capabilities

- Persistent PPTX workspaces with immutable revisions and optimistic concurrency
- Batch presentation, slide, and stable-element editing
- PPTX import with warnings and preservation metadata
- Single-slide and bounded contact-sheet PNG previews
- domOXML representation/editability/source-retention validation
- SQLite FTS presentation search
- Immutable PPTX export through MCP binary resources

## How it works

`HTML + inline CSS → domOXML typed IR → editable PPTX + PNG + validation`

Office never exposes OOXML to the model. Stable `prs_`, `rev_`, `sld_`, and server-owned `el_` identifiers make repeated edits compact and safe.

## Installation

An Agent Plugins client loads `plugin.json`, `mcp.json`, and the presentation skill. The development launcher requires Python 3.12+, `uv`, and Chromium:

```bash
cd server
uv sync --frozen --extra dev
uv run playwright install chromium
OFFICE_DATA_DIR=/path/to/private/state uv run --frozen python -m office_mcp
```

The source launcher is the current alpha distribution strategy. A future release may bundle a cross-platform runtime without changing the plugin contract.

## Usage

Ask an agent to create a deck, import a PPTX, refresh metrics, reuse a slide layout, preview a presentation, or validate/export a revision. The bundled presentation skill teaches the efficient inspect → element-edit → preview → validate → export workflow.

## Tools

The server exposes twenty high-level operations: nine `presentation_*`, six `slide_*`, and five `element_*` tools. See [the design contract](DESIGN.md) and generated [API reference](API_REFERENCE.md).

## Resources

Office exposes `office://capabilities` plus presentation metadata, outline, validation, preview, immutable revision/file, slide structure/source/preview, and element resources. Presentation roots are listed with true opaque cursor pagination.

## Storage

`OFFICE_DATA_DIR` points to private plugin state containing SQLite, revisions, previews, exports, assets, scratch, and runtime data. It is not a universal user filesystem. Standalone deletion is a documented hard delete.

## Security

Model-authored source is sanitised and limited to inline CSS. JavaScript, active content, event handlers, dangerous URLs, stylesheet injection, and caller-owned Office/domOXML metadata are rejected. Render-time network assets are disabled; use bounded raster `data:` images or safe inline SVG. `file:` and `https:` PPTX input default off; when enabled they enforce containment or DNS-pinned SSRF/redirect/MIME/size policies. Imported PPTX packages receive path, relationship, active-content, type, XML, media, entry-count, compression-ratio, and decompressed-size checks.

## Current limitations

Office follows domOXML's alpha capabilities and does not claim first-class chart authoring, arbitrary animations, notes, audio/video insertion, or master authoring. Imported theme/transition semantics are represented through domOXML's normalized inline source where its reverse API does not expose separate metadata. domOXML's public API does not yet accept its preservation fragments on a modified reverse-import render; Office therefore guarantees byte-identical untouched import export and reports lost preservation debt after content edits instead of claiming losslessness.

## Development

Run `uv run ruff check .`, `uv run ruff format --check .`, `uv run pyright`, and `uv run pytest`. Integration tests use real Chromium and PPTX packages. Generate API docs with `uv run office-docs ../API_REFERENCE.md`.

## License

MIT
