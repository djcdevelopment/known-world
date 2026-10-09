# Strategy: engineer (pipeline first), direction rev 2

Strategist: engineer angle, Workflow 2, 2026-10-09. Inputs: DIRECTION.md (payload model, Shape, Two evolutions),
CONTRACT.md §1/3/7/8 (v1.4), CORPUS-REPORT.md, SURVEY.md §4/4b, spike 01, RaidUI vendor copies. Figures marked
**[measured]** were taken in this session with a prototype of `compile/launches.py` and a capture harness on the
spike page; scripts live in the session scratchpad and printed counts only, no corpus line.

## 0. The one idea

One integer clock and two physics. Output frame `f` (30 fps) is the only time axis. Compile (Python 3.14 + numpy)
makes every judgement: launches, yield, shape, nation, infrastructure fields, camera. The page's `render(f)` is a
pure lookup-and-draw. Audio is synthesised from the same frame tables at 1,600 samples per frame (48,000 / 30, an
exact integer). Only compile reads parameters, so a lap is one key, a recompile in seconds and an export in minutes.

## 1. Densities this design is sized for

Default parameters, 13:00Z snapshot; the piece is 668.2 s = **20,047 frames** (A 46.7 s, B 87.5 s, C 534.1 s).

| Layer | Measure **[measured]** | Value |
|---|---|---|
| Git launches | episodes (2 h gap) / above min yield / launches after engagement grouping | 935 / 827 / **816** |
| | shape: single / MIRV / unified | 746 / 54 / 16 |
| | MIRV warheads: 2 / 3 / 5 / 7 / 8+ | 22 / 19 / 4 / 1 / 8 |
| | yield band (floor log10 lines) 1 / 2 / 3 / 4 / 5 / 6 | 52 / 289 / 341 / 109 / 21 / 4 |
| | per month 2026-03 to 2026-10 | 55, 57, 90, 67, 157, 167, 169, 40 |
| | **peak per film-second** / max in a sliding 1 s / seconds at 8 or more | **11** / 12 / 8 |
| | max starting in one frame / max blooms alive at once | 8 / 15 |
| | gap 1 h: 1,132 launches, peak 17/s; gap 4 h: 636, peak 11/s | |
| Non-git launches (v1.4) | from births alone (no `file_update` in the merged corpus yet) | 133, first 2020-12; one a year 2024-08 to 2025-10, then 8, 6, 16, 18, 16, 29, 25 from 2026-03 |
| Infrastructure | August 2026 mean per film-second: commits / folded chat messages | 35 / 710 |
| | peak per film-second: commits (2026-03 import) / chat messages / offload calls (2026-10-03) | 785 / 14,748 / 13,876 |
| | tiles (lineage, depth-2 path), non-third-party | 2,923 |
| | known tiles touched in one frame (known > 200): p50 / p99 / max | 0.19 % / 2.3 % / 8.8 % |
| Nations | first conducted git test: human / Claude / Codex / automation | 2023-11-03 / 2026-01-20 / 2026-07-02 / 2026-07-03 |
| | first participation, local seats (offload inside a launch window) | 2026-07-18 (153 launches) |
| | first event, radio only: ChatGPT / OpenCode | 2023-04-17 / 2026-09-27 |
| | Claude generations, first test | Opus 4 01-20, Sonnet 4 01-21, Haiku 4 06-05, Fable 5 06-10, Sonnet 5 07-04, Opus 5 07-29 |

Design peak: **12 launches per second** (collapse active in about 8 seconds) and **15,000 infrastructure events per
second**, folded to at most one delta per (tile, class group) per frame, so the page never scales with raw events.
Readability holds: touches change at most 8.8 % of known tiles in a frame, and a 30-day half-life dims a lit tile
0.03 % per era-C frame.

## 2. Compile layer: `compile/`

`python -I compile/build.py --params laps/LAP-NN/params.json` writes `compile/out/`:

| Output | Content | Size |
|---|---|---|
| `world.json` | continents, regions, tiles (indices only), cells, bridges, harbours, spurs, seat markers | ~0.6 MB |
| `timeline.bin` | frame-ordered infrastructure deltas, activity checkpoints, dense per-frame series | ~6 MB |
| `launches.json`, `nations.json` | CONTRACT §8 records plus render keyframes; legend rows with entry frame, colour, pitch | ~0.4 MB |
| `camera.f32` | F x 3 (cx, cy, scale), solved | 240 KB |
| `audio.wav` | 48 kHz stereo float32, exactly F x 1,600 samples | ~250 MB |
| `kw-data.js` | `window.KW_DATA` wrapping the page's inputs as base64 typed arrays (loads from `file://`) | ~9 MB |
| `receipt.json` | `events_sha256`, params hash, output hashes, the section 1 table recomputed | small |

