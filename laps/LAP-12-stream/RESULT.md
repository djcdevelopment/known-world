# LAP-12 the stream: result (2026-10-09, builder Sonnet 5.5, work item w-26069fe96149)

Code: `compile/stream.py` (new), `compile/{build,camera,corpus,series}.py`, `compile/params.json`, `render/stream.js` (new), `render/{data,main,border,panels,fields,card,index}.*`,
`export/{perf,edgecheck}.mjs` (new), runner `lap.py` (build stills arms perf cut full). Receipts: `receipt-{build,stills,arms,perf,export-cut,export-full}.json`;
`ct receipt` `receipt://d18412d45b0cb71c52ec99dd` (cut export) and `receipt://867c08812935165d698221b0` (full export).
Videos (git-ignored): `out/full/final.mp4` 106.8 MB, `out/cut/final.mp4` 24.5 MB.

## Corpus (new merge, pinned in `receipt-build.json`)

events.ndjson sha256 `cc5ca71fea32...` (216,796 events), repos.json `62da206a3d10...`, relations.json `8875b6ce4a1a...`, all eight input hashes in the receipt. 9,789 counted commits
(LAP-11: 9,787), 111 own lineages with commits (120 own git lineages; 132 git lineages in all with the third-party clones).

## Layout (after the second-viewing direction: HUD plates)

- **The map owns the full 1920 x 1080 frame** (`hud: plates`, `hud_alpha` 0.6). Ticker, surface tallies, nation panel, stream and radio band are plates at 60 percent opacity with a 1 px border; map layers are no longer clipped.
  `hud: columns` is the arm (opaque plates, map clipped to the safe area): compiles and renders (`stills/columns-arm-2026-09-27.png`).
- **Safe area** = frame minus insets (left 240, top 64, right 320 + stream 260, bottom 120) = **x 240, y 64, 1100 x 896** (was 1360 x 896 in LAP-11). The camera fits into it. Frame size and insets are params
  (`frame_w/h`, `hud_*`) written to `D.layout`; the page lays every plate out from them (nothing in the layout maths names 1920 or 1080 except the params), so a portrait frame needs params and arrangement only.
- **Stream plate** 260 px at x 1340, y 64 to 960: 20 px count row, 104 px pinned header of lane names, plot 772 px for `stream_window_s` 20 film seconds (38.6 px per second), era ticks and a faint ruler on the left edge (56 px; 1,007 ticks: year / month / day major, quarter / half-month / 6-hour minor, era boundaries bright), newest at the bottom.
- **Camera, start tight:** `camera_start_fill` 0.6, `max_hex_px` 40 to 110, pull back only from frame 0. Scale (px per hex): 98.0 at frame 0 (first region), 42.4 at 302, 25.3 at 394, 4.65 at 543 (first far continent), 2.4 at 900 (30 s), 2.2 through era C, 1.78 at the end.
  Fill rises from 0.6 to `camera_end_fill` 0.8 as the world grows. The coda never zooms in (clamped to the last run scale).
- **Slide-in clip (coordinator note):** nation rows now start 240 px (was 320) inside a clip that stops 8 px short of the panel edge, fading in (alpha = ease); the left tallies likewise (200 px, clip 8 px short). Check `export/edgecheck.mjs`
  at 10 frames around 2026-09-27 (OpenCode enters): pixels differing from a plain plate-over-map blend in the outer 8 px of the nation panel and the tallies: **0 of 0 in every frame** (`receipt-stills.json` `edge_check`).

## The stream

| | Full piece | 90 s cut |
|---|---|---|
| Lineages that ever appear (of 111 with commits) | 109 | 58 |
| Max concurrent / mean visible (story frames) | 14 / 10.4 | 14 / 11.1 |
| Frames at the 14-lane cap | 12,579 of 18,352 with lanes | 1,987 of 2,575 |
| Max "+N quiet" | 37 | 49 |
| Lane swaps by activity (hysteresis: x1.25, 3 s dwell) | 144 | 70 |
| Rails (branch 317 + worktree 224); rejoined at a unified launch | 541; 75 | same |
| MIRV connectors (warheads over >= 2 visible lanes; max 10 lanes touched) | 144 | 144 |
| Cross-constellation association connectors drawn / edges with both ends as lanes | 4 / 4 (3 consumes, 1 contract) | 1 / 4 |
| Lineages on two surfaces (paired rails at the bridge frame) | 20 | 20 |
| Slot overflow (fading lanes beyond the 18 slots) | 0 | 0 |

