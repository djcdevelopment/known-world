# LAP-07 cut and coda: result (2026-10-09, builder Sonnet 5.5, work item w-26069fe96149)

Code: `render/card.js`, coda handling in `compile/{camera,synth}.py` and `render/fields.js` (`codaK`), `export/{lapkit.py,rehash.mjs}`; runner `lap.py`
(build stills cut full). Receipts: `receipt-build.json`, `receipt-stills.json`, `receipt-export-cut.json`, `receipt-export-full.json`;
`ct receipt` `receipt://5e25079796e051efe6f68fb4` (cut export stage). Videos stay in `out/` (git-ignored): full 73.5 MB, cut 14.9 MB.

## Intro, coda, cut

- **Intro** 2 s (1 s in the cut): the empty map under the ticker; the sync probe white frame at frame 15.
- **Coda** 18 s (6 s in the cut), as fractions 3 : 4 : 2 : 8 : 1 of the coda: blooms, activity, hum and static decay (3); the camera pulls to the whole laid-out world
  (4); silence (2); the tally card (8, fade in over the first second); black (1). Card: one row per nation in entry order (first test, tests, yield, single / MIRV / unified,
  tiles the nation touched against 6,224 laid out) and two footer lines: "no chat source covers 2026-04" and "no Claude Code transcript before 2026-05-08 survives: Claude is
  known from commit trailers only, 2026-01 to 2026-04" (the task text said 05-09; the first Claude message in the corpus is 2026-05-08T13:31Z, and the 2026-04 hole is confirmed:
  chat counts per month are 2026-03 ChatGPT only, 2026-04 none, 2026-05 Claude only).
- **90 s cut**: m = 8.052, envelopes scaled by m^-1/2 (0.352), 2,700 frames, ticker `1 day = 0.30 s x8.05`, audio re-synthesised; 951 launches in 83 s.

## Measures

| | Full piece | 90 s cut |
|---|---|---|
| Frames / duration | 20,650 / 688.33 s | 2,700 / 90.000 s |
| Peak launches per film second (30-frame window) | 19 (STRATEGY expected 12) | 43 (expected about 37) |
| Collapsed frames | 295 (1.4 percent) | 1,533 (56.8 percent) |
| Audio tones / MIRV pips / bells / roll bins | 879 / 517 / 269 / 2 | 183 / 102 / 269 / 111 |

## Receipts

| Check | Result |
|---|---|
| Compile twice (separate processes), full and cut | kw-data.js and audio byte-identical, both |
| 30 frames re-rendered in a fresh Chromium, reverse order, against the export's own hashes | **30 of 30 equal**, full and cut |
| Sync probe, full piece | white frame 15 only, **delta 0.0 ms**, container 688.33 s, 20,650 frames, audio 33,040,384 samples (+384 AAC tail) |
| Sync probe, cut | white frame 15 only, **delta 0.0 ms**, 90.000 s, 2,700 frames, audio 4,320,256 (+256) |
| Page errors | none, both |
| Frame hash sha256 (Chromium 1248, DejaVu Sans Mono fallback) | full `129c364e2044...`, cut `d5ae7f301680...` |
| Corpus | `corpus/merged`, events sha256 `4e1e1c97...`, all eight input hashes in `receipt-build.json` |

## Timing: the full export, measured

| Export | Wall, frames | Wall, with concat, AAC mux, probe, re-hash | Effective per frame |
|---|---|---|---|
| **Full piece, 20,650 frames, 1080p, audio** (10 workers, nice, bench27 running) | **196.2 s** | **242.4 s (4.0 min)** | 9.48 ms |
| 90 s cut, 2,700 frames | 20.0 s | 26.2 s | 7.32 ms |

Slice 3's thin slice was 138.5 s / 184.5 s at 6.7 ms per frame; the real page now draws land paths, activity fills, beams, a band and panels, so it costs 1.4 x
more. Estimate in STRATEGY: about 9 minutes; measured 4.0.

## Stills (`stills/`)

`intro.png`, `coda-decay.png`, `coda-pull.png`, `coda-whole-world.png`, `coda-card.png`, `coda-black.png`.

## Deviations

- Footer date 2026-05-08 (data) against the task's 05-09.
- Card rows read zeros for local and OpenCode (they test never); their legend rows show participations instead (offload calls, sessions).
- The ct-wrapped re-run of the cut stage resumed all segments and rewrote `receipt-export-cut.json` with a 0.37 s wall; the first run's timing is kept inside it.