No names reach `kw-data.js`; `names.json` stays local unless `labels` is set.

### 2.1 Rate schedule

A monotone piecewise-linear `T(ts)` per era (`era_rates`), optional log-rate crossfade `era_ramp_s` at boundaries,
`tail_s` of 12 s for the pull-back and tally card. Per frame: `tau[f]` (story days) and `rate_label[f]`. Every event
maps by `f = floor(T(ts) * fps)`.

### 2.2 World layout (data from `repos.json`)

Reads `lineages[].id, kind, hosts, paths{host: [member paths]}, first_ts, third_party, foreign_org,
worktree_records, remotes`, and from events each tile's first-touch frame and touch weight.

1. Continents = hosts at fixed axial anchors (omen-e, omen-c, omen-linux west to east by first territory; AM4, FX99
   small southern landmasses; GitHub an archipelago). `cloud` has no land.
2. Regions = one per (lineage, host), on a deterministic hex spiral from the anchor ordered by `first_ts`, so reveal
   grows outward and the explored box grows monotonically. Two hosts, one bridge.
3. Tiles = depth-2 directories, `cells = 1 + floor(log2(1 + w))`, grown breadth-first in first-touch order.
   Corpus v1 has no per-directory file counts, so `w` = births + distinct commits touching the tile; a counts-only
   `tiles.ndjson` is a contract request. Expected 6,000 to 9,000 cells (spike range 5,000 to 20,000).
4. Spurs: each `worktree` event (94 under `work/worktrees` on omen-linux, all carrying a lineage) gets a one-cell
   spur at an angle from `sha1(ref)`. MIRV warheads aim at spurs.
5. Third-party lineages carry `ruin=1`; `third_party: hidden` drops them and re-packs.

### 2.3 Launches (`launches.py`)

1. **Episodes**: per non-third-party lineage, a commit gap over `episode_gap_h` closes an episode.
2. **Session join by activity, not span.** Sessions run long (p50 0.9 h, p90 20 h, max 489 h **[measured]**); a span
   overlap joins one session to weeks of episodes. A session joins when one of its `chat_msg` minute buckets on that
   lineage falls in `[t0 - session_overlap_min, t1 + session_overlap_min]`.
3. **Nation**: dominant non-human commit class (trailers); else the class with most joined messages; else `human`.
   Codex rarely writes a trailer (46 commits), so the session rule credits its 65 launches.
4. **Yield** per CONTRACT §8; integrations count seats from HEARTH `backend` in the window. Under `min_yield` the
   episode stays infrastructure.
5. **Engagement grouping**: episodes on different lineages union when they share a joined session.
   `engagement_union: session_or_nation` (also same-nation overlap) made 260 of 472 launches MIRVs, flooding the
   shape signal.
6. **Shape**: targets = distinct lineages + worktree births in the window. **Not `meta.hosts`**: it lists every host
   where the sha exists today, so a commit later copied to omen-linux becomes a second target (227 of 806 false
   MIRVs **[measured]**). At least `mirv_min_targets` makes a MIRV. **Unified** = a single-target launch within
   `unify_window_h` after a MIRV that hit its lineage plus another target, with at least half the MIRV's lines.
   Result: MIRVs from 2026-04 (3), then 4, 11, 24, 11 from July to October; unifications cluster in August (9 of
   16). The operator's curve falls out of the data.
7. **Yield class**: `score = log10(max(lines, 1))` or `composite` (+ 0.5 log10 files + 0.25 integrations + 0.1
   moving pieces); `band = clamp(floor(score), 1, 6)` by the edges in `yield_bands`.
8. **Non-git episodes (v1.4)**: a day with at least `min_yield.files` births or updates opens one; days within
   `episode_gap_days` merge; `lines` null, so the score is `log10(files) + 0.5 log10(bytes / 1e4)` on the same band
   scale. ChatGPT-inferred nations carry `nation_inferred` and render at reduced chroma (`inferred_nation: credit |
   human`), so the research program shows its hand without a claim it cannot support.
9. **Nations**: rows by first appearance, generation rows inside (`generation_granularity: major`: family plus major
   from trailers and session `models`, so `claude-opus-4.8` and `claude-opus-4-8` join). `nation_entry:
   first_event` adds a legend row at the first event of any kind (the direction names the first ChatGPT
   conversation); `first_test` waits for a test. `test_credit: conductor` tallies the conducting nation; local seats
   and OpenCode never commit, so their rows show participations.