Lane order: 13 constellation groups then 32 loose lineages, by first_ts. Commits: 9,789 ticks, dot area by log(lines, capped at 20,000).

## Receipts

| Check | Result |
|---|---|
| Compile twice (separate processes), full and cut | kw-data.js and audio byte-identical, both (full kw-data `cf1332ae...`, cut `5028e157...`) |
| 30 frames re-rendered in a fresh Chromium, reverse order, against the export's own hashes | **30 of 30 equal**, full and cut |
| Sync probe | white frame 15 only, **delta 0.0 ms**, both; page errors none |
| Frame hashes sha256 | full `5808fa23...`, cut `996f08f1...` |
| `stream_labels: hashed` arm | compiles; 0 lane names present in its kw-data.js |
| Totals arms (rolling_10s, launch_window) | compile |

## Timing (10 workers, nice, bench27 running)

| | Frames wall | With concat, mux, probe, re-hash | Per frame |
|---|---|---|---|
| Full, 20,650 frames | 215.9 s | **262.5 s (4.4 min)** | 10.44 ms |
| Cut, 2,700 frames | 23.0 s | 29.3 s | 8.43 ms |

LAP-11 was 202.1 / 248.3 s (9.77 ms): +7 percent. Compile 20.9 s full, 4.9 s cut; kw-data.js 22.4 MB. Frame time in Chromium with a forced raster flush (`export/perf.mjs`, 40 blocks of 30 consecutive frames): total median 9.7 ms,
p95 38 ms; the stream layer adds **median 0.4 ms, p95 6.3 ms, max 11.8 ms** on the full piece (cut: 2.0 / 4.3 / 7.4, eight times denser). Noisy: bench27 shares the machine; a quiet run read 0.4 / 1.9 / 3.9.

## Totals decisions applied (Fable, slice 8's five questions; each a params key)

1. `third_party_clones_row: tally_card`: one muted row on the card: 23,451 commits, 4,643,214 lines (capped), 11,164 without line counts; nothing in the live panel.
2. `totals_line_cap: yield`: displayed lines use the 20,000 per commit cap (87 commits capped, proportional split of added and removed): world lines **7.9M** (was 18.4M); the card footer states the uncapped 18,450,334 once.
3. Bulk copies stay out (`bulk_copy_footer`): footer line, 680,125 births and 62,411 updates.
4. `rate_window: era_unit`. 5. `births_to_nation: off`.

## Deviations from DIRECTION

- **HQ and the risen islands join the camera fit only once the explored land spans 120 world units** (`camera_items_min_span`); before that the camera frames land alone. The first island (frame 68) sits 145 units north of the first tile, so with it in the box a tight start is impossible; consequence: the first 11 islands rise off screen and appear at the first pull-back (frames about 360 to 900).
- The tight start lasts about 2 s: the second land cluster arrives at 394 and the first far continent at 543, and the 6 s look-ahead begins the pull-back before it. The first revealed tile sits left of centre at 320 because the zero-phase smoother anticipates that jump.
- **Pinned name header added** (names rotated up each lane in a 104 px strip) besides the spec's name at the lane's entry point, because entry labels scroll out in 20 s and lanes live for minutes. 12 px monospace, ellipsis at 14 characters; lane pitch tiers 4 / 7 / 10 / 14 slots, 14 px at the cap.
- A lane leaves when dormant > 30 story days **and** no commit lies in the trailing window (film-time floor), otherwise era A lanes would flash for 0.3 s. Entry marks the earliest commit in the window.
- Association connectors use all cross-constellation edges (4 of 10 have both ends as commit lanes: the others touch lineages without commits or not git); `stream_assoc: contract` restricts to type contract (1).
- Surface pairing uses the host bridge frame (later region first seen), 20 lineages; commits ride the rail of their host.
- The nation panel's old `c / f` line is still there. The radio band stays 1360 px wide under the stream plate. The slide-in of rows is shorter and fades (clip note).
- Not built: the player, scrubber, marks, portrait layout (slice 10).

## For Derek to decide (counts only)

1. Fill: 0.6 at the start rising to 0.8 (`camera_end_fill`); the final world is 1.78 px per hex. 1 value to set.
2. Islands and HQ in the fit from the start (loses the tight start, 1 switch: `camera_items_min_span` 0) or from span 120 (default).
3. Association connectors: 4 edges (all cross-constellation) or 1 (contract only).
4. Pinned header on (default) or entry labels only.
5. `stream_labels` names (this export) or hashed for any public cut.
