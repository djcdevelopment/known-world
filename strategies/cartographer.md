# Strategy: cartographer (Known World, 2026-10-09)

Angle: the world is laid out once from the final corpus, never moves, and grows outward from its oldest ground; fog,
launches, sound and the border are state drawn on that fixed map. Numbers come from prototype counts over
`corpus/merged/` run for this strategy, or from `spikes/01-canvas-budget/RESULT.md`.

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

Two findings shape the layout. Third-party history must not be replayed: about 16,000 upstream commits dated 2023
to 2025 would light ground Derek never touched then. And era A is nearly empty of own work (one own commit in 2017; 45
commits in own lineages 2018 to 2022 classed `third_party` by actor, likely identity-map gaps), so era A belongs to
the GitHub archipelago rising from `created_at` dates.

## 1. World layout

### 1.1 Data the layout needs

From `repos.json` per lineage: `id`, `kind`, `hosts`, `paths` (per host), `first_ts`, `third_party`, `foreign_org`,
`worktree_records`, `members`, `remotes` (a GitHub remote marks a harbour). From the GitHub `repo_born` events:
`magnitude.kb` (island size), `meta.fork`, `meta.pushed`. From events: the tile key `(repo, host, path)` where host
comes from `meta.hosts` on commits (a commit on two hosts touches the tile in both regions) and from `host` on
`file_birth`; the tile's first-touch time; and a tile weight `w` that stands in for file count.

