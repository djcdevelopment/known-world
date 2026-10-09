# STRATEGY.md: Known World, implementation strategy (Workflow 2 synthesis, 2026-10-09)

Direction rev 2 (payload model, Shape, Two evolutions). Three Candidates, two judge lenses (viewer, operator).
Combined: engineer 106, composer 98, cartographer 94.

## 0. Provenance: spine and grafts

**Spine: engineer** (`strategies/engineer.md`): top on determinism (10, 10) and budget (10, 9), the only measured
capture path, the only launch counts taken with a prototype `launches.py` on the merged corpus. Its pipeline, compile
formats, launch rules, luminance budget, sync probe and export plan stand unless a graft names a change.

| Graft | From | Replaces in spine |
|---|---|---|
| Tree-ring regions (tiles in first-touch spiral runs), facing bridge anchors (viewer best idea) | cartographer | generic spiral |
| Macro geography: Windows strait, omen-linux across open sea, archipelago rising at `created_at`, harbours, HQ crossing | cartographer | fixed anchors |
| Camera: 6 s lookahead, no zoom-in in era C, forward-backward smoother (operator best idea) | cartographer | damped spring |
| Flash radius constant in screen px (both lenses marked the spine's map-cell radius down) | cartographer, composer | radius in cells |
| Hollow-core inferred nations, radio-filtered F4 tone ("best honesty device") | cartographer | reduced chroma only |
| No replay of upstream history; 0.3 s attack ramp; per-commit lines cap; capped tile area | cartographer | additions |
| Era glides: 3 s log-rate smoothstep; only rate glyphs brighten 0.6 s (viewer best idea) | composer | linear `era_ramp_s` |
| Cut envelopes scaled by `m^(-1/2)` (operator best idea) | composer | envelopes / `m` |
| Era-by-era reading, intro/coda timing, tally card (spine had no era-A story) | composer | `tail_s` 12 |
| Ticker with 24-hour hairline; mirrored radio band | composer | single trace |
| Collapse as 125 ms chord bins then roll; offload crackle becomes a roar above 40/s | composer | roll or chord |
| One band table for tone, gain, bloom and radius | composer | two formulas |
| `nation_rule`, `generation_entry`, `local_backends`, `era_bounds` switches | composer | hard-coded |
| Pan by screen x | composer, cartographer | none |

Contradictions are marked **Resolved** in place, with the reason.

## 1. The one idea

One integer clock, two physics. Output frame `f` at 30 fps is the only time axis. Compile (Python 3.14 + numpy)
makes every judgement: launches, yield, shape, nation, fields, camera, pan. The page's `render(f)` is a pure
lookup-and-draw in Canvas 2D. Audio is synthesised from the same tables at exactly 1,600 samples per frame. Only
compile reads parameters: a Lap is one key, a recompile in seconds, an export in minutes. The two physics are a
**luminance budget**: field layers draw in normal compositing capped at OKLCH L 0.55; launch layers draw in `lighter`
and own L 0.55 to 0.95. Infrastructure cannot read as a detonation at any commit rate; nothing flashes per commit.

## 2. Densities the design is sized for

Spine figures, 13:00Z snapshot, default parameters:

| Measure | Value |
|---|---|
| Episodes / tests / launches after grouping | 935 / 827 / **816** (746 single, 54 MIRV from 2026-04, 16 unified, 9 in August) |
| Yield bands 1 to 6 | 52 / 289 / 341 / 109 / 21 / 4 |
| Launches per month 2026-03 to 10 | 55, 57, 90, 67, 157, 167, 169, 40 |
| Peak per film-second / max blooms alive | **11** (12 sliding) / 15 |
| Non-git launches (births only) | 133, first 2020-12 |
| Infrastructure per film-second: August mean commits / chat; peaks commits / chat / offloads | 35 / 710; 785 / 14,748 / 13,876 |
| Known tiles touched per frame p50 / p99 / max (2,923 own tiles) | 0.19 % / 2.3 % / 8.8 % |

Design peaks: **12 launches/s** in the full piece (collapse about 8 s), **about 37 per output second in the cut**
(composer's probe at `m` 8.05; the receipt recomputes it), **15,000 infrastructure events/s** folded to one delta per
(tile, class group) per frame. Worst-frame tile change is 8.8 %, under the 15 % bar.

**Resolved, three launch counts.** PROBE-00's 415 (215 single / 200 MIRV), the composer's 850 (524 engagements) and
the spine's 816 differ by grouping. PROBE-00 joins tests whose starts fall within 2 h on any lineages; the spine joins
only episodes that share a joined session and never counts `meta.hosts` as targets (it lists hosts where the sha exists
today: 227 of 806 false MIRVs). DIRECTION defines a MIRV as "one operator engagement": a shared session observes that,
proximity guesses it. Session grouping is default; `engagement_union: time_window` (with the cartographer's
`engagement_max_span_h` 12, since uncapped proximity chains to 30 h) reproduces PROBE-00 as a control arm. Slice 1
shows the groupings side by side for Derek's Verdict.

## 3. World layout (`compile/layout.py` → `world.json`)

**Data:** from `repos.json`: `id, kind, hosts, paths, first_ts, third_party, foreign_org, worktree_records, members,
remotes`; from GitHub `repo_born`: `kb`, `fork`, `created_at`; from events per tile (lineage, host, depth-2 path):
first-touch frame and weight `w` = Σ births (+ updates when merged) + Σ commit `files / len(files)`. Names serve joins
only and reach the page only under `labels`. A counts-only `tiles.ndjson` (tip-tree file count per depth-2 directory)
is a contract request that replaces `w`.

1. **Grid:** axial, pointy-top; `cells = clamp(1 + floor(tile_area_k · log10(1 + w)), 1, 7)`, about 7,500 cells.
   **Resolved:** the spine's uncapped `1 + floor(log2(1 + w))` gives the largest proxy 16 cells; the cap stops busy
   directories dominating while `w` is a proxy.
2. **Regions** (lineage × host): a blob grown in spiral order from its seed; tiles take consecutive runs **sorted by
   first touch**, oldest at the core. Exploration grows outward; the final map reads as tree rings. One-hex coast gap.
3. **Continents:** regions by `(first_ts, id)`, first-fit spiral disc packing (`R_reg = ceil(sqrt(cells / 2.6)) + 1`);
   a bridged region anchors `0.6 · R_cont` toward its partner, so bridges stay short. Ruins seed on the outer ring.
4. **Slots:** omen-e and omen-c share a 3-hex strait; omen-linux lies across an 8-hex sea, so the migration is a bridge
   lighting over open water while the west dims; AM4 and FX99 off the Linux coast; GitHub a band of islands in the
   north sea; `cloud` has no land. Terrain tint 4 to 6 L points above the background.
5. **Bridges:** quadratic arcs, dark until both ends exist, then a hairline at the lower activity of the two.
6. **Archipelago:** each GitHub repository an island (`clamp(1 + floor(log10(1 + kb)), 1, 5)` cells) rising at
   `created_at`, mostly in era A; when the local region appears, a harbour lands on its coast. Forks grey.
7. **Spurs** per `worktree` event (94 on omen-linux) at angle `sha1(ref)`, length `2 + log2(1 + commits)`, decaying
   to stubs; MIRV warheads aim at them. Branches are rim notches.
8. **Seat beacons** on omen-linux, AM4, FX99. **HQ** ring at the surface with most session activity over 7 story
   days, 2 s glide: in the ChatGPT years it broadcasts into the void where omen-c will rise; it crosses to omen-linux
   on 2026-09-27, uncaptioned.
9. **Third party:** grey hatch; upstream history never replayed (16,000 commits dated 2023 to 2025 would light ground
   Derek never touched); the region appears whole, explored, at clone time. `third_party: hidden` re-packs.

Viewport 1,360 × 896: 6 px hexes at the final pull-back, 12 to 20 px mid era C.

## 4. Timeline compilation

`python -I compile/build.py --params laps/LAP-NN/params.json` writes `world.json`, `timeline.bin` (deltas,
checkpoints, series, ~6 MB), `launches.json` and `nations.json` (CONTRACT §8 plus render keyframes), `camera.f32`,
`audio.wav`, `kw-data.js` (`window.KW_DATA` as base64 typed arrays, loads from `file://`) and `receipt.json` (input,
params and output hashes; section 2 recomputed).

### 4.1 Clock

Exact per calendar unit: A a year = 4 s from 2011-08-01; B a month = 2.5 s from 2023-04-01; C a UTC day = 2.4 s from
2026-03-01 to the snapshot. Story 668.2 s (46.7 + 87.5 + 534.1), plus `intro_s` 2 and `coda_s` 18: **688.2 s,
20,646 frames**. An event lands on `f = floor(30 · T(ts))`. **Glides:** each boundary gets `glide_s` = 3 s with
`ln r(u) = ln r0 + (ln r1 − ln r0)(3u² − 2u³)`, integrated at 1 ms and centred so the boundary date keeps its output
second; A→B slows story time 7.5×, B→C 29.2×, and nothing jerks. Per frame: `tau[f]` and `rate_label[f]`.

### 4.2 Launches (`launches.py`)

1. **Episodes:** per own lineage, a commit gap over `episode_gap_h` closes one.
2. **Session join by activity:** sessions run long (p90 20 h, max 489 h), so a span join chains weeks; a session joins
   when one of its `chat_msg` minute buckets on the lineage falls within the window ± `session_overlap_min`.
3. **Nation. Resolved:** CONTRACT §8 reads "dominant class of the commits, else the session class". Codex writes no
   trailer, so its commits read `human` and it gets 2 tests. Spine and composer independently reach the same fix:
   dominant **non-human** commit class, else the session class with most joined messages, else human (Codex 60 to 65
   launches). Default `nation_rule: session_over_human`; `commit_dominant` is the contract text. The industry's curve
   depends on it, so the owner records a §8 revision note.
4. **Yield** per §8; seats from HEARTH `backend`; a host counts only if its copy existed before the episode ended.
   Commits over `yield_cap_lines_per_commit` (20,000) count at the cap, flagged in the receipt, so imports do not read
   as megatons. Under `min_yield` it stays infrastructure.
5. **Shape:** targets = distinct lineages plus worktree births in the window; ≥ `mirv_min_targets` is a MIRV.
   **Unified:** band ≥ `unify_min_band` on a lineage that took ≥ 2 warheads within `unify_window_h`, with at least half
   the MIRV's lines.
6. **Band:** `clamp(floor(log10(max(lines, 1))), 1, 6)` by `yield_bands`; `yield_score: composite` adds 0.5 log10
   files + 0.25 integrations + 0.1 moving pieces.
7. **Non-git (v1.4):** a day with ≥ `min_yield.files` births or updates opens one; days within `episode_gap_days`
   merge; score `log10(files) + 0.5 log10(bytes / 1e4)`. ChatGPT-inferred nations carry `nation_inferred`.
8. **Nations:** canonicalised generations (`opus-4-7` = `opus-4.7`, seats mapped to models). **Resolved, legend
   entry:** a row enters at a class's **first event** (spine, composer), not its first test (cartographer), because
   DIRECTION names the first ChatGPT conversation as an entry and ChatGPT never tests: a row with 0 tests is the
   research program stated honestly. The tone first sounds at the first test; chips enter at their first test
   (`generation_entry`), which drops strays. `local_backends` keeps `gcp-gemini` out of the ember nation. Local seats
   and OpenCode never commit, so their rows show participations.

Per launch: `f_launch`, `f_split`, per warhead `f_land` (real order compressed into `warhead_spread_s`) and target
cell, consolidated cells for unified, `pan` from the target's screen x under `camera.f32`.

### 4.3 Infrastructure fields

A commit touches each tile in `files` at `1 + log10(1 + lines / nfiles)`, on each host where the lineage existed at
that time; a birth or update at `1 + log10(1 + n)`; a joined chat bucket at `0.25 · log2(1 + n)`; branches and
worktrees touch spurs.

1. **Deltas:** one record per (frame, tile, class group), indexed by `delta_start[f]`: frame `f` is an O(1) slice
   (the sparse index RaidUI lacks).
2. **Activity:** `A(f) = A(c)·D(c, f) + Σ w_i·D(f_i, f)`, `D(a, b) = 2^(−(tau[b] − tau[a]) / fog_half_life_days)`;
   exact, so checkpoints every 900 frames (2.2 MB) bound replay. Explored is `f ≥ tile_first_frame[k]`. A 0.3 s attack
   ramp stops pops. The half-life is 0.33 output s in era A and 72 s in era C.
3. **Series** per frame: tallies per nation and surface, chatter per class, commit rate, offloads per seat, HQ host,
   beams: one source for border, band, hum and static.

### 4.4 Camera (`camera.f32`)

The box of tiles revealed by `f + camera_lookahead_s` (6 s) plus risen islands and HQ; scale `min(Wv/bw, Hv/bh)(1 −
2·camera_pad)` capped at `max_hex_px` 40; from era C scale only decreases; a forward-backward smoother (`camera_tau_s`
4) on centre and log-scale, clamped to keep every revealed tile in. The coda frames the whole world. **Resolved:**
this replaces the spine's spring; both are compile-time, but a causal spring lets the Linux continent rise off screen.

## 5. How the two evolutions read (no caption anywhere)

**Era A, 2 to 48.7 s.** The year ticker counts; GitHub islands rise with faint bells (`repo_born` without a test, −12
dB, no bloom); non-git episodes from 2020-12 give the first white or hollow flashes. The loneliness is the length.

**Era B, 48.7 to 136.2 s, radio before territory.** ChatGPT enters 2023-04-17: a green row at 0 tests, rings, static.
Claude's row enters 2025-10 on its first session. Two lonely human tests with bells, twenty months apart; then
2026-01, twelve launches in under a second with Claude's first test (coral, E4) among them; a silent February.

**Era C, 136.2 to 670.2 s, the cascade.** March fills the Windows continents under the loudest hum. April's tests run
under a flat upper band (no chat source). Claude generations enter as shades. Codex's row 06-29, first tone 07-02;
automation 07-03; local seats participate from 07-18 (sparks, 0 tests); Opus 5 07-29. MIRVs grow from July; August is
the chatter peak and the unification month. 09-27 OpenCode enters and HQ crosses the sea; the west dims. 10-03 the
offload storm roars. Late on, the count holds while shapes and the mix of nations change: the operator's curve read
against the industry's.

**Coda, 18 s.** Blooms decay, hum and static fade (3 s); camera to the whole world, tallies settle (4 s); silence
(2 s); the tally card, one row per nation in entry order: first test, tests, yield, singles / MIRVs / unified, tiles
explored against laid out (8 s); black (1 s).

## 6. Audio synthesis (`audio.py`)

Every onset is sample `f · 1,600`. Seeded PCG32 noise; WAV length exactly F × 1,600; hash in the receipt; soft-knee
limiter at −1 dBFS.

| Band | Lines | Tone | Gain | Bloom life | Flash radius (screen px, any zoom) |
|---|---|---|---|---|---|
| 1 | 10–99 | 0.12 s | −27 dB | 0.40 s | 6 |
| 2 | 100–999 | 0.19 s | −24 dB | 0.60 s | 10 |
| 3 | 1k–10k | 0.31 s | −21 dB | 0.90 s | 15 |
| 4 | 10k–100k | 0.49 s | −18 dB | 1.35 s | 23 |
| 5 | 100k–1M | 0.79 s | −15 dB | 2.0 s | 35 |
| 6 | ≥ 1M | 1.26 s | −12 dB + sub-octave | 3.0 s | 52 |

- **Pitch:** human A3, Claude E4, Codex G4, OpenCode B4, local C3, automation D4; ChatGPT-inferred tests F4 through a
  band-pass, so they sound like radio. Generation `g` adds partial `3 + g` at −24 dB: timbre, never pitch.
- **Shape:** a MIRV sounds at departure (summed band, −6 dB), then a 60 ms pip an octave up per warhead at `f_land`;
  a unified launch an octave down at 1.5× length.
- **Firsts:** a lineage's first test rings a low bell (partials 1, 2.76, 5.40, 8.93 on C2, 3 s); a nation's first
  test doubles its tone at the octave with a 2 s tail.
- **Pan** `0.6 · (2x/W − 1)` from the target's screen x.
- **Collapse:** onsets in a sliding 1 s window above `collapse_events_per_s` group into 125 ms bins, each a chord of
  distinct nation pitches (≤ 4 voices); four collapsed bins in a row become a 16 Hz roll on the dominant pitch; 20 %
  hysteresis.
- **Hum** 55 + 110 Hz at `−36 + 6·log10(1 + commits/s)` dBFS, ceiling −24. **Static** band-passed per class
  (ChatGPT 1.2 kHz, Claude 2.0, Codex 2.8, OpenCode 3.6, local 0.8) by log message rate, ceiling −18: the ChatGPT
  years are static by construction. **Offloads** are 1 ms clicks below 40/s and 0.8 kHz band noise above.

**Alignment proof, every export:** a white frame at `f_p` and a 1 ms click at sample `f_p · 1,600`; `ffprobe` checks
duration F / 30 and F × 1,600 samples, then the decoded white frame against the click peak. Pass under 1 ms once the
MP4 edit list removes AAC's 1,024-sample priming.

## 7. Renderer (`render/index.html`)

Modules, building on RaidUI: `data.js` (decode `KW_DATA`, refuse a wrong `version`); `state.js` from
`render-state.js` (`buildState(f, out)`: checkpoint plus delta replay into preallocated scratch, live launches by
binary search); `layers.js` from `registry.js` (`{id, zIndex, render}`, save/restore, per-layer try/catch into the
frame receipt); `palette.js` (OKLCH by nation, generation shades at 0.06 L steps); `decay.js` from the trails-2s
template; `launch.js` (new); `border.js` from the Transport readout; `clock.js` from `playback-controller.js`
(preview 0.25× to 64×; export calls `renderFrame(f)`). Purity: no `Date`, no `Math.random` (mulberry32 by
`launch_id`), no rAF under `?export=1`, inlined WOFF2 behind `document.fonts.ready`, activity quantised to 32 levels,
land as one `Path2D` per colour bucket (~300 fills).

**Draw order:** 0 background `#07090e`, sea lattice 4 %; 1 explored land, terrain tint, 1 px coasts; 2 ruins hatch;
3 activity field (last conductor's hue, ≤ L 0.55); 4 bridges, harbours, spurs, notches; 5 radio (comms beams HQ →
region as the countdown, ChatGPT rings, one offload arc per seat per frame); 6 launches in `lighter` (MIRV beam splits
at 60 % of its path, warheads arc to spurs and bloom by share of lines; unified: converging lines 0.5 s, then a bloom
one band larger; inferred: reduced chroma, hollow core, open ring; per-region merge under collapse; total bloom
luminance capped so 15 blooms cannot white out); 7 HQ and beacons; 8 border; 9 coda card.

**Border:** top 64 px, the ticker (JetBrains Mono 30 px; `2017 · 12`, `2025 · 11`, `2026 · 09 · 27` over a 24-hour
hairline where a story hour is 0.1 s) with the rate always beside it. Right 320 px, the legend: one 34 px row per
nation sliding in at its entry frame: swatch, name, generation chips (a new chip named for 3 s in the border, never at
the flash), tests in 28 px tabular figures, cumulative yield, a 14 px capacity line (commits · files). Left 240 px,
surface tallies. Bottom 120 px, the mirrored radio band over 20 s: chatter above by class, commits below in warm grey,
offloads an ember hairline, era ticks. No launches on the band: band is radio and capacity, map is tests.

## 8. Export pipeline and estimate

Measured (spine, spike page, 1080p, per frame): `page.screenshot` 250 ms; **CDP `Page.captureScreenshot` PNG,
`optimizeForSpeed`, 66.7 ms**; parallel one Chromium per worker: **7.8 ms effective at K = 12**. Piped PNG to libx264
medium crf 18: 55 fps per encoder. Two browsers, opposite orders: identical PNG sha256, 6 of 6.

1. 60 s segments; `export_workers` (10) each capture over CDP and pipe into their own `ffmpeg -f image2pipe -c:v png
   -i - -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -g 60`. No frame touches disk.
2. Per-frame sha256; resume by segment. 3. Concat with `-c copy`; mux the WAV as AAC 256 kb/s; lengths checked.
4. Receipt: 30 frames re-rendered elsewhere in another order match; compile twice is byte-identical; `buildState`
   under Node matches a brute-force Python sum at three frames; the sync probe passes.

**Estimate: about 9 minutes wall** for the full piece: 20,646 × 7.8 ms = 2.7 min floor; × 1.5 encoder sharing; × 2
raster margin for real content = 8.0; plus warm-up, concat, mux. The cut: about 1.2 min. Workers run under `nice`
beside bench27. **Ladder** if slice 3 is slower, each a recorded switch: 16 workers, CDP JPEG q 95 (hash decoded
RGBA), `fps: 24` (2,000 samples per frame), `scale: 0.833`; raw `getImageData` → rawvideo is an optional spike 02.
**4K:** `scale: 2` on the same `render(f)`; unmeasured, about 31 ms at K = 12 with encode co-bottleneck: 20 to 30 min.

**The 90-second cut:** `m = 668.2 / (90 − 1 − 6) = 8.05`. Story state compresses by `m`; envelopes scale by
`m^(−1/2)` (0.35×). **Resolved:** the spine divided envelopes by `m`, which makes a band-1 bloom 1.5 frames and a
tone a 15 ms click; the square root keeps a flash a flash, and the extra overlap at 37 launches/s is what collapse and
the per-region merge exist for. Audio is re-synthesised, not resampled. The ticker reads `1 day = 0.30 s · ×8.05`.

## 9. Parameter table (`compile/params.json`, one key each, hashed into every output)

| Key | Default | Arms |
|---|---|---|
| `fog_half_life_days` | 30 | days |
| `hue_axis` / `geography` | actor / surfaces | surface / lineages |
| `collapse_events_per_s`, `collapse_mode` | 8, chord_then_roll | roll, chord |
| `camera` | fit_known | fixed_world |
| `third_party` | ruins | hidden, shown |
| `era_rates` | A 4 s/yr, B 2.5 s/mo, C 2.4 s/day | per era |
| `era_bounds` | B 2023-04-01, C 2026-03-01 | C 2026-01-15 (+104 s) |
| `cut_90s_multiple`, `cut_envelope_scale` | auto (8.05), sqrt | number; linear |
| `episode_gap_h`, `episode_gap_days` | 2, 1 | hours, days |
| `session_overlap_min`, `session_join` | 30, activity | span |
| `min_yield` | lines 50 or files 3 | |
| `yield_bands`, `yield_score`, `yield_cap_lines_per_commit` | log10 1–6, lines, 20,000 | edges; composite |
| `engagement_union`, `engagement_max_span_h` | session, 12 | session_or_nation, time_window |
| `mirv_min_targets`, `unify_window_h`, `unify_min_band` | 2, 24, 4 | |
| `nation_rule` | session_over_human | commit_dominant |
| `nation_entry`, `test_credit`, `inferred_nation` | first_event, conductor, credit | first_test; with participants; human |
| `generation_shades`, `generation_granularity`, `generation_entry` | true, major, first_test | one hue; minor/off; first_seen |
| `local_backends` | omen-*, am4-*, fx99-* | allowlist |
| `glide_s`, `intro_s`, `coda_s`, `warhead_spread_s` | 3, 2, 18, 0.4 | 0 = hard cut |
| `tile_area_k`, `coast_gap` | 2, 1 | |
| `camera_pad`, `camera_tau_s`, `camera_lookahead_s`, `zoom_in_allowed`, `max_hex_px` | 0.12, 4, 6, false, 40 | |
| `labels`, `offload_sound` | off, crackle | on; hiss |
| `fps`, `scale`, `export_workers`, `probe` | 30, 1, 10, on | export only |

Every DIRECTION.md initial parameter and every CONTRACT §8 parameter is one key above.

## 10. Thin-slice build order (each a Lap with a Receipt)

1. **Launch strip:** `launches.py`, `nations.json`, receipt; a strip PNG (time × band, nation colour, shapes marked)
   with the `engagement_union` arms side by side. Derek judges the event model before any map.
2. **Clock and sync:** schedule with glides, ticker-only `render(f)`, 10 s through the segment pipeline with the sync
   probe, the 90 s cut rendered twice with equal hashes.
3. **Thin slice:** black map, regions as dots, blooms with tones, bells and the growing legend, hum and static; a
   timed full export. The grammar end to end and the real budget.
4. **Atlas and fields:** layout and one final-frame still for a legibility Verdict; fog, checkpoints, Node vs Python.
5. **Shapes:** MIRV and unified, their sounds, hollow cores.
6. **Radio and camera:** beams, rings, sparks, band, lookahead camera, HQ crossing, bridges, harbours, spurs, ruins.
7. **Cut and coda;** then Laps one key each (`nation_rule`, `yield_bands`, `engagement_union`, `fog_half_life_days`).

## 11. Open risks

1. Era A is thin: no git test before 2023-11; early flashes wait on `file_update` in the merged corpus. Islands and
   birth bells carry the void until then.
2. Bands 5 and 6 (25 launches, one of 2.96M lines) likely hold imports; the lines cap is a first answer for slice 1.
3. `nation_rule` departs from CONTRACT §8 text; without it Codex shows 2 tests.
4. Launch counts diverge by grouping (415 / 816 / 850) until Derek's Verdict on the strip.
5. 11,164 commits lack numstat; their yield is understated.
6. Commits carry no worktree; MIRV targets rely on worktree births until depth-3 worktree cwd or `meta.records`.
7. OpenCode never appears in a launch window (0 tests); local seats show participations.
8. Up to 8 launches share a frame; staggering would be a lie, so the merge must read as one.
9. Tile area rests on a proxy until `tiles.ndjson`.
10. The 2026-04 chat hole may read as a bug.
11. The estimate rests on the spike page until slice 3; bench27 load stretches it.
12. Hashes hold per Chromium build (1248); AAC priming breaks sync without the probe.
13. The band table and `m^(−1/2)` are taste calls for a Lap.

## 12. Fable review and amendments (2026-10-09, binding for the builder)

**Verdict: accepted.** Spine and grafts stand as written in sections 0 to 11. Derek's three calls are all present
(payload model; shape single → MIRV → unified; two evolutions with a growing legend) and nothing flashes per commit.
The reconciliation of the three launch counts (section 2) is the right one: a shared session observes "one operator
engagement", proximity guesses it; PROBE-00's rule stays as the `time_window` control arm and slice 1 shows both.

Amendments from inputs the panel did not have (they landed while it ran):

1. **Relations drive the geography.** `corpus/merged/relations.json` (task 1b: the 12 constellation.yaml files and
   the JEPA export, joined to lineages; SURVEY.md §4c) replaces first-fit-by-`first_ts` as the primary packing rule in
   section 3.3: regions of one constellation pack into one disc with the `primary` repo at the centre, discs order by
   the constellation's earliest `first_ts`; inside a disc, by `first_ts`. `depends_on`, `parent`, `consumes`,
   `extracted_from`, `replaces` edges pull neighbours adjacent; cross-constellation edges and `bridges_traffic_to`,
   `leases_hardware_to`, `control_plane_for`, `describes_topology_for` draw bridges beside the lineage-across-hosts
   bridges. Unjoined lineages fall back to the section 3.3 rule. `yield.integrations` adds the lineage's
   `integrations` counts from relations.json (cross-repo contracts, data sources, depends in/out) to the episode's
   touched lineages, hosts and seats. Bridges keyed on relations light at `since` (the later endpoint's first commit).
2. **ChatGPT links name the pre-git nation.** `corpus/merged/chatgpt_links.json` (task 1b part 2): a conversation
   that names the project (`D:/work/<name>` → lineage) and is active within ± 2 h → `chatgpt`, `nation_inferred:
   "path+time"`; time-only → `"time"`; both hollow-core per section 7. The `activity_calendar` series backs the era-B
   static where per-minute buckets are thin.
3. **Era A is no longer thin.** The v1.4 corpus (merged 2026-10-09, 212,498 events) carries `file_update` on every
   host; non-git episodes (section 4.2.7) compile on the current merge, not the 13:00Z snapshot. Recompute section 2's
   table in the slice-1 receipt.
4. **`nation_rule: session_over_human` is contract text** (CONTRACT.md v1.5, §8), with `commit_dominant` as the arm;
   legend rows enter at a class's first event, chips at a generation's first test.
5. **Build order:** STRATEGY §10 slices 1 to 3 are task 3 (`known-world-plan/3-thin-slice.md`); the builder stops
   after slice 3 with receipts so Derek judges the launch strip and hears the grammar before the atlas. Slices 4 to 7
   follow as task 3b; laps as task 4. Commits by explicit path only (another worker holds `collect/`).
6. **Honesty guards kept:** no staggering of same-frame launches; the 2026-04 chat hole stays visible (a flat band),
   with one line in the tally card's footer naming the gap; third-party upstream history never replays.
