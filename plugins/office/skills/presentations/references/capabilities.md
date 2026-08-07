# Capabilities and limits

Office v1 creates, imports, searches, inspects, edits, previews, validates, exports, and persists PowerPoint presentations. It supports 16:9, 4:3, 16:10, and custom slide sizes up to 56 inches, plus domOXML's current transition set.

PowerPoint uses one presentation-wide slide size. Office can preview a differing per-slide override, but validation marks it unsupported for PPTX and export requires all effective slide sizes to match.

domOXML converts HTML/CSS through a typed presentation IR to editable PPTX and PNG. Validation reports native, decomposed, hybrid, layered, element-layer, rasterized, approximated, or failed representation together with semantic/components/layers/none editability and source-retention state.

Office v1 does not claim first-class chart authoring, arbitrary animation authoring, speaker notes, audio/video insertion, or master/layout authoring. Imported unsupported constructs are warned about and preserved where domOXML exposes preservation; an untouched imported revision exports the original bytes exactly, while Office explicitly blocks export after content edits when source-only preservation fragments cannot be reattached.

Portable input always supports base64 `data:` PPTX URIs. Local `file:` and remote `https:` input are disabled unless the operator explicitly enables their hardened resolvers.

Render-time remote assets are disabled for reproducibility and SSRF isolation. Use bounded raster `data:` images or safe inline SVG in authored slides.
