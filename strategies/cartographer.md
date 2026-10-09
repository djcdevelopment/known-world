# Strategy: cartographer (Known World, 2026-10-09)

Angle: lay the world out first, and lay it out so it can be read. The world is computed once from the final corpus, it
never moves while the film runs, and it grows outward from its oldest ground. Everything else (fog, launches, sound,
the border) is drawn as state on top of that fixed map. Every number below comes from `corpus/merged/` (prototype
counts run against `events.ndjson` and `repos.json` for this strategy) or from `spikes/01-canvas-budget/RESULT.md`.

## 0. What the corpus gives the map

| Measure (own work unless stated) | Value |
|---|---|
| Lineages in `repos.json` | 201: 110 own git, 11 third-party git, 78 `dir:` lineages, 2 GitHub-only |
| Multi-host lineages (bridges) | 17 two-host, 1 three-host (continuity: linux, am4, fx99) |
| Tile instances (lineage × host × depth-2 path) | 4,387: omen-c 1,688, omen-e 1,568, omen-linux 811, am4 305, fx99 15 |
| Distinct tiles | 3,894, of which 3,023 own and 871 third-party |
| Tiles per lineage | median 8; the largest five hold 492, 233, 196, 176, 114 |
| Worktrees / branches | 204 (107 on commandcenter) / 790 |
| Own commits | 9,271, all but 6 in 2026 (peak day 2026-03-17: 821) |
| Third-party commits | about 22,800, mostly 2023 to 2026 upstream history |
| Tile reveals per month, 2026-03 to 2026-10 | 360, 295, 316, 174, 356, 427, 744, 284 (37 before 2025-11) |

Two findings shape the layout. First, third-party history must not be replayed: about 16,000 upstream commits dated
2023 to 2025 would light grey ground in era B that Derek never touched then. Second, era A is almost empty of own work
(one own commit in 2017, 45 commits in own lineages from 2018 to 2022 classed `third_party` by actor, probably
identity-map gaps). Era A's 46 seconds belong to the GitHub archipelago rising from `created_at` dates.

## 1. World layout

### 1.1 Data the layout needs

From `repos.json` per lineage: `id`, `kind`, `hosts`, `paths` (per host), `first_ts`, `third_party`, `foreign_org`,
`worktree_records`, `members`, `remotes` (a GitHub remote marks a harbour). From the GitHub `repo_born` events:
`magnitude.kb` (island size), `meta.fork`, `meta.pushed`. From events: the tile key `(repo, host, path)` where host
comes from `meta.hosts` on commits (a commit on two hosts touches the tile in both regions) and from `host` on
`file_birth`; the tile's first-touch time; and a tile weight `w` that stands in for file count.

`w` per tile = sum of `file_birth.magnitude.n` + sum over commits of `magnitude.files / len(files)` (a commit's file
count apportioned across the depth-2 directories it touched). Measured distribution: p50 2, p90 26, top 37,041 (a
model or vendor directory). Data request for collection v1.4: a tip-tree file count per depth-2 directory, read with
`cat-file` tree walks and emitted as counts only; the proxy holds until then. Second request: Merge drops which
worktree record a commit came from; keep `meta.records` (hashed `repo_local` list) so MIRV warheads can target
worktree spurs exactly. Until then warheads target the distinct depth-2 tiles and hosts of the episode.

Names are read for joins only and never drawn: no region label appears on screen (privacy, and the honesty rule).

### 1.2 Grid and area

Axial hex coordinates `(q, r)`, pointy-top. A tile occupies `cells = clamp(1 + floor(tile_area_k · log10(1 + w)), 1,
7)` hexes with `tile_area_k = 2`: w=1 gives 1 cell, w=10 gives 3, w=100 gives 5, w≥1,000 gives 7 (a full flower).
The measured weights give about 1.7 cells per tile, about 7,500 cells for 4,387 tile instances.

### 1.3 Regions (repos and `dir:` lineages, one per lineage × host)

Each region is a contiguous blob grown in **spiral order from its seed**, and tiles take consecutive runs of that
spiral **sorted by first-touch time**. So a region's oldest tiles sit at its core and its newest at its rim: when a
region is explored it visibly grows outward, and the final map reads as tree rings. A one-hex coast gap separates
regions, so each one is a legible island of colour inside its continent.

Region footprint radius `R_reg = ceil(sqrt(cells / 2.6)) + 1` (in hexes). Third-party regions (the ruins) take a seed
on the outer ring of their continent, so foreign ground never sits in the core.

