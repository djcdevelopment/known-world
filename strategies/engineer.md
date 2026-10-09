# Strategy: engineer (pipeline first)

Strategist: engineer angle, Workflow 2, day 2026-10-09. Inputs: DIRECTION.md, CONTRACT.md §1/3/7, CORPUS-REPORT.md,
SURVEY.md §4/4b, spike 01, RaidUI vendor copies. New measurements taken for this strategy are marked **[measured
today]**; scripts and raw output live in the session scratchpad, not in the repository.

## 0. The one idea

One integer clock. Output frame `f` (30 fps) is the only time axis anything is keyed by. Compile (Python + numpy)
turns the corpus into **frame-indexed arrays**; the page's `render(f)` is a pure lookup-and-draw over those arrays;
audio is synthesised from the **same** frame-indexed event table at 1,600 samples per frame (48,000 / 30, an exact
integer). Every DIRECTION.md parameter is read only by compile, so a lap changes one YAML key, recompiles (seconds),
and re-exports (minutes).

## 1. Densities this design is sized for (from the merged corpus, counts only)

Under the initial rate schedule the piece is 668.2 s = **20,046 frames** (A 46.7 s, B 87.5 s, C 534.1 s).
Binning all 210,647 merged events into output seconds **[measured today]**:

| Measure | Value |
|---|---|
| Peak events in one output second (all kinds) | **16,286** (2026-10-03, the HEARTH offload burst) |
| Peak in one frame | 3,261; p99 frame 174 |
| Peak offload_call per second | 13,876 |
| Peak chat_msg records per second | 2,984 (48,583 folded messages incl. `n`) |
| Peak non-third-party commits per second | 794 (era C, 2026-03 import day); era C mean 17.5/s |
| Third-party commits, era B mean | 189/s (the llama.cpp fork history; ruins, muted) |
| Seconds where a single class exceeds 8 commit tones/s | human 94 of 216, claude 138 of 328 |
| Distinct tiles (lineage, depth-2 path) | 3,986 (1,069 touched by third-party authors), 199 regions |
| Tile onsets per frame as a share of known tiles (known > 200) | p99 3.1 %, max 8.7 % |

Design peak: **16,300 events/s, 3,300 per frame.** Nothing downstream may scale with raw events: compile folds
every frame to at most one delta per (tile, class) and one spark per (seat, class), so the page's per-frame work is
bounded by tiles, not events. The collapse rule is not an edge case: it is active in a third of era C's seconds.

The readability criterion (no more than 15 % of tiles changing per frame) holds on direct touches (max 8.7 %). Decay
is not "change": at h = 30 story days and era C's 0.0139 day per frame, a lit tile dims 0.03 % per frame.

## 2. Compile layer: `compile/` (Python 3.14, numpy, deterministic)

`compile/params.yaml` holds every switch (section 8). `python -I compile/build.py --params laps/LAP-NN/params.yaml`
writes `render/data/kw-data.js` (one `window.KW_DATA = {...}` with base64 typed arrays, loadable from `file://`
without fetch) plus `compile/out/audio-events.npz` and a receipt (input `events_sha256`, params hash, output hashes).

### 2.1 Rate schedule and story clock

`schedule.py` builds a monotone map from story time to output time: piecewise-linear segments per era (`era_rates`),
optional log-rate crossfade of `era_ramp_s` (default 2 s) at the two boundaries so the camera and decay do not jolt,
a `tail_s` (default 12 s) of silence and pull-back after the last event, and the end card. Emitted per frame:
`tau[f]` (Float64, story days since 2011-08-01), `rate_label[f]` (index into a short string table:
"1 yr = 4 s", "1 mo = 2.5 s", "1 day = 2.4 s", recomputed with the cut multiple). Events map by the inverse:
`f_e = floor(T(ts_e) * 30)`.

### 2.2 World layout: `layout.py` -> `world` block

Inputs from `repos.json`: per lineage `id, kind (git|dir|github), hosts, paths{host}, commits, first_ts,
third_party, foreign_org`; from events: the tile set (lineage, host, depth-2 path) with first-touch frame and touch
count; from `candidates`: nothing (never merged).

1. **Continents** = hosts, at fixed axial anchors on one hex lattice (west to east in chronological order of first
   territory: omen-e, omen-c, omen-linux; AM4 and FX99 as small southern landmasses; GitHub an archipelago in the
   south-east sea). `cloud` (ChatGPT) has no land: it is the HQ's broadcast.
2. **Regions** = lineage copies on a host (a lineage on two hosts gets two regions plus a bridge). Regions are placed
   in a continent by a deterministic hex spiral, ordered by `first_ts` (oldest nearest the anchor), so reveal grows
   outward and the camera's bounding box grows monotonically.
