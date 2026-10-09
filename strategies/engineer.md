# Strategy: engineer (pipeline first), direction rev 2

Strategist: engineer angle, Workflow 2, day 2026-10-09. Inputs: DIRECTION.md (payload model, Shape, Two evolutions),
CONTRACT.md §1/3/7/8, CORPUS-REPORT.md, SURVEY.md §4/4b, spike 01, RaidUI vendor copies, 2-strategy.md criteria.
Figures marked **[measured]** were taken in this session with a prototype of `compile/launches.py` and a capture
harness over the spike page; the scripts live in the session scratchpad and printed counts only (no corpus line).

## 0. The one idea

One integer clock and two physics. Output frame `f` (30 fps) is the only time axis. Compile (Python 3.14 + numpy)
makes every judgement: it detects launches, measures yield, assigns shape and nation, folds infrastructure into
per-tile fields, and solves the camera. The page's `render(f)` is a pure lookup-and-draw. Audio is synthesised from
the same frame-indexed tables at 1,600 samples per frame (48,000 / 30, an exact integer). Every DIRECTION.md
parameter is read only by compile, so a lap is one key in `params.json`, a recompile in seconds and a re-export in
minutes.

## 1. Densities this design is sized for

Default parameters, 2026-10-09T13:00Z snapshot, piece length 668.2 s = **20,047 frames** (A 46.7 s, B 87.5 s,
C 534.1 s).

| Layer | Measure **[measured]** | Value |
|---|---|---|
| Launches | episodes (2 h gap) / above min yield / launches after engagement grouping | 935 / 827 / **816** |
| | shape: single / MIRV / unified | 746 / 54 / 16 |
| | MIRV warheads: 2 / 3 / 5 / 7 / 8+ | 22 / 19 / 4 / 1 / 8 |
| | yield band (floor log10 lines) 1 / 2 / 3 / 4 / 5 / 6 | 52 / 289 / 341 / 109 / 21 / 4 |
| | per month, 2026-03 to 2026-10 | 55, 57, 90, 67, 157, 167, 169, 40 (before: 2023-11 one, 2025-07 one, 2026-01 twelve) |
| | **peak in one film-second** / max in any sliding 1 s / seconds at 8 or more | **11** / 12 / 8 |
| | max launches starting in one frame / max blooms alive at once | 8 / 15 |
| | gap sensitivity: 1 h gives 1,132 launches, peak 17/s; 4 h gives 636, peak 11/s | |
| Infrastructure | August 2026 mean per film-second: commits / folded chat messages | 35 / 710 |
| | peak per film-second: commits (2026-03 import) / chat messages / offload calls (2026-10-03) | 785 / 14,748 / 13,876 |
| | tiles (lineage, depth-2 path), non-third-party | 2,923 |
| | share of known tiles touched in one frame (known > 200): p50 / p99 / max | 0.19 % / 2.3 % / 8.8 % |
| Nations | first conducted test: human / Claude / Codex / automation | 2023-11-03 / 2026-01-20 / 2026-07-02 / 2026-07-03 |
| | first participation: local seats (offload in a launch window) | 2026-07-18 (153 launches) |
| | first event, radio only: ChatGPT / OpenCode | 2023-04-17 / 2026-09-27 |
| | Claude generations, first test (commit trailers) | Opus 4 01-20, Sonnet 4 01-21, Haiku 4 06-05, Fable 5 06-10, Sonnet 5 07-04, Opus 5 07-29 |

Design peak: **12 launches per second** (collapse rule active in about 8 seconds of the piece) and **15,000
infrastructure events per second** folded to at most one delta per (tile, class group) per frame. The page never
scales with raw events. Readability holds: direct touches change at most 8.8 % of known tiles in a frame, and decay
at a 30-day half-life dims a lit tile by 0.03 % per era-C frame.

## 2. Compile layer: `compile/`

`python -I compile/build.py --params laps/LAP-NN/params.json` writes `compile/out/`:

| Output | Shape | Size |
|---|---|---|
| `world.json` | continents, regions, tiles (indices only), cell lists, bridges, harbours, seat markers | about 0.6 MB |
| `timeline.bin` | frame-ordered infrastructure deltas, activity checkpoints, dense per-frame series | about 6 MB |
| `launches.json` | CONTRACT §8 records plus render keyframes (frames, target cells, warhead order) | about 0.4 MB |
| `nations.json` | CONTRACT §8 nation and generation rows, entry frame, colour, pitch | under 10 KB |
| `camera.f32` | F x 3 (cx, cy, scale), solved | 240 KB |
| `audio.wav` | 48 kHz stereo float32, exactly F x 1,600 samples | about 250 MB |
| `kw-data.js` | `window.KW_DATA = {...}` wrapping the above as base64 typed arrays, so the page loads from `file://` | about 9 MB |
| `receipt.json` | input `events_sha256`, params hash, every output hash, the section 1 table recomputed | small |