### 1.4 Continents (surfaces) by first-fit spiral disc packing

For each surface, regions are sorted by `(first_ts, id)` and placed one at a time: the seed search walks a hex spiral
outward from an anchor and takes the first position where the region's disc does not overlap a placed disc.
The anchor is the continent centre, except for regions with a bridge: their anchor is offset `0.6 · R_cont` toward
the partner continent, so bridge-carrying regions (commandcenter, llama.cpp, continuity, the gallery lineages) settle
on the facing coasts and bridges stay short. Sorting by first touch puts the oldest regions near the centre. A new
corpus run that only adds later lineages appends them at the rim and leaves the earlier positions alone.

### 1.5 Macro geography (fixed slots, scaled by final area)

```
            [ GitHub archipelago: a loose band of islands, north sea ]
   omen-e  ~3-hex strait~  omen-c   ~~~~~ 8-hex sea ~~~~~   omen-linux
                                                             AM4 (SE), FX99 (NE)
```

The Windows continents sit west and touch across a narrow strait (E: and C: share 6 lineages). omen-linux sits east
across open sea, so the migration (2026-09) is a lit bridge crossing water while the west dims. AM4 and FX99 are
smaller landmasses off the Linux coast (305 and 15 tiles). Continent radius `R_cont` comes from its final cell count.
The terrain tint per surface is the only surface colour: a cold, low-chroma tint 4 to 6 OKLCH lightness points above
the background.

### 1.6 Lineage bridges, the archipelago, spurs, seats and HQ

- **Bridges**: one quadratic arc per pair of regions of a lineage, centroid to centroid, bowed northward by 0.15 of
  its length; dark until both regions have a revealed tile, then a thin line in the lineage's last-touch hue, whose
  brightness follows the lower activity of its two ends.
- **GitHub archipelago**: all 54 listed repositories are islands in the north sea band, `cells = clamp(1 +
  floor(log10(1 + kb)), 1, 5)`, ordered west to east by `created_at`. An island rises (fades in over 1 s of output
  time) at its `created_at`; this is all of era A. When the matching local region appears, a **harbour mark** (a small
  notch glyph) appears on that region's coast, and a hairline links it to the island. Forks are grey islands; the 2
  GitHub-only lineages stay islands without a harbour.
- **Worktree spurs**: each worktree is a 2-to-5-hex line out of its region's rim at angle `djb2(ref) mod 360`, length
  `2 + log2(1 + commits)`; lit while active and decaying to a dim stub. Commandcenter's 107 spurs make the fleet era a
  visible hedgehog. Branches are 1-hex rim notches (790 of them), never lines.
- **Seat beacons**: a small diamond at the capital of each continent that serves models (omen-linux B70 seats, AM4,
  FX99). Offload sparks end there.
- **Operator HQ**: a ring marker at the capital of the surface with the most chat minutes over the trailing 7 story
  days, eased between capitals over 3 s of output time. It sits at the future omen-c capital during the ChatGPT years
  (rings broadcast into a void where a continent will later rise) and moves to omen-linux during the migration. The
  move is shown without a caption.

### 1.7 Final size at 1080p

The map viewport inside the border is 1,420 × 904 px (left 200, right 300, top 56, bottom 120). The final world is
about 7,500 tile cells, about 2,500 coast-gap cells, the seas and the archipelago band: roughly 14,000 hex slots in the
bounding box. That gives a hex radius of about 6 px on the final pull-back (a texture with legible islands) and 12 to
20 px mid era C, when one or two continents are known.

## 2. Timeline compilation

### 2.1 Rate schedule (`timeline.json`)

A piecewise map `film(ts)` from story time to film seconds: era A 2011-08-25 to 2023-04-01 at 4 s per year (46.4 s),
era B to 2026-03-01 at 2.5 s per month (87.5 s), era C to 2026-10-09T12:45Z at 2.4 s per day (533 s). Total 667 s,
plus a 6 s settle and an 8 s tally card: 681 s, 20,430 frames at 30 fps. Era joins blend log-rate across 2 s of output
so the speed changes without a jerk. The ticker shows the date (UTC; lap switch `ticker_tz`) and the current rate
("1 day = 2.4 s").

### 2.2 Event to tile touches (infrastructure field)

Each commit (own, or own work inside a third-party lineage), `file_birth`, joined `chat_msg`, branch and worktree
event yields touches `(tile, t_film, weight, class)`: commit weight `1 + log2(1 + lines)/4` per touched depth-2 tile,
file_birth `0.5 + log10(1 + n)/2`, chat minute 0.15 (chat lights ground faintly; it does not build it). Third-party
upstream history yields no touches. A third-party region is revealed whole, as found land, at its clone time (its
earliest local `repo_born`, or the first own event in it).