3. **Tiles** = depth-2 directories in a region; tile `k` occupies `c_k = 1 + floor(log2(1 + w_k))` cells grown by
   breadth-first fill from the region seed, sorted by first touch. `w_k` should be the file count; **the v1 corpus
   carries no file counts for git tiles** (only commit `files` lists and births' `n`), so v1 uses
   `w_k = births_n + distinct commits touching k` and requests contract v1.2: a counts-only `tiles.ndjson`
   (`ls-tree` count per depth-2 dir at tip, no names below depth 2). Estimated total: about 8,000 to 10,000 cells,
   inside the spike's 5,000 to 20,000 range (render 3.4 to 11.6 ms).
4. Chat paths that joined no lineage (17,763 Codex, 15,807 Claude records) attach to a per-host "wilds" region of
   home and scratch directories, revealed like any other; ChatGPT, ledger and `ct` events stay off-map.
5. Third-party lineages lay out identically but carry `ruin=1`; `third_party: hidden` removes their cells before
   layout (the world re-packs; a lap variable, so the switch is compile-time).

Emitted: `cell_q, cell_r` (Int16), `cell_tile` (Uint16), `tile_region`, `tile_host`, `tile_first_frame` (Int32),
`tile_ruin` (Uint8), `region_seed_xy`, `bridges` (region pairs and the frame both ends exist), `harbours` (regions
with a GitHub remote), `spurs` (branch and worktree births: region, frame, angle from a hash). **No names** reach
`kw-data.js`: tiles and regions are indices; a separate `compile/out/names.json` stays local, and labels are off
unless `labels: regions` is set (paths alone name private repositories).

### 2.3 Timeline: `timeline.py` -> deltas, checkpoints, series

Event to tile touches: a commit touches every tile in `files` (weight `1 + log10(1 + ins + del)`, numstat-less
commits weight 1); a file birth touches its tile (weight `1 + log10(1 + n)`); a session-joined chat record touches
its tile at weight 0.25 (radio lights territory faintly); branch, worktree and repo_born touch the region seed.

1. **Deltas** (frame-ordered, the sparse event index RaidUI lacks): one record per (frame, tile, class) with
   `w` (Float32 summed weight), `cnt` (Uint16), `kindmask` (Uint8). Packed as columns with `delta_start[f]` (Int32,
   length F + 1), so frame `f`'s deltas are a slice: O(1) lookup, no search.
2. **Activity** per tile per class group (8): `A(f) = A(c) * D(c, f) + sum over deltas in (c, f] of w * D(f_i, f)`,
   with `D(a, b) = 2^(-(tau[b] - tau[a]) / fog_half_life_days)`. Exact for exponential decay, so compile stores
   **checkpoints** every 900 frames (23 checkpoints x 3,986 tiles x 8 classes x Float32 = 2.9 MB) and `render(f)`
   replays at most 900 frames of deltas (about 2,600 records on average; worst slice under 40,000), well under 1 ms.
   Explored is not state at all: `f >= tile_first_frame[k]`.
3. **Camera** (`camera: fit_known`): per frame, the padded bounding box of explored cells (monotone), converted to
   target `(cx, cy, s)`; smoothed in compile by a critically damped spring stepped once per frame (half-time
   `camera_ease_s`, default 3 s), so the page reads `cam[f]` (Float32, F x 3, 240 KB) and never integrates. The
   tail pulls back to the whole-world box. `camera: fixed_world` is the control arm.
4. **Low-dimensional series**, dense per frame (O(1) lookup): tallies (Int32, F x 45: 8 classes x commits, files,
   messages; 7 surfaces x the same), radio band (Float32, F x 8: folded messages per class, smoothed over 0.5 s of
   output), HQ position (the host with most session cwd records over the trailing 7 story days, switching with a
   2 s glide; this is how the migration to omen-linux reads), session beams (intervals `[f0, f1, region, class]`
   with per-frame intensity from the radio series), offload sparks (per frame per seat per class: count; seat from
   `actor.name` through a 12-line `seats.json`, since ledger events carry the model name but no backend).
5. **Flashes and collapse (visual)**: a flash lives `flash_s` (0.5 s) of output time. Per region per frame, if more
   than `collapse_events_per_s / 30 * flash_frames` flashes would overlap, they merge into one region bloom with
   intensity `log2(1 + sum w)`; a chat spike or spark burst merges the same way per seat.

Total `kw-data.js`: about 8 to 10 MB raw, 12 MB base64; well under the 16 MB page budget and loaded once per worker.

### 2.4 Audio events: `audio-events.npz`

The same delta table, re-binned per (frame, class): commit count and summed `log(lines)`, repo births, chat rate per
class (the radio series), offload counts. The audio synthesiser never reads `events.ndjson`, so picture and sound
cannot disagree about what happened when.

## 3. Audio synthesis: `compile/audio.py` (numpy, offline, 48 kHz stereo float32 WAV)

- **Tones**: pitch by class (human A3 220 Hz, Claude E4 329.6, Codex G4 392.0, OpenCode B4 493.9, local models C3
  130.8, automation D4 293.7, third-party muted), sine plus 2nd and 3rd partials at -12 and -20 dB, 4 ms attack,
  exponential decay to -60 dB in 350 ms, gain `g = 0.12 * (1 + log10(1 + lines)) / 4`. Onset sample `s = f_e *
  1600`: the tone starts on the exact first sample of the flash frame.
- **Collapse** (`collapse_events_per_s: 8`, `collapse_mode: roll | chord`): per class, a trailing 1 s count over the
  frame table. Above the threshold the class's individual tones stop and a roll voice takes over (that class's
  pitch retriggered at a fixed 8 Hz with gain `0.15 * log2(1 + rate / 8)`); `chord` instead sustains a class chord
  (root, fifth, octave) with the same gain law. Hysteresis 20 % so the switch does not chatter.
