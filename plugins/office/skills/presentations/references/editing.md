# Editing workflows

For small edits, inspect structure and batch selectors in `element_update`. Select by stable ID when known or by a unique semantic name.

- `text` replaces child content with plain text while retaining the target element and ID.
- `inner_html` retains the target and replaces its children.
- `replace_html` replaces one target root and transfers its stable ID.
- `styles.set/remove` patches inline CSS properties.
- `attributes.set/remove` patches safe attributes; Office IDs and event handlers are forbidden.
- `element_move` changes DOM hierarchy/order, not pixel geometry.

Use optimistic `expected_revision` on mutations when coordinating concurrent work. Batch edits that form one user intent, but do not mix unrelated changes merely to reduce calls.
