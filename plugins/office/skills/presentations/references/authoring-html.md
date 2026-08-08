# HTML/CSS authoring

Technical reference for the model-facing authoring dialect. `DESIGN.md` and `API_REFERENCE.md` are the source of truth for exactly what the sanitizer accepts; this file teaches technique, not the full accepted-property list.

## The model

Each slide root is one or more semantic HTML elements with **inline CSS only** — no `<style>`, no stylesheet links, no CSS classes as a styling mechanism. Every element carries the styles that govern it, so editing one element never has hidden effects on another.

```html
<section style="width:100%;height:100%;background:#fff;padding:64px">
  <h1 data-office-name="headline" style="font-size:42px;font-weight:700;color:#111">
    Revenue grew 42%
  </h1>
  <p style="font-size:20px;color:#666">Driven by enterprise adoption.</p>
</section>
```

Use ordinary semantic elements: `section`/`div` for containers, `h1`–`h6` for headings, `p`/`span` for text, `ul`/`ol`/`li` for lists, `img` for images, `table`/`thead`/`tbody`/`tr`/`th`/`td` for tables, and inline SVG where the current implementation has parity for it.

## Rejected content

Never send `<style>` blocks, external stylesheet links, `<script>`, event-handler attributes (`onclick` and similar), `<iframe>`, `<object>`, `<embed>`, form-submission controls, `javascript:` URLs, or model-chosen `data-office-id` values. None of this is a style preference — it is rejected outright.

## Identity

- `data-office-id` is server-owned. Never invent, copy, or modify it — always use the ID Office returns.
- `data-office-name` is yours to assign: a unique, slide-scoped alias for elements you expect to target again in a future edit, e.g. `headline`, `arr-metric`, `period`.

## Images

Use bounded raster `data:` images or safe inline SVG. Remote image URLs are not fetched at render time — don't author a slide assuming a network image will load. Keep encoded image size reasonable; it inflates every future inspection of that element.

## CSS philosophy

CSS stays CSS — Office does not invent a styling DSL, and there's no need to memorize an Office-specific property list. Unsupported or lossy CSS surfaces through validation warnings rather than silently vanishing, so if `presentation_validate` flags something, treat it as real signal, not noise.

## Small reusable recipes

These illustrate technique — adapt them to content, don't reuse them as fixed templates.

**Hero title**
```html
<section style="width:100%;height:100%;display:flex;flex-direction:column;justify-content:center;padding:96px;background:#0b0b0c">
  <h1 style="font-size:64px;font-weight:800;color:#fff;line-height:1.05;max-width:70%">Zero-trust networking, explained for the board</h1>
</section>
```

**Split content/image**
```html
<section style="width:100%;height:100%;display:flex">
  <div style="flex:1;padding:64px;display:flex;flex-direction:column;justify-content:center">
    <h2 style="font-size:36px;font-weight:700;color:#111">Enterprise adoption drove the quarter</h2>
    <p style="font-size:18px;color:#555;margin-top:16px">New logo growth concentrated in regulated industries.</p>
  </div>
  <div style="flex:1;background:#eee"><img src="data:image/png;base64,..." style="width:100%;height:100%;object-fit:cover"/></div>
</section>
```

**Metric**
```html
<div data-office-name="arr-metric" style="display:flex;flex-direction:column;align-items:flex-start">
  <span style="font-size:80px;font-weight:800;color:#111">$1.8M</span>
  <span style="font-size:18px;color:#777;margin-top:4px">Annual recurring revenue</span>
</div>
```

**Comparison**
```html
<div style="display:flex;gap:48px;width:100%">
  <div style="flex:1;padding:32px;border:1px solid #e5e5e5"><h3 style="font-size:16px;color:#999;text-transform:uppercase;letter-spacing:0.06em">Before</h3><p style="font-size:28px;font-weight:700;margin-top:8px">14 days</p></div>
  <div style="flex:1;padding:32px;border:1px solid #e5e5e5"><h3 style="font-size:16px;color:#999;text-transform:uppercase;letter-spacing:0.06em">After</h3><p style="font-size:28px;font-weight:700;margin-top:8px;color:#0a7d33">36 hours</p></div>
</div>
```

**Simple table**
```html
<table style="width:100%;border-collapse:collapse;font-size:16px">
  <thead><tr><th style="text-align:left;padding:12px 0;border-bottom:2px solid #111;color:#555;font-weight:600">Plan</th><th style="text-align:right;padding:12px 0;border-bottom:2px solid #111;color:#555;font-weight:600">Price</th></tr></thead>
  <tbody>
    <tr><td style="padding:12px 0;border-bottom:1px solid #eee">Starter</td><td style="text-align:right;padding:12px 0;border-bottom:1px solid #eee">$29/mo</td></tr>
    <tr><td style="padding:12px 0;border-bottom:1px solid #eee">Enterprise</td><td style="text-align:right;padding:12px 0;border-bottom:1px solid #eee">Custom</td></tr>
  </tbody>
</table>
```

**Process row**
```html
<div style="display:flex;align-items:center;width:100%;gap:24px">
  <div style="flex:1;text-align:center"><div style="font-size:14px;color:#999;font-weight:600">01</div><div style="font-size:16px;margin-top:8px">Ingest</div></div>
  <div style="width:32px;height:1px;background:#ccc"></div>
  <div style="flex:1;text-align:center"><div style="font-size:14px;color:#999;font-weight:600">02</div><div style="font-size:16px;margin-top:8px">Normalize</div></div>
  <div style="width:32px;height:1px;background:#ccc"></div>
  <div style="flex:1;text-align:center"><div style="font-size:14px;color:#999;font-weight:600">03</div><div style="font-size:16px;margin-top:8px">Export</div></div>
</div>
```

Treat these as a starting gesture, not a rule — real content rarely fits a recipe unmodified.