- **Bells** for repo_born: inharmonic partials (1, 2.76, 5.40, 8.93) on a low C2 base, 3 s decay, capped at 2
  concurrent; extra births in the window add gain, not voices.
- **Radio static**: a seeded white-noise bed (own PCG32 over integers, not numpy distribution methods, so the bytes
  survive numpy upgrades) band-passed per class (centre 600 Hz to 3.2 kHz by class, Q 4, biquad), amplitude
  following that class's radio series with 50 ms smoothing, total limited at -18 dBFS. ChatGPT years: static only,
  no tones, by construction (no ChatGPT commits exist).
- **Sparks**: a 6 ms 2.4 kHz tick per offload, collapsing to a hiss above the threshold (`offload_sound: tick|off`).
- Master: soft-knee limiter at -1 dBFS, then the WAV. Length is exactly `F * 1600` samples. Hash recorded.

**Alignment proof** (a receipt, every export): compile inserts a sync probe in a probe build (`probe: on`): frame
`f_p` is a full white flash and sample `f_p * 1600` a 1 ms click. After muxing, `ffprobe` checks video duration
`F / 30` and audio sample count `F * 1600`; then the probe MP4 is decoded (video to rawvideo luma per frame, audio
to PCM) and the white frame's start time is compared to the click's peak sample. Pass: offset under 1 ms after the
MP4 edit list removes AAC's 1,024-sample priming. The probe runs on a 10 s segment, not the whole piece.

## 4. Renderer: `render/index.html` + `kw.js` (Canvas 2D, pure)

Modules (adapted from RaidUI; the vendor copies stay unedited):

| Module | From RaidUI | Role |
|---|---|---|
| `data.js` | schema check idea | decode `KW_DATA`, refuse a wrong `version`, drop unknown enums |
| `state.js` | `render-state.js` | `buildState(data, f, out)`: checkpoint + delta replay into preallocated `Float32Array(tiles x 8)` scratch; no allocation per frame |
| `layers.js` | `registry.js` | overlay descriptors `{id, zIndex, enabled, render(ctx, state)}` with save/restore and try/catch per layer (a failing layer is logged to a frame receipt, never silent) |
| `palette.js` | `palette.js` | OKLCH by class (warm white, green, coral, cyan, violet, ember, amber, grey) with djb2 +/-10 degree jitter per actor name; `hue_axis: surface` swaps the key |
| `decay.js` | `trails-2s.overlay` | age-to-alpha for flashes, beams and sparks (window of `flash_s`, resampled by frame) |
| `clock.js` | `playback-controller.js` | preview only: speeds 0.25x to 64x, scrub, `_tick`; export never touches it |
| `border.js` | Transport readout | tallies, ticker, rate, radio band |

Purity rules: no `Date`, no `Math.random` (mulberry32 seeded by tile index for hatching offsets), no rAF in export
mode (`?export=1`), JetBrains Mono embedded as a base64 WOFF2 and awaited through `document.fonts.ready`, colour
levels quantised (activity to 32 brightness levels) so float noise cannot move a pixel. Per frame the land is drawn
as **one Path2D per (colour bucket)**: at most 8 classes x 32 levels + terrain + ruins, about 300 fills instead of
10,000, which keeps JS time near the spike's 5,000-tile figure.

