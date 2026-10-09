# LAP-14 information architecture: result (2026-10-09, builder Sonnet 5.5, work item w-26069fe96149)

Binding design: DIRECTION.md "Information architecture" (rev 5) and the Known World design system at `design/known-world-design-system/` (tokens.json, README.md, component READMEs, bundle.css). Default `layout: ia`; `layout: v4` (the slice-10 layout) compiles and renders unchanged: 30 of 30 frames equal the slice-10 renderer (`receipt-compat.json`).
Code: `compile/{camera,stream,build,build_cli}.py`, `compile/params.json`, `render/{system,ia,data,palette,border,panels,card,fields,main,player,stream}.js`, `render/index.html`, `export/{frames,rehash,still,motion,landbox,chrome}.mjs`, `export/lapkit.py`, runner `laps/LAP-14-ia/lap.py` (build stills centre motion compat cut full cutp fullp).
Receipts (`ct receipt`): build `receipt://492da3c7135d712b98d4d3c8`, landscape full `receipt://dd2bfca48091f51f9ae09a99`, portrait cut `receipt://fb3b8efc664fd18cca4c1ffb`, portrait full `receipt://558c40a676fe44645fb37cd6`. Corpus pinned in `receipt-build.json` (events.ndjson `b1ee0cf8fbb0...`).

## Videos (git-ignored)
| Piece | Path | Size | Export wall (frames / total) | Rehash 30 frames, reverse order | Probe |
|---|---|---|---|---|---|
| landscape full 1920x1080, 11:28.5 | `/home/derek/work/known-world/laps/LAP-14-ia/out/full/final.mp4` | 79.0 MB | 200.2 s / 246.3 s (4.1 min) | 30 of 30 | delta 0.0 ms |
| landscape cut 90 s | `.../out/cut/final.mp4` | 17.8 MB | 20.6 s / 26.8 s | 30 of 30 | delta 0.0 ms |
| portrait cut 90 s 1080x1920 (360x640 css at 3x, strip closed, lanes folded) | `.../out/cut-portrait/final.mp4` | 34.8 MB | 29.6 s / 35.9 s | 30 of 30 | delta 0.0 ms |
| portrait full 1080x1920 | `.../out/full-portrait/final.mp4` | 133.3 MB | 280.7 s / 326.8 s (5.4 min, under the 10 min limit) | 30 of 30 | delta 0.0 ms |
Compile twice (separate processes, full and cut): kw-data.js and audio byte-identical. Page errors none. Compile 67.9 s full, 4.8 s cut. Player URL: serve with `.venv/bin/python -I export/serve.py 8765`, then `http://127.0.0.1:8765/render/index.html?data=../laps/LAP-14-ia/build-full/kw-data.js` (add `&audio=none` to skip the WAV).
Stills (`stills/`): `2019-05 2023-11 2026-01-20 2026-03-05 2026-07-05 2026-09-27 2026-10-03`, `tally-card`, `portrait-390x844-*`, `portrait-1080x1920-*` (2023-11 and 2026-09-27), `portrait-390x844-tally-card`, `portrait-390x844-lanes-open-2026-09-27`, `surfaces-toggle-2026-09-27`, chrome checks `chrome-{visible,hidden,surfaces}-*`, and the 2026-04-27 pair per export: `landscape-full-`, `landscape-cut-`, `portrait-full-`, `portrait-cut-2026-04-27.png` (portrait ones are 1080x1920).

