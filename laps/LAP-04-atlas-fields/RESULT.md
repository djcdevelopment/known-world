# LAP-04 atlas and fields: result (2026-10-09, builder Sonnet 5.5, work item w-26069fe96149)

Code: `compile/{tiles,layout,series,camera,audit,build}.py` (tile table, world, tile-level fields, simple fit camera, audit),
`render/{data,state,palette,fields,launch,main}.js`, `export/lapkit.py`; runner `lap.py` (stages build audit verify stills).
Corpus: `corpus/merged` read directly; hashes pinned in `receipt-build.json` (events sha256 `4e1e1c97...`, identical to the earlier
`cache/corpus-pin-0653`). Counts only. Receipts: `receipt-build.json`, `receipt-verify.json`, `receipt-stills.json`,
`nongit-audit.json`; `ct receipt` `receipt://d91bcf8983bf5c31eb28b091` (verify stage, exit 0).

## Fable amendments applied (each a parameter)

`engagement_union: combined` (default), `generation_granularity: minor`, `nongit_min_files: 10`, `chip_max_visible: 4`,
`chip_named_s: 3`, unversioned trailers get no chip, legend rows with 0 tests show participations (offload calls for local, sessions
otherwise), `first_event_include_third_party: false` (Claude stays 2026-01-20), collapse 8 per second unchanged.

## Launch counts under combined (strip: `strip-compare.png`, combined above, time_window below)

| | combined (default) | session | time_window |
|---|---|---|---|
| Git launches | 640 | 938 | 390 |
| Non-git launches (min files 10) | 311 | 311 | 311 |
| All launches | 951 | 1,249 | 701 |
| single / MIRV / unified | 769 / 171 / 11 | 1,195 / 47 / 7 | 486 / 209 / 6 |
| Bands 1..6 (combined) | 71 / 268 / 363 / 205 / 35 / 9 | | |
| Nations (combined) | human 370, claude 453, codex 82, chatgpt 37 (inferred), automation 9 | | |

## Non-git audit (`nongit-audit.json`, directories labelled host#hash)

| nongit_min_files | launches | files | directories | by year |
|---|---|---|---|---|
| 3 | 572 | 144,025 | 158 | 2017 2, 2018 24, 2019 16, 2020 3, 2021 11, 2022 5, 2023 12, 2024 56, 2025 84, 2026 359 |
| **10** | **311** | 142,225 | 123 | 2018 7, 2019 6, 2020 1, 2021 1, 2022 1, 2023 9, 2024 17, 2025 30, 2026 239 |
| 20 | 232 | 140,761 | 103 | 2018 4, 2019 5, 2022 1, 2023 6, 2024 14, 2025 14, 2026 188 |

Nations at 10: human 255, ChatGPT time-inferred 37, Claude 11, Codex 8; first non-git test 2018-07-07 (at 3: 2017-05-01). The git gate
(a directory that later gains a git lineage counts as non-git only before its first commit) covers 2 directories and removed 2 active
days (574 earlier, 572 now at 3). Per-directory-by-year rows (148 at the default) are in the JSON; the busiest directory holds 43,920
files in 2 launches; files are dominated by few directories, launches by many small ones.

## World (`world.json`, counts)

320 regions (130 git, 177 dir, 13 ruins) as lineage x surface; 6,224 tiles (2,925 git, 2,283 dir, 1,016 ruin) and **16,117 cells**
(STRATEGY planned about 7,500: the spine's 2,923 git tiles are 7,865 cells; non-git directories and ruins double it). 13
constellation discs hold 83 joined lineages (primary at the centre, edge-pulled neighbours), loose lineages by first touch; omen-e
and omen-c with a 3-hex strait, omen-linux nested to the south across 8 hexes, AM4 and FX99 off its west coast, 54 GitHub islands (4
rows, rise at `created_at`), 46 harbours, 29 bridges (host-spanning and relations), 224 spurs (worktrees), 316 notches (branches).
284 tiles are laid out and never touched (void forever). 20 clone events reveal 41 tiles already explored elsewhere; ruins appear
whole at clone time (1 by an event, 12 by the last upstream commit date, a proxy). HQ: omen-e from 2026-05, omen-c, back to omen-e,
crosses to omen-linux on **2026-09-28** (frame 19,276; STRATEGY expected 09-27: the 7-day window with 20 percent hysteresis).

## Receipts

| Check | Result |
|---|---|
| Compile twice (separate processes) | kw-data.js and audio byte-identical |
| Checkpoints | every 900 frames, 23; 147,061 touches folded into 26,272 deltas |
| `buildState` under Node 24 vs Python brute force over all touches, frames 7,721 / 14,273 / 19,457 | max relative error 3.6e-8, 4.1e-8, 3.8e-8 |
| Order independence, 30 frames in two Chromiums, shuffled | 30 of 30 equal |
| Luminance, fields only (6 busy cut frames) | max OKLab L 0.548 (limit 0.55); a first run read 0.91 from light bridge, spur and harbour strokes, now capped |
| Compile time, full | 18 s |

## Stills (`stills/`)

`2026-03-15.png`, `2026-07-05.png`, `2026-09-28.png`, `final.png` (7 s into the coda: the camera has pulled back to the whole world),
`final-tile_area_k1.png` (same frame with `tile_area_k` 1: 9,830 cells).

**Legibility, my reading.** The final pull-back fits at about 2.1 px per world unit: a hex is about 4 px across, tiles are 4 to 10 px blobs, the
continents read as three distinct masses with the fog texture of tiles, ruins hatched, islands in the north; individual tiles do not read at
1080p, regions of a constellation do (hexagonal blobs, spiral rings inside). The k = 1 alternative is only marginally larger, since sea and
the 12 percent pad set the scale. 4K (`scale: 2`) or a lap on `tile_area_k` / ruins are the levers. Verdict field for Derek: ______

## Deviations from STRATEGY (reason)

- Terrain tint L 0.225 to 0.265 (STRATEGY: 4 to 6 points above the background, about 0.19): at 4 px hexes the specified tint was invisible
  in the still. Parameters `terrain_L`, `terrain_C`.
- Ruins are kept out of the camera box (`camera_ruins_in_box: false`): they sit on the outer ring and would hold the camera wide for 6 years.
- Camera here is the simple fit with the smoother; slice 6 refines it (lookahead and clamps are already in; stills show it).
- GitHub islands are a compact cluster (4 rows) in the north sea, not a band across the world: a full-width band forced the camera wide in era A.
- Compile tables for slices 5 to 7 (beams, rings, sparks, band, card) were built in the same pass; their render layers follow in their slices.
- Chips for nations that never test (local, OpenCode) enter at first participation (STRATEGY: first test).