Per launch, render keyframes: `f_launch`, `f_split` (MIRV), per warhead `f_land` (real first-commit order in the
window compressed into `warhead_spread_s`), target cell; for unified launches the source cells it consolidates.

### 2.4 Infrastructure fields (`timeline.py`)

A commit touches each tile in `files` at `1 + log10(1 + lines / nfiles)`; a birth or update at `1 + log10(1 + n)`;
a joined chat bucket at `0.25 * log2(1 + n)`; branch and worktree births touch the spur; third-party touches stay
at the explored state.

1. **Deltas**: one record per (frame, tile, class group), columns with `delta_start[f]` (Int32, F + 1): frame `f`
   is an O(1) slice. This is the sparse event index RaidUI lacks.
2. **Activity**: `A(f) = A(c) * D(c, f) + sum of w_i * D(f_i, f)` over deltas in `(c, f]`, with
   `D(a, b) = 2^(-(tau[b] - tau[a]) / fog_half_life_days)`. Exact, so checkpoints every 900 frames (23 x 2,923 x 8 x
   Float32 = 2.2 MB) bound replay to 900 frames. Explored is `f >= tile_first_frame[k]`, no state.
3. **Dense series**: tallies per nation (tests, cumulative yield, commits, files) and per surface; radio band per
   class; hum level; HQ host (most session activity, trailing 7 story days, 2 s glide: the migration reads here);
   beams as intervals; offload sparks per (frame, seat).
4. **Camera**: padded explored box as target, a critically damped spring of half-time `camera_ease_s` stepped in
   compile; the tail pulls back to the whole known world. `camera: fixed_world` is the control arm.

## 3. Audio synthesis (`audio.py`)

Every onset is sample `f * 1,600`: the first sample of the frame where the picture shows it.

- **Launch tones**: nation pitch (human A3 220 Hz, Claude E4 329.6, Codex G4 392.0, OpenCode B4 493.9, local C3
  130.8, automation D4 293.7), sine with partials at -12 and -20 dB, length `0.15 * 1.5^(band - 1)` s (0.15 to
  1.14), gain `-24 + 3 * band` dBFS. Generations shade partial balance, never pitch.
- **Shape**: a MIRV plays its tone, then a 60 ms tick an octave up per warhead at `f_land`; a unified launch plays an
  octave down at 1.5 times the length.
- **Firsts**: a lineage's first test keeps the low bell (partials 1, 2.76, 5.40, 8.93 on C2, 3 s); a nation's first
  test doubles its tone at the octave with a 2 s tail.
- **Collapse**: per nation trailing 1 s count; above `collapse_events_per_s`, a roll (8 Hz) or chord
  (`collapse_mode`), gain `0.15 * log2(1 + rate / 8)`, 20 % hysteresis.
- **Infrastructure**: hum (55 + 110 Hz) at `-36 + 6 * log10(1 + commits_per_s)` dBFS, ceiling -24; static from a
  seeded PCG32 over integers, band-passed per class (600 Hz to 3.2 kHz, Q 4), following the radio series, ceiling
  -18. The ChatGPT years are static by construction. Sparks join the static (`offload_sound`).
- Soft-knee limiter at -1 dBFS; length exactly `F * 1,600`; hash in the receipt.

**Alignment proof** (every export): `probe: on` puts a white frame at `f_p` and a 1 ms click at `f_p * 1,600` in a
10 s segment; after muxing, `ffprobe` checks duration `F / 30` and `F * 1,600` samples, then the decoded white
frame's start is compared with the click peak. Pass: under 1 ms once the MP4 edit list removes AAC's 1,024-sample
priming.

## 4. Renderer: `render/index.html` (Canvas 2D, pure)

| Module | From RaidUI | Role |
|---|---|---|
| `data.js` | schema rule | decode `KW_DATA`, refuse a wrong `version`, drop unknown enums |
| `state.js` | `render-state.js` | `buildState(f, out)`: checkpoint plus delta replay into preallocated scratch; active launches by binary search |
| `layers.js` | `registry.js` | `{id, zIndex, render(ctx, state)}`, save/restore, per-layer try/catch into the frame receipt |
| `palette.js` | `palette.js` | OKLCH by nation; generation shades as 0.06 lightness steps; `hue_axis: surface` swaps the key |
| `decay.js` | `trails-2s` | age-to-alpha in output seconds |
| `launch.js` | new | bloom, MIRV beam and split, unified convergence |
| `border.js` | Transport readout | ticker, rate, legend, tallies, radio band |
| `clock.js` | `playback-controller.js` | preview only (0.25x to 64x, scrub); export calls `renderFrame(f)` |