Names never reach `kw-data.js`; regions and tiles are indices, and `names.json` stays local unless `labels` is set.

### 2.1 Rate schedule (`schedule.py`)

A monotone piecewise-linear map `T(ts)` from story time to output seconds, one segment per era (`era_rates`), with an
optional log-rate crossfade of `era_ramp_s` at the boundaries, a `tail_s` of 12 s for the pull-back and the tally
card. Emitted per frame: `tau[f]` (Float64 story days) and `rate_label[f]`. Every event and launch maps by
`f = floor(T(ts) * fps)`.

### 2.2 World layout (`layout.py`) and the data it needs

From `repos.json.lineages[]`: `id, kind (git|dir|github), hosts, paths{host: [member paths]}, first_ts,
third_party, foreign_org, worktree_records, remotes, members`. From `events.ndjson`: the tile set (lineage, host,
depth-2 path from commit `files`, births and joined chat), each tile's first-touch frame and touch weight.

1. Continents = hosts at fixed axial anchors on one hex lattice, west to east by first territory (omen-e, omen-c,
   omen-linux; AM4 and FX99 small southern landmasses; GitHub an archipelago at sea). `cloud` has no land.
2. Regions = one per (lineage, host), placed by a deterministic hex spiral from the anchor, ordered by `first_ts`, so
   reveal grows outward and the explored bounding box grows monotonically. A lineage on two hosts gets a bridge.
3. Tiles = depth-2 directories, `cells = 1 + floor(log2(1 + w))`, grown breadth-first from the region seed in
   first-touch order. Corpus v1 has no per-directory file counts, so `w` = births `n` + distinct commits touching
   the tile; a counts-only `tiles.ndjson` (file count per depth-2 directory at tip) is a contract revision request.
   Expected total 6,000 to 9,000 cells, inside the spike's 5,000 to 20,000 range.
4. Worktree spurs: each `worktree` event (94 under `work/worktrees` on omen-linux, all carrying their lineage) gets a
   one-cell spur off its region at an angle from `sha1(ref)`. MIRV warheads aim at these spurs.
5. Third-party lineages carry `ruin=1`; `third_party: hidden` drops them before layout and the world re-packs.

### 2.3 Launches (`launches.py`): the event model

Deterministic, sorted inputs, byte-identical across runs. The prototype gives the section 1 counts.

1. **Episodes.** Per non-third-party lineage, sort commits; a gap over `episode_gap_h` closes an episode.
2. **Session join by activity, not span.** Claude and Codex sessions run long (p50 0.9 h, p90 20 h, max 489 h
   **[measured]**), so a span overlap joins one session to weeks of episodes. A session joins an episode when one of
   its `chat_msg` minute buckets on that lineage falls inside `[t0 - session_overlap_min, t1 + session_overlap_min]`.
   `session_join: span` is the control arm.
3. **Nation.** The dominant non-human commit class (AI trailers); else the class with most joined messages; else
   `human`. Codex rarely writes a trailer (46 commits), so the session rule is what credits Codex with 65 launches.
4. **Yield.** `lines` = sum of ins + del; `files` = distinct depth-2 paths; `integrations` = distinct lineages +
   distinct seats called (HEARTH `backend` in the window) + session hosts; `moving_pieces` = distinct depth-2 paths +
   branches and worktrees born in `[t0 - 1 h, t1]` + distinct agent classes. An episode under `min_yield` (50 lines
   and under 3 files) stays infrastructure.
5. **Engagement grouping.** Episodes on different lineages are unioned when they share a joined session (one operator
   engagement). `engagement_union: session_or_nation` (also union same-nation overlap) is a measured alternative: it
   makes 260 of 472 launches MIRVs, which floods the shape signal, so it is not the default.