`w` = sum of `file_birth.magnitude.n` + sum over commits of `magnitude.files / len(files)` (file count apportioned
over the depth-2 directories touched); measured p50 2, p90 26, max 37,041. Data requests for collection v1.4: a
tip-tree file count per depth-2 directory (`cat-file` tree walk, counts only) to replace the proxy; and `meta.records`
(hashed `repo_local` list) on merged commits, so MIRV warheads can target worktree spurs exactly (until then they
target the episode's distinct depth-2 tiles and hosts).

Names are read for joins only and never drawn: no region label appears on screen (privacy, and the honesty rule).

### 1.2 Grid and area

Axial hex coordinates `(q, r)`, pointy-top. A tile occupies `cells = clamp(1 + floor(tile_area_k · log10(1 + w)), 1,
7)` hexes with `tile_area_k = 2`: w=1 gives 1 cell, w=10 gives 3, w=100 gives 5, w≥1,000 gives 7 (a full flower).
The measured weights give about 1.7 cells per tile, about 7,500 cells for 4,387 tile instances.

### 1.3 Regions (repos and `dir:` lineages, one per lineage × host)

Each region is a contiguous blob grown in **spiral order from its seed**; tiles take consecutive runs of the spiral
**sorted by first-touch time**, so the oldest tiles are the core and the newest the rim. Exploration visibly grows a
region outward and the final map reads as tree rings. A one-hex coast gap keeps each region a legible island.

Region footprint radius `R_reg = ceil(sqrt(cells / 2.6)) + 1` (in hexes). Third-party regions (the ruins) take a seed
on the outer ring of their continent, so foreign ground never sits in the core.

### 1.4 Continents (surfaces) by first-fit spiral disc packing

Per surface, regions sorted by `(first_ts, id)` are placed in turn: a hex spiral walks outward from an anchor to the
first seed whose disc overlaps no placed disc. The anchor is the continent centre, or for a bridged region a point
`0.6 · R_cont` toward the partner continent, so bridged regions settle on facing coasts and bridges stay short. Old
regions sit central; a later corpus run that adds lineages appends them at the rim without moving earlier ones.

### 1.5 Macro geography (fixed slots, scaled by final area)

```
            [ GitHub archipelago: a loose band of islands, north sea ]
   omen-e  ~3-hex strait~  omen-c   ~~~~~ 8-hex sea ~~~~~   omen-linux
                                                             AM4 (SE), FX99 (NE)
```

The Windows continents share a strait (6 lineages span E: and C:); omen-linux lies across open sea, so the migration
is a bridge lighting over water while the west dims; AM4 (305 tiles) and FX99 (15) lie off the Linux coast. `R_cont`
follows final cell count. Surfaces carry only a low-chroma terrain tint 4 to 6 OKLCH lightness points above the
background.

### 1.6 Lineage bridges, the archipelago, spurs, seats and HQ

- **Bridges**: a quadratic arc per region pair of a lineage, bowed 0.15 of its length; dark until both ends are
  revealed, then a hairline in the last-touch hue at the lower activity of its two ends.
- **GitHub archipelago**: all 54 listed repositories are islands in the north band, `cells = clamp(1 + floor(log10(1
  + kb)), 1, 5)`, west to east by `created_at`, each rising at that date (most of era A). When the local region
  appears, a **harbour mark** lands on its coast with a hairline to the island. Forks are grey; the 2 GitHub-only
  lineages stay harbourless.
- **Worktree spurs**: a line off the rim at angle `djb2(ref) mod 360`, length `2 + log2(1 + commits)` hexes, lit
  while active, decaying to a stub; commandcenter's 107 make the fleet era a hedgehog. Branches (790) are rim notches.
- **Seat beacons**: a diamond at the capital of each model-serving continent (omen-linux, AM4, FX99); sparks end there.
- **Operator HQ**: a ring at the capital of the surface with the most chat minutes over the trailing 7 story days,
  eased over 3 s. Through the ChatGPT years it broadcasts rings into the void where omen-c will rise; it crosses to
  omen-linux with the migration, uncaptioned.

### 1.7 Final size at 1080p

The map viewport inside the border is 1,420 × 904 px (left 200, right 300, top 56, bottom 120). The final world is
about 7,500 tile cells, about 2,500 coast-gap cells, the seas and the archipelago band: roughly 14,000 hex slots in the
bounding box. That gives a hex radius of about 6 px on the final pull-back (a texture with legible islands) and 12 to
20 px mid era C, when one or two continents are known.

## 2. Timeline compilation

### 2.1 Rate schedule (`timeline.json`)

A piecewise map `film(ts)` from story time to film seconds: era A 2011-08-25 to 2023-04-01 at 4 s per year (46.4 s),
era B to 2026-03-01 at 2.5 s per month (87.5 s), era C to 2026-10-09T12:45Z at 2.4 s per day (533 s). Total 667 s,
plus a 6 s settle and an 8 s tally card: 681 s, 20,430 frames at 30 fps. Era joins blend log-rate over 2 s. The ticker
shows the date (UTC, `ticker_tz`) and the rate.

### 2.2 Event to tile touches (infrastructure field)

Own commits (including own work inside a third-party lineage), `file_birth`, `file_update` (contract v1.4), joined
`chat_msg`, branch and worktree events yield touches `(tile, t_film, weight, class)`: commit `1 + log2(1 + lines)/4`
per depth-2 tile, file_birth and file_update `0.5 + log10(1 + n)/2`, chat minute 0.15. Upstream history yields none;
a third-party region appears whole, as found land, at its clone time. A lineage's tiles touched only by births and
updates before its first commit are revealed by them, so pre-git ground exists before the repo does.

**Decay**, pure and closed-form: per tile, sorted touches `t_k` carry precomputed `A_k = A_{k-1} · 2^(-(t_k -
t_{k-1})/h) + w_k` (`h = fog_half_life_days`, story time). Render binary-searches the last `t_k ≤ t` and takes `A(t) =
A_k · 2^(-(t - t_k)/h)`, with a 0.3 s attack ramp so no tile pops. Fog state: unknown if `t < t_first`; explored lightness `L_floor`;
active lightness `L_floor + (1 - L_floor) · (1 - e^(-A/A0))`, hue from the class of the most recent touch.

**Readability**: in 0.8-story-hour bins (one era C frame) at most 98 tiles are touched per frame (p99 31), against
1,000+ explored tiles after 2026-04 and 3,000+ by 2026-09: under 10% changing per frame after era C's first fortnight.
Infrastructure peaks (342 own commits per film-second on 2026-03-17; August's 730 chat ticks per film-second) reach
only tile brightness, the hum and the radio band; nothing is drawn per event.

### 2.3 Launches (`launches.json`, CONTRACT section 8)

Episodes per lineage close on `episode_gap_h`; sessions join on cwd ± `session_overlap_min`; below `min_yield` stays
infrastructure. The reference counts are PROBE-00's (`laps/PROBE-00-launches/RESULT.md`): 1,047 tests, **415
launches**, 215 single and 200 MIRV, MIRVs from 2026-03, at parity in May, dominant July and August. My own prototype
(third-party-actor commits also dropped) gives 902 tests, 12 to 209 per month in 2026, peak 15 on one story-day.
**Non-git episodes** (v1.4): a day with ≥ `min_yield.files` births plus updates in a `dir:` region, or in a lineage
before its first commit, opens an episode (`episode_gap_days` 1); yield in files, bytes and moving pieces. These are
the early tests, and they land on `dir:` regions and on pre-git cores.

**Shape**: a launch joins tests on different lineages or hosts whose starts fall within `episode_gap_h`, capped at
`engagement_max_span_h` 12 so busy months do not chain (uncapped, my prototype chained to 30 h). `≥ mirv_min_targets`
targets make a MIRV of N warheads; a unification is a class ≥ 4 test on a parent lineage within `unify_window_h` of
≥ 2 warheads on its worktrees or components.

**Peak launch density, designed for**: 14 tests (warheads) and 4 launches (beams) in the busiest era C film-second
(10 story-hours); 6.3 tests per second across the peak day; mean one launch per 1.3 s. Warheads of a MIRV share a
beam, a tone and a landing burst, so `collapse_events_per_s = 8` fires only when launches overlap; in the 90 s cut
(×7.6) the peak is about 30 beams per second and collapse carries it.

**Nation**: under the contract order PROBE-00 gives human 165, Claude 236, Codex 10, automation 4 against 71,842
Codex events: trailerless commits read as human when a Codex session did the work. Lap switch `nation_rule:
commits_first | sessions_first` (trailerless commits take the class of the joined session with most messages); the
industry curve depends on it. Non-git episodes may carry `chatgpt` with `nation_inferred: true`: drawn with a hollow
flash core and an open ring, never a solid one (`inferred_nation_render: marked | human`).

**Yield class**: `class = clamp(floor(log10(lines)), 1, 6)` by default (`yield_basis: lines | composite`, composite =
lines + 40·files + 400·integrations + 100·moving pieces, the bands re-cut on quantiles). Episodes of more than 20,000
lines per commit are vendored imports or migration copies: lap switch `yield_cap_lines_per_commit`.

### 2.4 Nations (`nations.json`)

Ordered by first appearance, per class and per canonicalised generation (PROBE-00 counts about sixty in a year:
`opus-4-7` = `opus-4.7`, seats mapped to models). The border lists the eight classes; each class row grows a strip of
generation chips, one OKLCH shade step per generation, added at that generation's first test. No caption is drawn at
the flash; the legend carries identity. ChatGPT enters at 2023-04-17 with its first broadcast ring.

### 2.5 Camera keyframes (`camera.json`)

Computed at compile time, one keyframe per output second, rendered by monotone cubic interpolation:

1. `bbox(t)` = tiles revealed by `t + 6 s` lookahead, plus visible islands and HQ; reveal is monotone, so it only grows.
2. Target scale `s* = min(Wv/bw, Hv/bh) · (1 - 2·camera_pad)`, capped at 40 px per hex.
3. **No zoom-in** in era C (`zoom_in_allowed: false`): `s(t) = min(s(t-1), s*(t))`; a camera that only pulls back
   cannot jitter.
4. A forward-backward exponential smoother (τ = 4 s) on centre and log-scale, clamped to keep every revealed tile in.
5. The final keyframes frame the whole world: the ending's pull-back.

The lookahead makes room before the Linux continent rises, so no landmass arrives off screen.

### 2.6 Field series (`fields.bin`)

One Float32 row per output frame of the full piece: commit rate (log-smoothed), chat message rate per class, offload
count per seat, cumulative tallies per surface and per nation. The 90 s cut samples it through the same time map.

## 3. Audio synthesis plan

Offline numpy, 48 kHz stereo, written as WAV, from the same `timeline.json` and `launches.json` (sample index =
`round(t_out · 48000)`), so the sound is aligned by construction.

- **Launch tone**: pitch by nation (human A3, Claude E4, Codex G4, OpenCode B4, local C3, automation D4); sine plus two
  partials whose balance marks the generation; length `0.18 · 1.45^class` s, gain `-24 + 3·class` dB.
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
| `clock.js` | playback-controller `_tick` | preview; export calls `render(t)` directly |
| `state.js` | render-state | (data, t) → scratch Float32Arrays: activity, camera, live launches |
| `index.js` | new | sorted Float64Array indices, upper-bound search, per-tile touch slices |
| `layout.js` | new | Path2D per tile and coast in world units, built once |
| `palette.js` | palette.js | OKLCH class hues, generation shades, terrain tints |
| `layers/*.js` | registry | ordered layers, save/restore, per-layer try/catch |
| `border.js` | Transport readout | ticker, legend, tallies, radio band |

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

Identity-map gaps empty era A; Codex is undercounted under commits_first; tile area rests on a file-count proxy;
worktree attribution is lost at merge; engagements chain in busy months; vendored imports inflate yield; the export
estimate extrapolates a single-page spike; the archipelago is the public view until `gh` auth; the 2026-04 chat hole
leaves that month without beams.