**Decay**, pure and closed-form: per tile, the touch times `t_k` are sorted and the activity just after each touch is
precomputed, `A_k = A_{k-1} · 2^(-(t_k - t_{k-1})/h) + w_k`, with `h = fog_half_life_days` in story time converted per
era. At render time a binary search finds the last `k` with `t_k ≤ t`, then `A(t) = A_k · 2^(-(t - t_k)/h)`, with a
0.3 s output-time attack ramp so no tile pops. Fog state: unknown if `t < t_first`; explored lightness `L_floor`;
active lightness `L_floor + (1 - L_floor) · (1 - e^(-A/A0))`, hue from the class of the most recent touch.

**Readability (criterion 2)**: measured in 0.8-story-hour bins (one era C frame), at most 98 tiles are touched in a
frame and the p99 is 31, against 1,000+ explored tiles after 2026-04 and 3,000+ by 2026-09. With the attack ramp that
is under 10% of tiles changing per frame after the first fortnight of era C. Infrastructure peaks (342 own commits per
film-second on 2026-03-17; 730 chat ticks per film-second as August's mean) land only in tile brightness, the hum and
the radio band. Nothing is drawn per event.

### 2.3 Launches (`launches.json`, CONTRACT section 8)

Episodes per lineage close on a gap over `episode_gap_h`. Sessions join on cwd and an overlap of
`session_overlap_min`, and episodes below `min_yield` stay infrastructure. A prototype of this rule over the corpus
finds **1,001 episodes and 902 tests**: 1 in 2023-11, 1 in 2025-07, then 12, 56, 59, 93, 71, 171, 175, 209, 54 per
month from 2026-01 to 2026-10, with a peak of 15 tests on one story-day. In log10 lines the counts run 1, 79, 317, 370,
110, 21, 4 for bands 0 to 6.

**Shape**: an *engagement* joins tests on different lineages (or hosts) whose windows fall within `episode_gap_h` of
each other and that share a session class, capped at a 12-story-hour span so the busy months do not chain into one
blob (the uncapped prototype chained up to 30 h). An engagement with `≥ mirv_min_targets` targets is one MIRV with N
warheads. The prototype found 356 engagements, 186 of them on two or more lineages, first in 2026-03 (11), peaking
2026-07 (46). A unification is a test on a parent lineage with yield class ≥ 4 within `unify_window_h` after ≥ 2
warheads hit its worktrees or components.

**Peak launch density, designed for**: 14 tests (warheads) in the busiest film-second of era C (a 10-story-hour
window) and 4 engagements (beams) in that second; 6.3 per second over the peak day. 14 is above
`collapse_events_per_s = 8`, but the warheads of one MIRV share one beam, one tone and one landing burst, so the
collapse rule fires only when separate engagements overlap. In the 90 s cut (×7.6) that peak becomes about 30 beams
per second, and the collapse rule is what keeps the cut legible.

**Nation**: the contract orders commits, then session, then human. The prototype assigns 523 tests to Claude, 362 to
human, 14 to automation and only 3 to Codex, against 71,842 Codex events. Commits without a trailer read as human
even when a Codex session conducted them. Lap switch `nation_rule: commits_first | sessions_first`. Under
sessions_first, a test whose commits are human without a trailer takes the class of the joined session with the most
messages in its window. The industry curve depends on this switch.

**Yield class**: `class = clamp(floor(log10(lines)), 1, 6)` by default (`yield_basis: lines | composite`, composite =
lines + 40·files + 400·integrations + 100·moving pieces, the bands re-cut on quantiles). Episodes of more than 20,000
lines per commit are vendored imports or migration copies: lap switch `yield_cap_lines_per_commit`.

### 2.4 Nations (`nations.json`)

Ordered by first appearance, per class and per model generation (from commit trailers, session `models` and offload
`backend`/`model`). The hue is fixed per class (DIRECTION), and generations are OKLCH lightness and chroma steps of
that hue (`generation_shades`). ChatGPT enters at 2023-04 with zero tests: its entry is its first broadcast ring and it
has no tone.

### 2.5 Camera keyframes (`camera.json`)

Computed at compile time, one keyframe per output second, rendered by monotone cubic interpolation:

1. `bbox(t)` = bounds of tiles revealed by `t + lookahead` (lookahead 6 s of output), plus visible islands and the HQ.
   Because reveal is monotone, `bbox` only grows.
2. Target scale `s* = min(Wv/bw, Hv/bh) · (1 - 2·camera_pad)`, capped so a hex is ≤ 40 px.
3. **No zoom-in** after era C begins (`zoom_in_allowed: false`): `s(t) = min(s(t-1), s*(t))`. The camera only ever
   pulls back, so it cannot jitter.
4. A forward-backward exponential smoother (τ = 4 s) on centre and log-scale, then a clamp so the eased frame still
   holds every revealed tile.
5. The last keyframes frame the whole final world: the pull-back of the ending.

The lookahead means the camera starts making room before the Linux continent appears, so a new landmass never
arrives off screen. Before 2026, the frame holds the archipelago and the HQ point at the 40 px cap.

### 2.6 Field series (`fields.bin`)

One Float32 row per output frame of the full piece: commit rate (log-smoothed), chat message rate per class, offload
count per seat, cumulative tallies per surface and per nation. The 90 s cut samples it through the same time map.

## 3. Audio synthesis plan

Offline numpy, 48 kHz stereo, written as WAV, from the same `timeline.json` and `launches.json` (sample index =
`round(t_out · 48000)`), so the sound is aligned by construction.

- **Launch tone**: pitch by nation (human A3, Claude E4, Codex G4, OpenCode B4, local C3, automation D4). Sine plus
  two partials whose balance shifts per generation, so a generation changes the timbre, not the pitch. Length
  `0.18 · 1.45^class` s, gain `-24 + 3·class` dB, exponential release.
- **MIRV**: one rising 120 ms chirp for the beam, then N ticks an octave up, spread over 300 ms and panned to their
  warheads.
- **Unified**: the nation's tone with a fifth below, twice the length.
- **First test of a lineage**: a low bell (inharmonic partials 1, 2.76, 5.4).
- **First test of a nation**: the bell plus the nation's tone held 1.5 s.
- **Pan**: from the target's screen x under the camera, `pan = 0.8 · (x/W - 0.5)`. Sound follows the map.
- **Hum**: brown noise, low-passed at 90 Hz, gain following the log of the commit-rate field.
- **Static**: per-class band-passed noise (ChatGPT 2.5 kHz, Claude 1.6 kHz, Codex 3.2 kHz, OpenCode 2.0 kHz),
  amplitude following the log of that class's message rate. The ChatGPT years are static only.
- **Offload sparks**: soft clicks at local-model C5, density-limited to 20 per second.
- **Collapse**: onsets above `collapse_events_per_s` in a 1 s window merge into a roll (tremolo on the dominant
  nation's pitch) or a chord of the nations present.

## 4. Renderer structure

One HTML page, Canvas 2D, `render(t_out, profile)` pure: no `Date`, no `Math.random` (mulberry32 seeded by
`launch_id`), fonts inlined and awaited. The modules build on RaidUI:

| Module | From RaidUI | Role |
|---|---|---|
| `clock.js` | playback-controller `_tick` | preview playback; export calls `render(t)` directly |
| `state.js` | render-state pattern | (data, t) → scratch Float32Arrays: tile activity, camera, active launches |
| `index.js` | new | sorted Float64Array event indices with upper-bound search; per-tile touch slices |
| `layout.js` | new | Path2D per tile and region coast in world units, built once from `layout.json` |
| `palette.js` | palette.js OKLCH | class hues, generation shades, terrain tints |
| `layers/*.js` | registry compositor | ordered layers, save/restore, per-layer try/catch |
| `border.js` | Transport readout idea | ticker, legend, tallies, radio band in screen space |

**Draw order**:

1. Background `#07090e`.
2. Explored tiles in terrain tint, region coasts as 1 px strokes, ruins hatched grey (one CanvasPattern).
3. Active glow in the `lighter` composite.
4. Spurs, notches, bridges, harbours, beacons, HQ.
5. Comms: session beams HQ→region at an alpha set by messages per minute, ChatGPT rings, offload arcs aggregated per
   seat per frame (2,571 calls per story-day in October would be about 1,070 per film-second, so they are drawn as
   one arc per seat with brightness by log count).
6. Launches in `lighter`: beam, split point at 70% of the path, warheads, flash with a screen-space radius `6 ·
   1.6^(class-1)` px (constant on screen across zoom, as kilotons were), bloom `0.25 · 1.4^class` s of output time.
7. Border.
8. End card.

**The border**:

- **Top**: date ticker and rate.
- **Right**: nations in order of entry. Swatch, name (class and generation), tests and yield in 22 px tabular
  figures, capacity (commits, files) in 14 px beneath. A new nation's row slides in at its first test.
- **Left**: per-surface tallies (tiles explored, commits).
- **Bottom**: the radio band, stacked log-rate areas per class over a trailing 20 s window.

## 5. Export pipeline and time estimate

Sharding is trivial because `render(t)` is pure. 12 headless Chromium workers on the 24 cores each take a contiguous
frame range. Each draws, reads the canvas through `toDataURL('image/png')` (this skips the page compositor that
`page.screenshot` pays for), and pipes the frames into its own ffmpeg (libx264 crf 18, identical settings, closed
GOP). The segments are joined with the concat demuxer (`-c copy`) and the WAV is muxed last.

**Estimate**: the spike measured 271 ms per frame at 20,000 tiles through one page. Take 270 ms per worker frame and
assume 60% parallel efficiency over 12 workers: 20,430 × 0.27 / 7.2 = 766 s, about **13 minutes** for frames. Encode
runs inside the workers and is negligible (spike: 0.41 s per 60 frames). The 90 s cut (2,700 frames) adds about 2
minutes and audio about 1. Total about **17 minutes** against the 30 minute bar. The first lap measures 300 frames at
1, 6 and 12 workers before the estimate is relied on.

**4K path**: DPR 2 on the same render. The world is in world units and the border in CSS px, so nothing reflows.
About 4× capture cost, about 55 minutes with 12 workers, as an offline batch.

## 6. Parameters (every DIRECTION.md parameter is one switch in `compile/params.json`)

| Switch | Default | Values |
|---|---|---|
| `fog_half_life_days` | 30 | days (story time) |
| `hue_axis` | actor | actor, surface |
| `geography` | surfaces | surfaces (continents per host), lineages (one region per lineage, hosts as provinces) |
| `collapse_events_per_s` | 8 | onsets per output second |
| `camera` | fit_known | fit_known, fit_final, fixed |
| `third_party` | ruins | ruins, hidden, shown |
| `era_rates` | A 4/yr, B 2.5/mo, C 2.4/day | per era |
| `cut_90s_multiple` | auto (667 / 88 ≈ 7.6) | auto or a number |
| `episode_gap_h` | 2 | hours |
| `session_overlap_min` | 30 | minutes |
| `min_yield` | lines 50 or files 3 | |
| `yield_bands` | log10 | log10, quantile; `yield_basis` lines, composite |
| `mirv_min_targets` / `unify_window_h` / `generation_shades` | 2 / 24 / true | contract section 8 |
| Layout and camera extras | `tile_area_k` 2, `coast_gap` 1, `camera_pad` 0.08, `camera_tau_s` 4, `camera_lookahead_s` 6, `zoom_in_allowed` false, `max_hex_px` 40 | |
| Rule extras | `nation_rule` commits_first, `ticker_tz` UTC, `yield_cap_lines_per_commit` 20,000, `engagement_max_span_h` 12 | |

Output durations of blooms and tones are set in output seconds, so the 90 s cut keeps its flashes visible while the
story time compresses.

## 7. Thin-slice build order

1. **The atlas**: `compile/layout.py` over the real `repos.json` and tile keys produces `layout.json` and one still,
   `render(t_end)`, at 1080p. Verdict on legibility (islands distinct, bridges short, ruins peripheral) before any
   motion.
2. **Fog in motion**: the rate schedule, tile touch arrays, decay and camera keyframes. Export 2026-03 to 2026-05 (about
   220 s) at 1 worker and then 12. Measure ms per frame and the fraction of tiles changing per frame.
3. **Launches**: `launches.py` (episodes, engagements, shapes, nations) and the launch layer. Check the 902 / 356
   counts and the March-to-September cadence.
4. **Border**: ticker, legend, tallies, radio band.
5. **Audio**: `audio.py`, the mux, an alignment check (clap frames at known launches).
6. **Full export** and the 90 s cut. Hash three frames twice to confirm byte-identical output.
7. **Laps**, one switch at a time: `nation_rule`, `yield_bands`, `fog_half_life_days`, `era_rates`.

## 8. Open risks

See the structured output; the essentials: identity-map gaps empty era A; the Codex nation is undercounted under
commits_first; the file-count proxy for tile area; worktree attribution lost at merge; engagement chaining in the busy
months; vendored imports inflating yield; the export estimate is extrapolated from a single-page spike; GitHub private
repositories pending auth (the archipelago is the public view only); the 2026-04 chat hole leaves no session beams that
month.