6. **Shape.** Targets = distinct lineages in the engagement + worktree births in the window. **Do not use
   `meta.hosts`**: it lists every host where the sha exists today, so a commit later copied to omen-linux counts as
   a second target; under that rule 227 of 806 launches were false MIRVs **[measured]**. Targets of at least
   `mirv_min_targets` make a MIRV with that many warheads. A **unified** launch is a single-target launch on a
   lineage within `unify_window_h` after a MIRV that hit it plus another target, with lines at least half the
   MIRV's. Result: MIRVs appear in 2026-04 (3), then 4, 11, 24, 11 from July to October; unifications cluster in
   August (9 of 16).
7. **Yield class.** `score = log10(max(lines, 1))` (`yield_score: lines`), or `composite` = log10 lines + 0.5 log10
   files + 0.25 integrations + 0.1 moving pieces; `band = clamp(floor(score), 1, 6)`; `yield_bands` holds the edges
   so a lap can retune them.
8. **Nations.** `nations.json` rows ordered by first appearance, with generation rows inside each class
   (`generation_granularity: major`, the family plus major version from trailers and session `models`, so
   `claude-opus-4.8` and `claude-opus-4-8` join). `nation_entry: first_event` (default, as the direction names the
   first ChatGPT conversation) adds a legend row at a nation's first event of any kind; `first_test` waits for a
   conducted or participated test. `test_credit: conductor` tallies a test for its nation only; local seats and
   OpenCode never commit, so they show a participation count (local seats 153) on their row.

Per launch, compile also emits render keyframes: `f_launch`, `f_split` (MIRV only), per warhead `f_land` (real
first-commit order inside the window compressed into `warhead_spread_s`, default 0.4 s), target cell, and for
unified launches the converging source cells of the MIRV it consolidates.

### 2.4 Infrastructure fields (`timeline.py`)

Touches: a commit touches each tile in `files` at weight `1 + log10(1 + lines / nfiles)` (weight 1 without numstat);
a file birth at `1 + log10(1 + n)`; a session-joined chat bucket at `0.25 * log2(1 + n)`; branch and worktree births
touch the spur. Third-party commits touch ruins only, capped at the explored state.

1. **Deltas**: one record per (frame, tile, class group) with summed `w`, packed as columns with `delta_start[f]`
   (Int32, F + 1), so frame `f` is an O(1) slice. This is the sparse event index RaidUI lacks.
2. **Activity**: `A(f) = A(c) * D(c, f) + sum of w_i * D(f_i, f)` over deltas in `(c, f]`, with
   `D(a, b) = 2^(-(tau[b] - tau[a]) / fog_half_life_days)`. Exact for exponential decay, so compile stores
   checkpoints every 900 frames (23 x 2,923 tiles x 8 groups x Float32 = 2.2 MB) and `buildState(f)` replays at most
   900 frames of deltas. Explored needs no state: `f >= tile_first_frame[k]`.
3. **Dense series** per frame: tallies (per nation tests, cumulative yield lines, commits, files; per surface the
   same), radio band (folded messages per class, smoothed over 0.5 s), hum level (commit rate), HQ host (most
   session activity over the trailing 7 story days, 2 s glide: the migration reads here), session beams as
   intervals, offload sparks per (frame, seat) as counts.
4. **Camera**: the padded bounding box of explored cells (monotone) as the target; a critically damped spring of
   half-time `camera_ease_s` stepped once per frame in compile; the tail pulls back to the whole known world.
   `camera: fixed_world` is the control arm.

## 3. Audio synthesis (`audio.py`, numpy, offline)

Every onset is at sample `f * 1,600`, the first sample of the frame where the picture shows the event.

- **Launch tones**: nation pitch (human A3 220 Hz, Claude E4 329.6, Codex G4 392.0, OpenCode B4 493.9, local C3
  130.8, automation D4 293.7), sine plus 2nd and 3rd partials at -12 and -20 dB, 4 ms attack. Length
  `0.15 * 1.5^(band - 1)` s (0.15 to 1.14 s), gain `-24 + 3 * band` dBFS. Generation shades the timbre slightly
  (partial balance), never the pitch.
- **Shape in sound**: a MIRV plays its tone at `f_launch`, then one short tick per warhead at its `f_land` (the
  nation pitch an octave up, 60 ms, -9 dB under the tone): the scatter is audible. A unified launch plays its tone
  an octave down at 1.5 times the length.
- **Firsts**: a lineage's first test keeps the low bell (inharmonic partials 1, 2.76, 5.40, 8.93 on C2, 3 s);
  a nation's first test doubles its tone at the octave with a 2 s tail. A radio-only nation entry is silent beyond
  its static colour.
