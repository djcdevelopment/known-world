# Known World

The visual language of **Known World**, a film of one developer's journey with local AI and AI-collaborative development, told in the manner of the classic nuclear-test timelapse: a dark map, a date ticker, flashes where work lands, and a counter per "nation". The nations are the collaborators (human, ChatGPT, Claude, Codex, automation, local models). A test is a burst of work, yield is how much it moved, and the land is the code that exists.

This system is built from the *Known World Wireframes* board. Every value here comes from that page. It covers the board (the page where the frame is designed) and the frame itself.

**Mobile first.** Portrait is the primary frame: the player is designed at 360×640 CSS px and the export renders that at 1080×1920. Landscape (1920×1080) is the desktop enhancement, so it gets the same zones with more room, not a different film. Every component is written phone-first and widens at `bp-sm` (640px) and `bp-lg` (900px). Touch controls are at least `touch-target` (44px) tall, and only a fine pointer gets the compact size.

## Principles

1. **Why before where.** Each zone answers one question, in the order the eye asks them: *when are we* (ticker), *what is happening* (map), *who and how much* (nations), *when in context* (timeline). Portrait stacks them top to bottom as ticker, nation strip, map, timeline. Landscape lays them out as top-left, centre, right, bottom. *Where* is answered on the map itself, with coast labels.
2. **Signal-gated.** A zone renders only when it has signal. There are no empty panels, no zero rows, and no bare lane column before the first commit.
3. **Negative space is the medium.** In landscape the left edge stays empty, as in the original. In portrait the map runs edge to edge, and the land never touches the sides. The known land is always centred in the safe area, never pushed into a corner.
4. **Motion budget.** The map is the only thing that moves every frame. The timeline scrolls at a constant rate. Numbers change without animation. A nation gets one fade-in at its first event and never slides.
5. **Player chrome is not content.** Transport controls and the scrubber overlay the ruler, hide after three seconds without input, and never appear in the export.

## Content fundamentals

- **Voice.** Plain, declarative, short sentences. State the rule, then the reason: "The left edge is empty by design." Don't use hype, exclamation marks or emoji.
- **Case.** Sentence case for prose and headings. Labels in `mono` are UPPERCASE with 1px tracking (`kw-label`, `kw-section`).
- **Separators.** A middle dot with spaces joins facets: `2026 · 07 · 05`, `commits 4.4k · files 56k · lines 3.2M`, `2 · The frame`.
- **Numbers.** Abbreviate at a thousand: `1.1k`, `3.2M`. Dates read largest-first: `2026 · 07`. Rates read as `1 day = 2.4 s`.
- **Vocabulary from the original.** Use *tests* for events, *yield* for lines moved, *nations* for collaborators, *MIRV* for one commit that lands in several places, and *era* for a rate regime. Keep these words. They are the joke and the frame.
- **Honesty about gaps.** The tally card states what the sources do not cover ("no chat source covers 2026-04"). Never paper over a hole.
- **Names.** Lane labels show real names in a personal cut and hashed names in a public cut.

## Visual foundations

**One theme, dark.** The board uses `bg`, panels use `panel`, and anything inside the frame uses `canvas`, which is a step darker so the frame reads as a screen. Rules are hairlines in `line`. There are no shadows and no gradients.

**Colour has two jobs and they never mix.**
- `accent` (amber) is the annotator's pen on the board. It marks the hot zone, the recommendation, focus rings, row numbers and the eye path. It never appears inside the film frame and is never a nation.
- The `nation-*` hues identify collaborators: swatches, blooms, beams, band bars and chips. Each nation keeps its hue everywhere. They are spread around the wheel *and* across lightness, so pairs stay apart for colour-blind viewers. `nation-local` is the brightest colour in the system, because local AI is the protagonist and its tests should be the hottest flashes. `nation-human` is bone, the second brightest. Every hue is at least 5.9:1 on `canvas`. Still pair each hue with its label.
- The `surface-*` hues mark terrain (GitHub, linux, E:, C:, AM4, FX99). They are low chroma at mid lightness, used for swatches, coast labels and a 1px coast edge. Land tiles stay `land`. Terrain must never out-shout a nation.

**Text colours.** Use `fg` for content, `fg-2` for explanation and `muted` for labels. `muted` measures 4.1:1 on `bg`, which is under the 4.5:1 target for its small sizes. It is kept from the source and flagged; use `frame-muted` (5.6:1) where a label must be read.