Purity: no `Date`, no `Math.random` (mulberry32 by index), no rAF under `?export=1`, JetBrains Mono as base64 WOFF2
behind `document.fonts.ready`, activity quantised to 32 levels, land as one `Path2D` per colour bucket (~300 fills).

**The two physics as a luminance budget**: field layers draw with normal compositing under OKLCH L 0.55; launch
layers draw with `lighter` and own L 0.55 to 0.95. Infrastructure cannot read as a detonation at any commit rate.

Draw order (map clipped to a 1,360 x 896 viewport):

0. Background `#07090e`, sea lattice at 4 %.
1. Explored land: host terrain tint, desaturated. 2. Ruins: grey cached hatch.
3. Activity field: class-weighted colour, lightness `log(1 + A)` quantised.
4. Structure: bridges, harbours, spurs.
5. Radio: faint comms beams HQ to region (the countdown), ChatGPT rings, offload sparks to seat markers.
6. Launches: bloom radius `1.5 * 1.6^(band - 1)` cells (1.5 to 15.7), life `0.6 + 0.4 * band` s. MIRV: a beam from
   HQ in the nation colour splits at 60 % of the path at `f_split`; warheads arc to their spurs and bloom at `f_land`,
   sized by share of lines. Unified: converging lines from the consolidated cells for 0.5 s, then one bloom a band
   larger. Merge per region under collapse; total bloom luminance capped so 15 concurrent cannot white out.
7. Markers: HQ, seats.
8. Border (opaque, unclipped): top 64 px date ticker (year, month or day by era) with the rate; right 320 px **nation
   legend**, one row per nation appearing at its entry frame: swatch, name, generation swatches, tests (28 px tabular),
   cumulative yield (`1.2M` lines, or files for non-git), and a 14 px capacity line (commits, files); left 240 px
   surface tallies; bottom 120 px radio band, a 12 s trace by class.
9. End card: final tallies per nation, tiles explored against laid out.

## 5. Export pipeline and budget

**[measured]** spike page (5,000 hexes, 200 radial gradients), 1080p, per frame including render:

| Capture | ms / frame | Bytes |
|---|---|---|
| `page.screenshot` PNG (spike path) | 250 | 1.6 MB |
| CDP `Page.captureScreenshot` PNG, `optimizeForSpeed` (lossless) | **66.7** | 2.0 MB |
| `canvas.toDataURL('image/png')` | 79.3 | 2.4 MB |
| `toDataURL('image/jpeg', 0.95)` | 32.7 | 0.6 MB |

Parallel CDP PNG, one Chromium per worker: K = 1, 82.9 ms; **K = 8, 10.6 ms effective; K = 12, 7.8 ms**. Piped PNG
to libx264 medium crf 18: 55 fps per encoder at 2 threads. The same frames captured by two browsers in opposite
orders gave identical PNG sha256 (6 of 6).

1. 60 s segments (1,800 frames, 12 in all). `export_workers` (default 10) each take the next segment, call
   `renderFrame(f)`, capture over CDP and pipe into their own `ffmpeg -f image2pipe -c:v png -i - -c:v libx264
   -preset medium -crf 18 -pix_fmt yuv420p -g 60 -threads 2`. No frame touches disk (40 GB as PNG).
2. Per-frame sha256 into `frames.sha256`; a segment is done when its MP4 and hashes are complete: resume by segment.
3. `ffmpeg -f concat -c copy`, mux `audio.wav` as AAC LC 256 kb/s, no `-shortest` (lengths equal and checked).
4. Determinism receipt: 30 sampled frames re-rendered by another worker in another order must match; compile twice
   gives identical bytes; `buildState` under Node matches a brute-force Python sum at frame 0, a checkpoint
   boundary and the 2026-10-03 burst.

**Estimate, full piece at 1080p 30 fps: about 9 minutes wall.** Capture floor at K = 12: 20,047 x 7.8 ms = 2.6
min; encoders share the cores (x 1.5); real content at twice the spike's raster cost (a margin: ~300 fills and at
most 15 blooms against 3,500 fills and 200 gradients); plus warm-up, concat, mux. The 90 s cut: about 1.2 minutes.
Laps review the cut and targeted windows; full exports are for candidates.