- **Collapse**: per nation a trailing 1 s launch count; above `collapse_events_per_s` individual tones yield to a roll
  (8 Hz retrigger) or a chord (`collapse_mode`), gain `0.15 * log2(1 + rate / 8)`, 20 % hysteresis. Measured load:
  fires in about 8 seconds of the default piece.
- **Infrastructure**: a hum (55 Hz plus 110 Hz partial) at `-36 + 6 * log10(1 + commits_per_s)` dBFS smoothed over
  1 s, ceiling -24; radio static from a seeded PCG32 over integers (bytes survive numpy upgrades), band-passed per
  class (centre 600 Hz to 3.2 kHz, Q 4), amplitude following the radio series, total ceiling -18 dBFS. The ChatGPT
  years are static only by construction: no ChatGPT launch exists. Offload sparks join the static (`offload_sound:
  hiss | off`).
- Master: soft-knee limiter at -1 dBFS; length exactly `F * 1,600`; hash in the receipt.

**Alignment proof** (every export): a probe build (`probe: on`) puts a full-white frame at `f_p` and a 1 ms click at
sample `f_p * 1,600` in a 10 s segment. After muxing, `ffprobe` checks video duration `F / 30` and audio samples
`F * 1,600`; the probe MP4 is decoded (luma per frame, PCM) and the white frame's start is compared with the click
peak. Pass: under 1 ms after the MP4 edit list removes AAC's 1,024-sample priming.

## 4. Renderer: `render/index.html` + modules (Canvas 2D, pure)

| Module | From RaidUI | Role |
|---|---|---|
| `data.js` | schema-check rule | decode `KW_DATA`, refuse a wrong `version`, drop unknown enums |
| `state.js` | `render-state.js` | `buildState(f, out)`: checkpoint plus delta replay into preallocated `Float32Array` scratch; active launches by binary search on `f_launch` |
| `layers.js` | `registry.js` | overlay descriptors `{id, zIndex, render(ctx, state)}`, save/restore, per-layer try/catch logged to the frame receipt |
| `palette.js` | `palette.js` | OKLCH by nation; generation shades as lightness steps of 0.06 in entry order; `hue_axis: surface` swaps the key |
| `decay.js` | `trails-2s` | age-to-alpha for blooms, beams and sparks in output seconds |
| `launch.js` | new | single bloom, MIRV beam and split, unified convergence |
| `border.js` | Transport readout | ticker, rate, nation legend and tallies, surface tallies, radio band |
| `clock.js` | `playback-controller.js` | preview only: 0.25x to 64x, scrub; export calls `renderFrame(f)` directly |

Purity: no `Date`, no `Math.random` (mulberry32 seeded by index), no rAF under `?export=1`, JetBrains Mono embedded
as base64 WOFF2 behind `document.fonts.ready`, activity quantised to 32 levels. Land is drawn as one `Path2D` per
colour bucket (about 300 fills), not one fill per cell.

**The two physics as a luminance budget.** Field layers draw with normal compositing and a lightness ceiling of
OKLCH L 0.55; launch layers draw with `lighter` compositing and own L 0.55 to 0.95. Infrastructure can never read as
a detonation, whatever the commit rate.

Draw order (map layers clipped to the 1,360 x 896 viewport):

0. Background `#07090e`, sea lattice at 4 % alpha.
1. Explored land: terrain tint by host at low chroma, desaturated.
2. Ruins: grey cached hatch pattern.
3. Activity field: cells with `A > epsilon`, class-weighted colour mix, lightness `log(1 + A)` quantised.
4. Structure: bridges, harbours, worktree spurs.
5. Radio: comms beams HQ to region (faint, the countdown), ChatGPT rings, offload sparks HQ to seat markers.
6. Launches (`lighter`): single bloom radius `1.5 * 1.6^(band - 1)` cells (1.5 to 15.7), life `0.6 + 0.4 * band`
   s; MIRV: a beam from HQ in the nation colour, splits at 60 % of the path at `f_split`, warheads arc to their spurs
   and bloom at `f_land` with radius scaled by their share of lines; unified: converging lines from the consolidated
   warheads' cells for 0.5 s, then one bloom a band larger. Per-region merge when the collapse rule is active.
   Bloom luminance capped so 15 concurrent blooms cannot white out the viewport.