Draw order (map layers clipped to the inner viewport):

0. Background `#07090e` (the lab palette), faint sea lattice at 4 % alpha.
1. Explored land: cells with `first_frame <= f`, terrain tint by host at low chroma, dimmed and desaturated.
2. Ruins: third-party cells, grey with a cached `createPattern` hatch, never lit beyond explored.
3. Activity: cells with `A > epsilon`, colour as the activity-weighted mix of class colours, lightness by
   `log(1 + A)` quantised.
4. Structure: lineage bridges (quadratic curves over sea, lit when both ends exist), harbour marks, spurs.
5. Events, `globalCompositeOperation = 'lighter'`: commit flashes and region blooms, repo-born slow blooms.
6. Radio: session beams HQ to region, ChatGPT rings from HQ into the dark, offload sparks HQ to seat markers.
7. Markers: HQ, seat markers (omen-linux dense and MoE, AM4 tool seats, FX99).
8. Border (unclipped, opaque panels): top 64 px date ticker (`2026-07-04`, story-day resolution in era C, month in
   B, year in A) with the rate label on the right; left 260 px surface tallies (C:, E:, omen-linux, AM4, FX99,
   GitHub, radio); right 300 px class tallies (commits, files, messages; third-party in grey and marked "not
   counted" when `third_party: ruins`); bottom 120 px radio band, a 12 s scrolling stacked trace coloured by class.
   Tally digits 22 px tabular figures. Map viewport: 1,360 x 896.
9. End card after the tail: final tallies, span, counts of tiles explored vs laid out.

Interactive preview uses the same `render(f)` behind the clock, so what Derek scrubs is what exports.

## 5. Export pipeline and budget

The spike's 245 to 280 ms per frame is PNG compression in `page.screenshot`, not rendering. **[measured today]**
on this host, N = 5,000 hex tiles, 1080p, median total per frame including render:

| Capture | ms / frame | Bytes |
|---|---|---|
| `page.screenshot` PNG (spike path) | 249.5 | 1.6 MB |
| CDP `Page.captureScreenshot` PNG, `optimizeForSpeed` (lossless) | **69.0** | 2.0 MB |
| `canvas.toDataURL('image/png')` | 77.1 | 2.4 MB |
| `toDataURL('image/jpeg', 0.92)` | 30.2 | 0.5 MB |

Parallel, lossless CDP PNG, separate Chromium per worker: K = 1, 78.4 ms; **K = 8, 10.6 ms effective; K = 16,
6.6 ms** (24 cores, load 0.5 at the time). libx264 crf 18 preset medium encodes 1080p at about 340 fps and 4K at
about 63 fps (synthetic source).

Pipeline (`export/frames.mjs`, `export/encode.sh`):

1. Split the piece into 60 s segments (1,800 frames; 12 segments). A pool of K workers (default 10, `export_workers`)
   each takes the next segment, renders frames in order through `window.kw.renderFrame(f)` and CDP PNG, and pipes
   them into its own `ffmpeg -f image2pipe -c:v png -i - -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p
   -g 60 -threads 2 seg_NN.mp4`. No frame touches disk: the full piece as PNG would be about 40 GB against 50 GB
   free.
2. Every frame's sha256 (of the PNG bytes) goes to `frames.sha256`; a segment is done when its MP4 exists and its
   hash list is complete, so a failed run resumes by segment.
3. `ffmpeg -f concat -c copy` joins segments; a second pass muxes `audio.wav` as AAC LC 256 kb/s with no `-shortest`
   (lengths are equal by construction and checked).
4. Determinism receipt: 30 sampled frames re-rendered by a different worker in a different order must match
   `frames.sha256` exactly; Chromium build (1248) and font hash recorded.

**Estimate, full 11-minute piece at 1080p: about 8 minutes wall** (measured floor 3.5 minutes at K = 8; doubled for
real content, the encoders sharing cores, and per-segment warm-up). The 90 s cut (2,700 frames) is about 1 minute.
If the real renderer turns out slower than this (lap 1 measures it), the ladder is: more workers up to 16; JPEG
capture at q 95 (30 ms single-page; loses the lossless hash, so hash the decoded RGBA instead); 24 fps
(`fps` switch; 2,000 samples per frame, still an integer). **4K path**: the spike page's canvas is fixed at
1920 x 1080, so today's 4K timing is not a real 4K raster; scaling lossless capture by pixel count gives about
300 ms single-page, about 40 ms at K = 16, about 14 minutes plus 5 minutes of encode. The renderer takes `scale` so
the same `render(f)` draws at 2x; a 4K lap measures it before anyone relies on the figure.

## 6. The 90-second cut

Same compile, `cut_90s_multiple: auto` = `master_length / 90` (7.42 under the initial rates). The cut's frame `g`
renders master time `t = g / 30 * m`; screen-time envelopes (`flash_s`, beam fades, camera ease) are divided by `m`
so a flash still lasts 0.5 s of cut time. Audio is **re-synthesised**, not resampled (resampling would shift pitch),
from the same event table with times divided by `m`; collapse fires 7.4 times as often, which is the point. The
ticker's rate label multiplies (`1 day = 0.32 s`).

## 7. Determinism, stated as tests

- `render(f)` twice, any order, any worker: identical PNG bytes (receipt step 4).
- Compile twice: identical `kw-data.js`, `audio.wav` bytes (seeded PCG, sorted inputs, no wall clock).
- `buildState` runs under Node (as RaidUI's does) for a frame-0, checkpoint-boundary and mid-burst state check
  against a brute-force Python sum of decayed deltas (tolerance 1e-4 before quantisation).

## 8. Parameter table (compile switches; one key each)

| Key | Default | Effect |
|---|---|---|
| `fog_half_life_days` | 30 | `D(a,b)` in activity; checkpoints recomputed |
| `hue_axis` | actor | palette key: actor class or surface |
| `geography` | surfaces | continents by host; `lineage` packs one continent per lineage family |
| `collapse_events_per_s` | 8 | audio roll/chord threshold and visual bloom merge |
| `collapse_mode` | roll | roll or chord |
| `camera` | fit_known | fit_known or fixed_world |
| `third_party` | ruins | ruins, hidden (re-layout) or shown (counted, a control arm) |
| `era_rates` | A 4 s/yr, B 2.5 s/mo, C 2.4 s/day | rate schedule |
| `cut_90s_multiple` | auto | uniform multiple for the cut |
| `era_ramp_s` | 2 | log-rate crossfade at era boundaries (0 = hard cut) |
| `camera_ease_s`, `camera_pad` | 3, 0.12 | spring half-time, bounding-box padding |
| `flash_s` | 0.5 | flash life in output seconds |
| `labels` | off | off or regions (names leave the machine only on Derek's word) |
| `offload_sound` | tick | tick or off |
| `fps`, `scale`, `export_workers` | 30, 1, 10 | export only; do not change the picture's content |

Only compile reads these; the page reads arrays. A lap is a params file plus its receipt.

## 9. Thin-slice build order (each step ends in a frame or a sound you can look at)

1. `schedule.py` + a 60-line `render(f)` with only the ticker and rate label; export 10 s through the segment
   pipeline with the sync probe. Proves the clock, the pipe, the hash and the alignment receipt first.
2. `layout.py` with continents and regions as flat hexes (no fog): one still of the final world.
3. `timeline.py` explored set + tallies: the world reveals over the whole piece; first full-length export, timed
   (this is the budget's real measurement).
4. Activity with checkpoints, flashes, collapse merges; Node state test.
5. `audio.py` tones, collapse, bells; mux; listen to era C's March import day and the 2026-10-03 burst.
6. Radio layer: band, beams, rings, sparks, static bed.
7. Camera spring, bridges, harbours, spurs, ruins hatch, end card.
8. The 90 s cut; then hand to laps (one parameter per lap).

## 10. Open risks

1. Tile area by file count has no data in corpus v1; the proxy (touch count) makes busy directories large rather
   than big ones. Needs contract v1.2 counts or a recorded decision to keep the proxy.
2. The export estimate rests on a synthetic page; real content (gradients in 'lighter' mode, 300 Path2D fills,
   beams) may cost 2 to 4 times more raster. Step 3 measures it; the ladder in section 5 is the fallback.
3. Concurrent bench27 work on the same 24 cores would stretch the estimate; workers are a switch and run under nice.
4. Era B is 189 third-party commits per second against 1.5 of Derek's: as ruins they must stay visually silent or
   the "radio before territory" act reads as a building boom it was not.
5. The 2026-10-03 offload burst (13,876 sparks in one second) is a single-frame-scale whiteout risk even folded;
   the spark bloom needs a hard luminance ceiling.
6. No chat source covers 2026-04: the radio band goes silent for a month; the honesty rule says show it, the
   ticker should make it legible as a gap, not a bug.
7. Hash reproducibility is per Chromium build; an upgraded Playwright invalidates old receipts.
8. AAC priming and the MP4 edit list are the usual place sync breaks; the probe catches it only if it runs on
   every export.