If slice 3 measures slower, the ladder (each rung a switch, recorded): workers to 16; CDP JPEG q 95 (33 ms single;
hash decoded RGBA); `fps: 24` (2,000 samples per frame); `scale: 0.833` (1600 x 900).

**4K**: `scale: 2` draws the same `render(f)` at 3,840 x 2,160. Unmeasured: about 270 ms single, 31 ms at K = 12,
with 4K encode a co-bottleneck: 20 to 30 minutes. A 4K lap measures it first.

## 6. The 90-second cut

`cut_90s_multiple: auto` = master length / 90 (7.43). Cut frame `g` renders master time `g / 30 * m`; screen-time
envelopes (bloom life, beam travel, warhead spread, camera ease) divide by `m`. Audio is re-synthesised with times
divided by `m`, not resampled (no pitch shift). The rate label multiplies.

## 7. Parameter table (`compile/params.json`, one key each)

| Key | Default | Effect |
|---|---|---|
| `fog_half_life_days` | 30 | decay `D(a, b)` |
| `hue_axis` | actor | nation or surface |
| `geography` | surfaces | continents by host, or by lineage family |
| `collapse_events_per_s` | 8 | roll or chord, visual merge |
| `camera` | fit_known | or fixed_world |
| `third_party` | ruins | ruins, hidden, shown (counted) |
| `era_rates` | A 4 s/yr, B 2.5 s/mo, C 2.4 s/day | schedule |
| `cut_90s_multiple` | auto | cut multiple |
| `episode_gap_h`, `episode_gap_days` | 2, 1 | git and non-git episode boundaries |
| `session_overlap_min` | 30 | join window |
| `min_yield` | lines 50 or files 3 | test threshold |
| `yield_bands` | log10 edges 1 to 6 | band edges |
| `mirv_min_targets`, `unify_window_h` | 2, 24 | shape thresholds |
| `generation_shades` | true | shades or one hue per class |
| `session_join` | activity | or span |
| `engagement_union` | session | or session_or_nation |
| `yield_score` | lines | or composite |
| `generation_granularity` | major | major, minor, off |
| `nation_entry` | first_event | or first_test |
| `test_credit` | conductor | or conductor_and_participants |
| `inferred_nation` | credit | or human |
| `collapse_mode` | roll | or chord |
| `warhead_spread_s` | 0.4 | landing spread |
| `era_ramp_s`, `camera_ease_s`, `camera_pad` | 2, 3, 0.12 | transitions |
| `labels`, `offload_sound` | off, hiss | names stay local; spark sound |
| `fps`, `scale`, `export_workers`, `probe` | 30, 1, 10, off | export only |

## 8. Thin-slice build order

1. `launches.py` + `nations.json` + receipt: the section 1 table and a launch strip PNG (time on x, band as
   height, nation colour, MIRVs marked). Derek judges the event model before a map exists.
2. `schedule.py` + ticker-only `render(f)`; 10 s through the segment pipeline with the sync probe.
3. **The thin slice**: black map, regions as dots, launches as blooms with tones and the growing legend; a timed
   full export. The reference's grammar end to end and the budget's real measurement.
4. Layout and infrastructure fields (fog, activity, checkpoints, Node test), hum and static.
5. MIRV and unified rendering and sound.
6. Radio layer, camera spring, bridges, harbours, spurs, ruins, surface tallies.
7. The 90 s cut and end card; then laps, one parameter each.

## 9. Open risks

1. Era A is near empty: no git test before 2023-11; the early flashes depend on non-git episodes, and their volume
   waits on `file_update` in the merged corpus.
2. Bands 5 and 6 (25 launches) likely include imports and vendored copies (785 commits in one film-second on the
   2026-03 import day); they may read as megatons that were copies. A lap on a per-commit lines cap or a bulk rule.
3. 11,164 commits lack numstat; their episodes pass on files only and their yield is understated.
4. Commits cannot be attributed to a worktree (chat paths stop at `work/worktrees`); MIRV targets rely on worktree
   births. A depth-3 cwd for worktree paths would sharpen them.
5. OpenCode never appears in a launch window: it enters the legend with zero tests.
6. Up to 8 launches share a frame (batched timestamps); staggering would be a lie, so the merge must read as one.
7. The estimate rests on the spike page; slice 3 measures real content. bench27 work on the same 24 cores would
   stretch it; workers run under nice.
8. Tile area has no file counts in corpus v1; the touch proxy makes busy directories large.
9. No chat source covers 2026-04: the radio band goes silent for a month while launches continue.
10. Hashes hold per Chromium build (1248); AAC priming breaks sync unless the probe runs on every export.