7. Markers: HQ, seat markers.
8. Border (opaque panels, unclipped): top 64 px date ticker (year in A, month in B, day in C) with the rate label;
   right 320 px **nation legend**: one row per nation in entry order, appearing at its entry frame (swatch,
   name, generation swatches, tests in 28 px tabular figures, cumulative yield lines as `1.2M`, then a 14 px second
   line of capacity: commits, files; local seats show participations); left 240 px surface tallies; bottom 120 px
   radio band, a 12 s scrolling trace coloured by class.
9. End card after the tail: final tallies per nation, tiles explored against laid out.

## 5. Export pipeline and budget

**[measured]** on this host, spike page (5,000 hexes, 200 radial gradients), 1080p, per frame including render:

| Capture | ms / frame | Bytes |
|---|---|---|
| `page.screenshot` PNG (spike path) | 250 | 1.6 MB |
| CDP `Page.captureScreenshot` PNG, `optimizeForSpeed` (lossless) | **66.7** | 2.0 MB |
| `canvas.toDataURL('image/png')` | 79.3 | 2.4 MB |
| `toDataURL('image/jpeg', 0.95)` | 32.7 | 0.6 MB |

Parallel CDP PNG, one Chromium per worker: K = 1, 82.9 ms; **K = 8, 10.6 ms effective; K = 12, 7.8 ms**. Encode
from a piped PNG stream, libx264 medium crf 18: 55 fps per encoder at 2 threads, 102 fps unthreaded. The same frame
captured by two browsers in opposite orders gave identical PNG sha256 (6 of 6 frames).

Pipeline (`export/frames.mjs`, `export/encode.sh`):

1. Split into 60 s segments (1,800 frames, 12 segments). A pool of `export_workers` (default 10) takes segments in
   order, calls `renderFrame(f)` then CDP capture, and pipes PNGs into its own `ffmpeg -f image2pipe -c:v png -i -
   -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -g 60 -threads 2`. No frame touches disk (the piece as PNG
   is about 40 GB).
2. Per-frame sha256 into `frames.sha256`; a segment is done when its MP4 and hash list are complete, so a run
   resumes by segment.
3. `ffmpeg -f concat -c copy`, then mux `audio.wav` as AAC LC 256 kb/s; no `-shortest` (lengths equal by
   construction and checked).
4. Determinism receipt: 30 sampled frames re-rendered by another worker in another order must match.

**Estimate, full piece at 1080p 30 fps: about 9 minutes wall.** Capture floor at K = 12 is 20,047 x 7.8 ms = 2.6
min; encoders share the cores (x 1.5); real content is assumed twice the spike's raster cost (it draws about 300
fills and at most 15 blooms against the spike's 3,500 fills and 200 gradients, so x 2 is a margin); plus warm-up,
concat and mux. The 90 s cut is about 1.2 minutes. Laps review the 90 s cut and targeted windows; full exports are
for candidates.

If slice 3 measures slower, the ladder: workers to 12 to 16; CDP JPEG at q 95 (33 ms single page; hash the decoded
RGBA instead of the bytes); `fps: 24` (2,000 samples per frame, still an integer); `scale: 0.833` (1600 x 900). Each
rung is a switch and is recorded in the receipt.

**4K path**: `scale: 2` draws the same `render(f)` on a 3,840 x 2,160 canvas. Not measured; scaling capture by
pixels gives about 270 ms single page, about 31 ms at K = 12, about 10 minutes of capture with 4K encode becoming a
co-bottleneck: 20 to 30 minutes. A 4K lap measures it before anyone relies on the figure.

## 6. The 90-second cut

Same compile, `cut_90s_multiple: auto` = master length / 90 (7.43). Cut frame `g` renders master time `g / 30 * m`;
screen-time envelopes (bloom life, beam travel, camera ease, warhead spread) divide by `m` so a bloom still lasts its
output seconds. Audio is re-synthesised from the same launch table with times divided by `m`, not resampled (that
would shift pitch); collapse fires far more often, which is the point. The ticker's rate label multiplies.

## 7. Determinism, stated as tests

- `render(f)` twice, any order, any worker: identical PNG bytes (receipt step 4; holds per Chromium build, 1248).
- Compile twice: identical `launches.json`, `timeline.bin`, `audio.wav` bytes.
- `buildState` under Node at frame 0, a checkpoint boundary and the 2026-10-03 burst, against a brute-force Python
  sum of decayed deltas (tolerance 1e-4 before quantisation).
- `launches.py` receipt recomputes the section 1 table; a lap that changes a count says so in its receipt.