## Zone map (pixel rects; landscape 1920x1080)
| Zone | Rect (x, y, w, h) | Content and gating |
|---|---|---|
| ticker | 0, 0, 720, 84 | date 44 px, rate glyph, totals line beneath (line two) once commits exist; no plate, no hairline |
| map = safe area | 0, 84, 1600, 796 | the only per-frame motion; sea fill; coast labels and coast edges; land centred |
| nations | 1600, 0, 320, 880 (plate hugs its rows) | one row per nation from its first signal, 120 px each, 1 s fade-in, no slide, zero figures not drawn; absent until a nation has signal |
| timeline | 0, 880, 1920, 200 | one shared axis: x 108 to 1908 = 600 frames (20 s) at 3 px per frame, now at x 1908; names x 0 to 108 |
| ruler | 0, 880, 1920, 24 | always: date ticks, hashmarks with labels (left of the tick, thinned) |
| band | 0, 904, 1920, 60 | from the first chatter or commit (frame 826): chatter above the centre line by class, commits below, offload ember |
| lanes | 0, 967, 1920, 110 (ten at 11) | from the first lane (frame 826): fixed slots, names 10 px at the left end, commit ticks, rails, vertical MIRV connectors |
Portrait (360x640 css, exported at 3x): ticker 0,0,360,64 (date 32 px; rate and totals line two); strip 0,64,360,44 (chips, appears with the first nation); map 0,108,360,448 (448 = the system's minimum); timeline closed 0,556,360,84 (ruler 24 + band 60), open 0,440,360,200 (lanes behind a tap on the band or the `lanes` button; overlays the map, camera does not move). The export keeps the strip closed and the lanes folded.
Era A (2011 to frame 68): ticker, one centred spot, the ruler. The left edge is empty. Surfaces: coast labels (surface hue, 12 px) from a surface's first tile, a 1 px coast edge in its hue, the tally card block, and the player toggle `s` (a transient overlay, not a panel).

## Centred land
Camera box = warm weighty land + launch targets, islands, HQ, beacons and ruins only after their existing thresholds; the camera centre is the box centre through a finite (+-1.5 s) window, scale still looks ahead 6 s. Offsets of the known land's box from the safe-area centre (800, 482), full piece:
| Date | frame | box px | offset px (x, y) |
|---|---|---|---|
| 2019-05-15 | 994 | 155 x 178 | **0.0, 0.0** |
| 2023-11-15 | 2021 | 174 x 772 | 1.7, 4.7 (inside the 1 s window after the 2023-11-03 far launch joined the box) |
| 2026-01-20 | 3982 | 137 x 335 | 2.8, 1.2 |
| 2026-03-05 | 4409 | 349 x 339 | **0.0, 0.0** |
Over all story frames the box centre is within 2 px of the safe-area centre in 94.9 percent, within 10 px in 97.8 percent, within 50 px in 99.1 percent (the rest are the ease after a box change; max 832 px at one step). Two of four dates are within 2 px, the other two within 5 px; a smaller window would pull the second pair inside 2 px at the cost of a faster pan (arm: `camera_centre_halfwidth_s`).
Pixel check (`receipt-centre.json`, the land layer alone): 2019-05 land bbox centre offset 0, 0.5 px. The drawn continents at the other three dates sit lower than the box centre (80, 183 / 98, 130 / 6.5, 127 px) because the box contains the GitHub islands and a launch target once the span passes `camera_items_min_span` 120 (the existing threshold): see question 5.

## Motion budget
10 random seconds (seed 14: seconds 76 111 254 263 279 300 312 462 541 632), every consecutive frame pair, changed pixels outside the map rect and the timeline rect: **worst 0.26 percent** (per-second maxima 0.02 to 0.26 percent; none over 0.5). Two nation-entry seconds (Claude 3975, OpenCode 19232; the allowed fade-in): max 1.89 and 0.98 percent, all inside the 1 s fade. Ticker hairline, era-switch brightening, row slide, swatch flash and plate-opacity effects are removed under ia. `receipt-motion.json`, `receipt-motion-entries.json`.

## Player chrome
Transport and scrubber overlay the ruler (landscape 24 px; portrait ruler + band), visible at load, hidden after 3 s without input (opacity 0, 0.3 s transition), back on pointer movement (`receipt-chrome.json`, 1920x1080 and 390x844); key `s` toggles the surface tallies; absent under `?export=1` (0 elements, player not loaded). Portrait: tap the band or the `lanes` button opens the lanes; tap the strip opens the nation rows; tap the ticker opens the surfaces.

## Lane statistics (horizontal form; `receipt-build.json`)
| | Full | 90 s cut |
|---|---|---|
| Lanes total / ever visible | 111 / 107 | 111 / 43 |
| Slots; max concurrent | 10; 10 | 10; 10 |
| Frames with lanes / at the cap of 10 | 18,358 / 15,092 | 2,575 / 2,061 |
| Mean visible (frames with lanes) | 8.69 | 8.57 |
| Slot moves while a lane is visible | **0** | 0 |
| Swaps by activity (x1.25, 3 s dwell) | 176 | 47 |
| Max "+N quiet" | 41 | 53 |
| Rails (branch + worktree) / rejoined at a unified launch | 541 / 75 | same |
| MIRV connectors / max lanes touched | 144 / 10 | same |
| Cross-constellation connectors drawn / edges | 3 / 4 | 1 / 4 |
| Lineages on two surfaces (paired rails) | 20 | 20 |
| Constellation order: mean inversions per frame; same-constellation lanes adjacent | 18.5; 50.4 percent | 17.3; 59.6 percent |
Fixed slots win over order: at the cap a leaving lane frees exactly one slot, so an entering lane has no choice. Order degrades to near entry order (question 4).

## Design system comparison (source: design/known-world-design-system/)
Values are adopted only under `layout: ia` (`design_system: on`); `layout: v4` keeps its colours. All adopted values live in one module, `render/system.js` (`window.KW_SYS`); amber `accent` is deliberately not in it.

### Colour
| token | system value | code value before | match | what I did |
|---|---|---|---|---|
| nation-human | #e3d3b4 | OKLCH h 85, C 0.045 (swatch #938467) | mismatch | hue and chroma read back from the hex (h 84, C 0.045); swatches, chips, bars, band, ticks and connectors use the exact hex; field and launch shades keep the film lightness |
| nation-chatgpt | #26bf7c | OKLCH h 155, C 0.160 (swatch #00a159) | mismatch | hue and chroma read back from the hex (h 158, C 0.157); swatches, chips, bars, band, ticks and connectors use the exact hex; field and launch shades keep the film lightness |
| nation-claude | #ff7a59 | OKLCH h 35, C 0.170 (swatch #d95737) | mismatch | hue and chroma read back from the hex (h 35, C 0.170); swatches, chips, bars, band, ticks and connectors use the exact hex; field and launch shades keep the film lightness |
| nation-codex | #3b8cf5 | OKLCH h 205, C 0.130 (swatch #009bab) | mismatch | hue and chroma read back from the hex (h 256, C 0.176); swatches, chips, bars, band, ticks and connectors use the exact hex; field and launch shades keep the film lightness |
| nation-automation | #e062c4 | OKLCH h 80, C 0.160 (swatch #b77800) | mismatch | hue and chroma read back from the hex (h 337, C 0.193); swatches, chips, bars, band, ticks and connectors use the exact hex; field and launch shades keep the film lightness |
| nation-local | #e2ef6a | OKLCH h 27, C 0.200 (swatch #e6443d) | mismatch | hue and chroma read back from the hex (h 114, C 0.157); swatches, chips, bars, band, ticks and connectors use the exact hex; field and launch shades keep the film lightness |
| nation-opencode | #c4b0ff | OKLCH h 300, C 0.180 (swatch #9867e1) | mismatch | hue and chroma read back from the hex (h 295, C 0.112); swatches, chips, bars, band, ticks and connectors use the exact hex; field and launch shades keep the film lightness |
| surface-github | #6f9585 | swatch OKLCH hue 190 | mismatch | swatches (tally toggle, card block), coast label and coast edge use the hex |
| surface-linux | #86915a | tint hue 165 | mismatch | same |
| surface-e | #5f7fb5 | tint hue 255 | mismatch | same |
| surface-c | #8d96a6 | tint hue 275 | mismatch | same |
| surface-am4 | #a5809e | tint hue 310 | mismatch | same |
| surface-fx99 | #a8876a | tint hue 60 | mismatch | same; land tiles keep their tint (question 2) |
| canvas | #07090e | #07090e | match | kept; plates are canvas under ia |
| sea | #0c111b | none (canvas under a dot lattice) | mismatch | the map's safe area is filled with sea |
| frame-line | #2b3650 | plate rule rgba(74,86,112,.55) and #1b2230 | mismatch | plate rules use frame-line (solid 1 px, not dashed) |
| frame-muted | #7d8aa3 | #8b93a6 | mismatch | adopted for labels and muted text |
| fg | #e8edf6 | #e8e0c0 (cream) | mismatch | adopted for text, ruler ticks, chrome |
| fg-2 | #9aa7bb | #c9c3a8 | mismatch | adopted |
| muted | #66748c | #5f6779 / #6a7388 | mismatch | adopted for the few dim notes |
| dim | #2a3346 | #2a3346 (band centre line #222b3b, lane rails rgba muted .28) | match for the token; rails differ | token matches; rails kept translucent (a). Recommend dim for rails |
| land / land-dim | #3b4a66 / #1f2838 | terrain tints per surface and fog state from `terrain_L/C` | mismatch | not changed (question 2) |
| accent | #ffb347 | not used | match | never in the frame; note the migration mark (240,160,96) is amber-like (question 6) |
### Type
| token | system | code before | match | what I did |
|---|---|---|---|---|
| kw-ticker | JetBrains Mono 44 landscape | 30 | mismatch | 44 (date); rate glyph 20 |
| kw-ticker-p | 32 portrait | 24 | mismatch | 32 |
| kw-count | 30 landscape / 28 phone | 28 | mismatch | 30 in the landscape rows; 28 in portrait expanded rows |
| kw-label | 11 px uppercase, 1 px tracking | 12 px lowercase | mismatch | nation-row labels (commits, files, lines, commits/wk) only; card and tally headers keep 16 px (question 7) |
| chips | 12 px | 12 px | match | kept |
| lane names | no token | 12 px stacked in a 14 px lane | n/a | 10 px (landscape and portrait) because the lane is 11 px (brief said 11 px names) |
### Layout
| token | system | code before | match | what I did |
|---|---|---|---|---|
| ticker-h | 64, 84 with totals | 64 plate | mismatch | 84 fixed (the camera safe area is compiled, so the strip cannot change height at the first commit); portrait 64 |
| nations-w | 320 | 320 | match | kept |
| nation-row | 136 (<=7 nations), 96 from the eighth | 136 in v4 | mismatch | 120; 7 x 136 = 952 > the 880 px panel (question 1). Dense 96 not built: the corpus has 7 nations |
| timeline-h / ruler / band / lane | 200 / 24 / 60 / 11 | 208 / 24 / 56 / 12 | mismatch | 200 / 24 / 60 / 11 |
| p-ticker / p-strip | 64 / 44 | 56 / 30 | mismatch | 64 / 44 |
| p-timeline closed / open | 84 / 200 | 176 | mismatch | 84 closed, 200 open |
| p-map-min | 448 of 640 | n/a (450 px wide frame) | mismatch | 448 exactly at 360x640 |
| portrait frame | 360x640 css at 3x = 1080x1920 | 450 logical px wide | mismatch | 360 logical, exported at 3x (clip scale 3); the 450 layout is gone |
### Opacity
| token | system | code | match | what I did |
|---|---|---|---|---|
| bloom-halo / bloom-core | 0.18 disc / 0.6 core at 45 percent radius | radial gradient, peak 1.0, 0.7 at 35 percent, lighter compositing, squared decay | mismatch | not changed (question 3) |
| beam | 0.5 (launch beams and lane rails) | comms beams 0.5 (match); launch beams 0.75 and 0.8; lane rails 0.55 | partial | comms beams match; others kept (question 3) |
### Luminance budget (the one place the film dims a field tint)
At the field cap (L 0.55) relative luminance, system hue against the film's old hue, gamut-fitted: human 1.00, ChatGPT 1.00, Claude 1.00, Codex 0.93, automation 0.89, OpenCode 1.06, **local 1.18**. nation-human #e3d3b4 does not exceed the cap. nation-local exceeds it by 18 percent (yellow-green is luminous at the same OKLCH lightness), so under ia its field tint (L at or below 0.55) is dimmed by a lightness factor found at load so its relative luminance equals the old hue's; its launches (L above the cap) keep the system hue untouched. No other nation is dimmed.

## Lists
**(a) Values adopted:** all nation-* hues (swatches, chips, bars, band, ticks, connectors exact; field and launch shades by hue and chroma with the film's lightness); surface-* in swatches, coast labels, coast edge and the card block; fg, fg-2, frame-muted, muted, frame-line, canvas, sea; ticker 44/32, count 30/28, kw-label for nation-row labels, chips 12; timeline 200 = 24 + 60 + ten lanes at 11; ruler, nations-w, ticker 720 wide; portrait 360x640 at 3x with ticker 64, strip 44, timeline 84 closed and 200 open, map 448; totals as line two; coast labels, tally card surfaces block, no left panel; lanes at the bottom on one axis; real lane names by default and `build_cli.py --public` (stream_labels hashed: 0 lane names found in a public cut's kw-data.js); strip closed and lanes folded in the export; both orientations exported.
**(b) Values kept from the old code, with the reason:** terrain tint on land tiles (carries fog states: question 2); bloom and launch-beam alphas (detonation physics under lighter compositing, luminance cap: question 3); lane rails 0.55 and band centre line (translucent over lighter-composited ticks); ticker strip 84 constant (compiled camera safe area); nation row 120 (question 1); lane names 10 px; card and tally headers 16 px; mark colours (marks have no token); the film's field lightness cap L 0.55; nation-local field tint dimmed (luminance budget, above).
**(c) Structural conflicts, unresolved (questions, counts only: 7):**
1. Nation rows: system 136 px (96 from the eighth) against the real panel height 880 px: seven rows at 136 need 952. Values 136 vs 120 (built). Recommendation: keep 120, or let the panel start at y 0 with 112.
2. Land: system says land tiles stay `land` (#3b4a66) and surfaces only mark coasts; the film tints land per surface and by fog state. Values: land vs `terrain_L/C` tints. Recommendation: keep the tint for now, as fog needs more than two lightnesses.
3. Bloom and beam: system discs at 0.18 / 0.6 against the film's gradient blooms (peak 1.0, lighter) and launch beams 0.75 to 0.8. Recommendation: keep; the 0.18 disc would remove the hottest flash the system asks for in nation-local.
4. Lane order: fixed slots at the cap leave no room for constellation order (50 percent of same-constellation lanes adjacent). Options: allow one re-sort at a lane swap (a slide) or accept. Recommendation: accept.
5. Known land and islands: the box includes the GitHub islands once the span reaches 120, so drawn continents sit about 127 to 183 px below the safe-area centre at 3 of 4 dates. Values: `camera_items_min_span` 120 vs never. Recommendation: islands never join (continents centred, islands may clip at the top).
6. Mark colours: no tokens; migration (240,160,96) reads as accent amber, which must not appear in the frame. Recommendation: use fg-2 for migration.
7. The commit series below the band line is one aggregate; the system says commits sit in nation-human. Values: warm grey rgba(150,135,112,.8) vs #e3d3b4. Recommendation: keep grey until the compile splits commits per nation. Also the kw-label style on card and tally headers (16 px lowercase vs 11 px uppercase): recommendation: keep on the card.
Also open (count 1): the `s` toggle shows a left overlay of surface tallies although the system says no left panel; recommendation: keep as a transient overlay.

## Deviations from rev 5, with reasons
- Hairline in the ticker and the era-switch brightening removed (motion budget). Lane entry and exit are instant (no fade).
- The ruler scrolls with the band (one axis) and the scrubber overlays it; marks carry their labels left of the tick, thinned when dense.
- Nation row 120 px, ticker strip 84 px, lane names 10 px (above).
- Constellation order is best effort (above). Compile-only arm for islands not run (question 5).
