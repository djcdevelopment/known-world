# SegmentedControl

A row of mono toggle buttons inside a hairline group, used to pick a moment or a layout on the board.

- Markup: a `.kw-controls` row with a `.kw-controls__label` (uppercase, `muted`) and a `.kw-seg` group of `<button type="button" aria-pressed>`.
- The pressed segment fills with `line` and turns `fg`. Focus shows a 2px `accent` ring.
- Labels follow the content rules: `2026-07 · era C`, `proposed`, `current`.
- Standalone toggles (the zone buttons) use `.kw-btn`, which keeps its own `line` border.
- The consumer provides the state: set `aria-pressed` and re-render. There is no script here.
- **Mobile first.** On phones, each label sits above its group, and every segment is at least `touch-target` (44px) tall at 13px. A group wider than the screen scrolls inside itself. From `bp-sm` the labels and groups share one row. With a fine pointer (a mouse), segments drop to the compact 12px size. Wrap standalone toggles in `.kw-btnrow`.