## 8. Parameter table (compile switches, one key each, in `compile/params.json`)

| Key | Default | Effect |
|---|---|---|
| `fog_half_life_days` | 30 | `D(a, b)`; checkpoints recomputed |
| `hue_axis` | actor | palette key: nation or surface |
| `geography` | surfaces | continents by host, or one per lineage family |
| `collapse_events_per_s` | 8 | audio roll or chord and visual merge threshold |
| `camera` | fit_known | or fixed_world |
| `third_party` | ruins | ruins, hidden (re-layout) or shown (counted, control arm) |
| `era_rates` | A 4 s/yr, B 2.5 s/mo, C 2.4 s/day | rate schedule |
| `cut_90s_multiple` | auto | uniform multiple for the cut |
| `episode_gap_h` | 2 | episode boundary |
| `session_overlap_min` | 30 | session join window |
| `min_yield` | lines 50 or files 3 | test threshold |
| `yield_bands` | log10 edges 1 to 6 | band edges |
| `mirv_min_targets` | 2 | MIRV threshold |
| `unify_window_h` | 24 | unification window |
| `generation_shades` | true | shade per generation, or one hue per class |
| `session_join` | activity | or span |
| `engagement_union` | session | or session_or_nation |
| `yield_score` | lines | or composite |
| `generation_granularity` | major | major, minor, off |
| `nation_entry` | first_event | or first_test |
| `test_credit` | conductor | or conductor_and_participants |
| `collapse_mode` | roll | or chord |
| `warhead_spread_s` | 0.4 | MIRV landing spread |
| `era_ramp_s`, `camera_ease_s`, `camera_pad` | 2, 3, 0.12 | transitions |
| `labels` | off | or regions (names leave the machine only on Derek's word) |
| `offload_sound` | hiss | or off |
| `fps`, `scale`, `export_workers`, `probe` | 30, 1, 10, off | export only |

## 9. Thin-slice build order (each step ends in something to look at or hear)

1. `launches.py` + `nations.json` + receipt: the section 1 table, plus a one-line launch strip PNG (time on x, band
   as height, colour by nation, MIRVs marked). Derek can judge the event model before any map exists.
2. `schedule.py` + a ticker-only `render(f)`; export 10 s through the segment pipeline with the sync probe: proves the
   clock, the pipe, the hashes and alignment.
3. **The thin slice**: black map, regions as dots on the spiral, launches as single blooms with tones and the growing
   legend. A full 11-minute export, timed: the reference's grammar end to end and the budget's real measurement.
4. Full layout and the infrastructure fields (fog, activity, checkpoints, Node state test), hum and static.
5. Shapes: MIRV beam and warheads, unified convergence, their sounds.
6. Radio layer, camera spring, bridges, harbours, spurs, ruins, surface tallies.
7. The 90 s cut and the end card; then laps, one parameter each.

## 10. Open risks

1. Era A has no tests: Derek's 2018 to 2022 commits fall below min yield or carry unmapped identities. The first
   flash is 2023-11; the "lonely early flashes" act may be empty unless identity mapping or min yield changes. A lap
   decision, not a bug.
2. Band 5 to 6 launches (25) likely include imports and vendored copies (the 2026-03 import day is 785 commits in
   one film-second); they may read as megatons that were copies. Needs a lap on a per-commit lines cap or a bulk rule.
3. 11,164 commits lack numstat (lines 0); their episodes pass only on files and their yield is understated.
4. Worktree commits cannot be attributed to a worktree (chat paths stop at depth 2, `work/worktrees`); MIRV targets
   rely on worktree births in the window. A contract revision carrying depth-3 cwd for worktree paths would sharpen
   it.
5. OpenCode never appears in a launch window; it enters the legend at first event with zero tests. Honest, but the
   industry curve's last entrant is silent.
6. 8 launches can start in one frame (batched timestamps); they sound as a chord. Staggering them would be a lie, so
   the collapse merge must make them read as one event.
7. Export estimate rests on the spike page; slice 3 measures real content. Concurrent bench27 work on the same 24
   cores would stretch it; workers run under nice.
8. Tile area by file count has no data in corpus v1; the touch-count proxy makes busy directories large.
9. No chat source covers 2026-04: the radio band goes silent for a month while launches continue.
10. Hashes are per Chromium build; a Playwright upgrade invalidates old receipts. AAC priming is the usual sync
    break; the probe catches it only if it runs on every export.