**Type.** JetBrains Mono (`mono`) carries everything that is data or chrome: titles, labels, controls, the ticker and the counts. Source Sans 3 (`sans`) carries prose. Both load from Google Fonts at weights 400/500/700 and 400/600.

**Shape.** Corners are nearly square: `radius-sm` (4px) for buttons and `radius-md` (6px) for panels. Inside the frame, land is drawn as **hex tiles**; a test is a **bloom** (a disc at `bloom-halo` with a core at `bloom-core`, 45% of the radius); a launch is a **beam** (a quadratic arc at `beam` opacity); a new nation entering from the void is a set of **concentric rings**. Zones are outlined in dashed `frame-line` and turn solid `accent` when selected.

**Spacing.** On phones the page uses a `space-16` gutter and `space-20` top padding. From `bp-sm` it moves to a `space-20` gutter and `space-28` top. The bottom stays `space-64`. The page has and a max width of `page-max` (1240px). Sections sit `space-36` apart, and the board columns `space-18` apart.

## The frame: portrait first (360×640, exported 1080×1920)

| Zone | Where | Size (CSS px at 360 wide) | Motion |
| --- | --- | --- | --- |
| ticker | top, full width | `p-ticker-h` 64: date on line one, rate and totals on line two | none, only the text changes |
| nations | under the ticker | `p-strip-h` 44: a strip of swatch + test count chips; tap to open the full rows | counts tick; a chip fades in once |
| map | what remains, land centred | at least `p-map-min` 448 (70%) | per-frame |
| timeline | bottom, full width | `p-timeline-h` 84 (ruler 24 + band 60); tap the band to open the lanes to `p-timeline-open` 200 | a steady scroll, now at the right edge |

- Opening the lanes or the nation rows overlays the map. The camera never re-centres for chrome.
- The ticker date uses `kw-ticker` at 32px in portrait (44px in landscape). Counts in the strip use 13px mono.
- Transport overlays the ruler and the band, at `touch-target` height, and hides after three seconds.
- The export has no strip interaction, so it keeps the strip closed and the lanes folded. A portrait cut tells the story through the map, the ticker and the counts.

## The frame: landscape enhancement (1920×1080)

| Zone | Where | Size | Motion |
| --- | --- | --- | --- |
| ticker | top-left | 720 × `ticker-h` (64, or 84 with totals) | none, only the text changes |
| map | the safe area, land centred | what remains | per-frame |
| nations | right edge | `nations-w` 320, rows of `nation-row` 136 (96 from the eighth nation) | numbers tick, one fade-in |
| timeline | bottom, full width | `timeline-h` 200 = `ruler-h` 24 + `band-h` 60 + lanes (ten at `lane-h` 11) | a steady scroll, now at the right edge |

The band is mirrored in both orientations: chatter by class sits above its centre line and commits sit below it. The player switches to landscape when the viewport is at least `bp-lg` wide and wider than it is tall.

## Decisions (settled 2026-10-09)

These close the open questions from the wireframes board. Build to them, and raise a conflict with existing code as a question rather than an override.

| Decision | Settled |
| --- | --- |
| Where the lineage lanes live | The bottom timeline, horizontal, sharing one time axis with the ruler and band. Portrait folds them behind a tap. |
| Surfaces | Coast labels on the map plus the tally card. There is no left panel, and the left edge stays quiet. |
| World totals line | Line two of the ticker. |
| Lane labels | Real names in your own cut; stable hashes in a public cut. |
| Landscape timeline height | `timeline-h` 200: ruler 24, band 60, ten lanes at 11. |
| Nation rows (landscape) | `nation-row` 136 at seven nations or fewer; 96 with counters hidden from the eighth. |



There are no icons. Meaning comes from shape and colour: hex tiles, blooms, rings, beams, ticks on the ruler and a ring with the label `HQ`. Transport glyphs are plain text (`-- - ▶ + ++   1×`). If an icon seems necessary, use a word in `kw-label` instead.

## Components

`SegmentedControl`, `Panel`, `DataTable`, `ZoneLegend`, `NationStrip` and `NationRow` are CSS components in `components/bundle.css` (class prefix `kw-`). They need no script. All of them are mobile-first: base rules are the phone layout, `@media (min-width: 640px | 900px)` widens it, and `@media (pointer: fine)` compacts controls. Page layout uses `.kw-page` and `.kw-board`. No component may cause horizontal page scroll; long control groups scroll inside themselves.

## Reference

The **Reference** asset group holds renders of the work in progress. `wip-2026-04-27.png` is the current layout that the proposal reworks.
