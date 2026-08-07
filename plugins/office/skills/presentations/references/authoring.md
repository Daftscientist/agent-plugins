# HTML/CSS authoring

Author each slide as one or more semantic HTML roots with all visual styling in each element's `style` attribute.

```html
<section style="width:100%;height:100%;background:#fff;padding:64px">
  <h1 data-office-name="headline" style="font-size:42px;font-weight:700;color:#111">
    Revenue grew 42%
  </h1>
  <p style="font-size:20px;color:#666">Driven by enterprise adoption.</p>
</section>
```

Use headings, paragraphs, lists, images, tables, and meaningful containers. Do not send `<style>`, stylesheet links, scripts, event handlers, iframes, forms, objects, embeds, `javascript:` URLs, or model-chosen `data-office-id` values. Classes are not a styling mechanism in Office's model-facing dialect.

Use `data-office-name` for unique slide-scoped aliases such as `headline`, `arr-metric`, or `period` when an element will likely be edited again.

CSS remains CSS; Office does not invent a style DSL. Unsupported or lossy CSS appears in validation warnings rather than silently disappearing.
