# Strategy: composer (time first), rev 2

Composer angle, Workflow 2, 2026-10-09, DIRECTION rev 2; supersedes the rev 1 file. Densities come from an
aggregate-only probe of `corpus/merged/events.ndjson` (counts only) running the CONTRACT §8 episode rule at the
DIRECTION defaults (third-party and `foreign_org` lineages excluded), mapped through the era schedule.

## 0. What the probe measured

| Measure | Value |
|---|---|
| Own lineages with commits / own depth-2 tiles / third-party tiles | 99 / 2,032 / 1,076 |
| Episodes / launches (at or above min yield) | 935 / 850 |
| Engagements (one beam; overlapping launches on distinct lineages) | 524; 170 MIRVs (2 to 10 warheads) |
| Lineages with a first test | 96 (3 in era B, 93 in era C) |
| Launches by era | A 0, B 14, C 836 |
| Yield bands, floor(log10 lines) 1 to 6 | 75 / 292 / 348 / 109 / 21 / 4 |
| Peak launches in any 1 film-second, full piece | 12 (2026-01-17..27 in era B; 12 warheads 2026-09-06 in C) |
| Film-seconds over 8 engagements / over 8 warheads, full piece | 0 / 5 |
| Peak launches per output second, 90 s cut (multiple 8.05, sliding) | 37 launches, 22 engagements; 41 cut-seconds over 8 |
| Max concurrent launch tones (lengths in section 2) | 12 |
| Commits per film-second, era C | mean 16.8, p90 39, p99 219, max 793 (2026-03-17) |
| Chat messages per film-second, B / C | B p90 246, max 2,337; C mean 868, p90 3,301, max 14,757 (2026-07-16) |
| Offload calls per film-second, era C | p90 6, p99 369, max 13,876 (2026-10-03) |
| Tiles touched per frame (frames with any touch) | p50 4, p99 22, max 72 of 3,108 (2.3 %) |

Peak designed for: **37 launches per output second** (the cut). The full piece never exceeds 12: the collapse rule
is the cut's normal regime and the full piece's safety.

Two findings shape the model. **(a) Nation:** the CONTRACT rule "dominant commit class, else session class" gives
Codex 2 tests, because Codex writes no co-author trailer and its commits read `human`. Letting a session's class
override a `human` commit class gives claude 502, human 274, codex 60, automation 14: the industry's curve appears.
That is my default (`nation_rule: session_over_human`), flagged for a CONTRACT v1.4 note. **(b) Era B carries the
first light:** two lonely tests (2023-11-03, film 64.4 s; 2025-07-07, 114.7 s), then twelve launches in 0.83 s
(2026-01-17 to 01-27), Claude's first test among them, then a silent February: Trinity, the second test, the
cascade's first breath.

## 1. Time: the compiled clock

**Clock.** Compile writes `clock.json`: a monotone piecewise map from output seconds `f` to story seconds `s`,
`{param_hash, fps: 30, intro_s, coda_s, segments: [{f0, f1, s0, s1, kind: "const"|"glide", r0, r1}], eras}`.
Rates are exact per calendar unit (A a year = 4 s from 2011-08-01, B a month = 2.5 s from 2023-04-01,
C a UTC day = 2.4 s from 2026-03-01 to the 12:45Z snapshot), so ticker boundaries land on fixed beats: A 46.66 s, B 87.48 s, C 534.08 s, story total 668.22 s; plus `intro_s` 2 (black, then the 2011-08-25
GitHub account's bell at 2.3 s) and `coda_s` 18: **688.2 s, 20,646 frames, 11 min 28 s**.

**Glides.** A→B slows story time 7.5× (0.0110 → 0.0822 output s per story day), B→C 29.2× (→ 2.4). A hard switch
jerks the band scroll and the decay, so each boundary gets a `glide_s` = 3 s glide, `ln r(u) = ln r0 + (ln r1 −
ln r0)·(3u² − 2u³)`, integrated at 1 ms and centred so the boundary date keeps its output second (drift in the
receipt). `glide_s: 0` is the hard-cut arm.

**Ticker (top centre).** JetBrains Mono 30 px; resolution follows the era: A `2017 · 12`, B `2025 · 11` (day dim),
C `2026 · 09 · 27` over a 24-hour hairline (a story hour is 0.1 s, so night drains show as a moving notch). Beside
it, always, the rate: `1 yr = 4 s`, mid-glide `1 mo = 0.71 s`, `1 day = 2.4 s`. At a boundary only the rate glyphs
brighten for 0.6 s; nothing else announces an era.

**The 90-second cut.** Same `clock.json` composed with a uniform multiple: `m = T_story / (90 − intro_cut − coda_cut)`
with `intro_cut` 1 s and `coda_cut` 6 s gives `m = 668.22 / 83 = 8.05` (`cut_90s_multiple: auto`; a number pins it).
Story state (fog, tallies, camera, band) follows story time and compresses by `m`; envelopes (bloom, tone, beam
flight) are output time scaled by `m^(−1/2)` (0.35×) so a tone stays a tone (`cut_envelope_scale: sqrt`). The ticker
appends the multiple: `1 day = 0.30 s · ×8.05`.

**Sync rule.** An event's visual onset is frame `k = ceil(30·f(s))` and its audio onset is sample `1600·k`
(48 kHz / 30 fps); picture and sound cannot disagree.

## 2. Sound

Offline numpy synthesis from `cues.json` and `series.f32` (section 7), 48 kHz stereo, WAV muxed as AAC 256 kb/s;
noise seeded by `sha1(param_hash + cue_id)`, so the WAV is byte-identical across runs and hashed in the receipt.

**Launch tones.** Pitch by nation as DIRECTION: human A3 220.00 Hz, Claude E4 329.63, Codex G4 392.00, OpenCode
B4 493.88, local C3 130.81, automation D4 293.66, third-party a low-passed thud. ChatGPT never tests (no cwd), so it
is static only. Voice: sine with 2nd and 3rd partials (−12, −20 dB), 5 ms attack, exponential decay. Generation is
timbre, not pitch: generation `g` adds partial `3 + g` at −24 dB, the audio twin of the shade swatch. By band `b`:

| Band b | Lines | Tone length (full) | Gain | Bloom duration | Flash radius (viewport px at fit scale) |
|---|---|---|---|---|---|
| 1 | 10–99 | 0.12 s | −27 dB | 0.40 s | 6 |
| 2 | 100–999 | 0.19 s | −24 dB | 0.60 s | 10 |
| 3 | 1k–10k | 0.31 s | −21 dB | 0.90 s | 15 |
| 4 | 10k–100k | 0.49 s | −18 dB | 1.35 s | 23 |
| 5 | 100k–1M | 0.79 s | −15 dB | 2.0 s | 35 |
| 6 | ≥ 1M | 1.26 s | −12 dB + sub-octave at −12 | 3.0 s | 52 |

(length `0.12·1.6^(b−1)`, bloom `0.4·1.5^(b−1)`, radius `6·1.54^(b−1)`; `yield_bands` swaps the edges.)

**Shapes in sound.** A single is one tone. A **MIRV** is one tone at the beam's departure (the bus, band of the summed
yield, −6 dB), then a 60 ms pip per warhead at its impact: staggered impacts make an arpeggio. A **unified** blip is
root, fifth and octave, one band longer: consolidation is consonant. Every cue pans by screen x to ±0.6.

**Bells.** A lineage's first test rings a low bell (partials 1, 2.76, 5.40, 8.93 over 110 Hz, 3 s decay) with the
slow bloom. A `repo_born` with no test yet (era A's five births, GitHub listings) rings it at −12 dB, no bloom.

**Infrastructure hum.** Detuned saws at 55 and 110.4 Hz, 400 Hz low-pass, level `−42 dB + 18 dB ·
log1p(c)/log1p(793)` with `c` the smoothed commits per output second (EMA τ 1.5 s), silent at zero; births and
branches lift a 220 Hz partial. Infrastructure never beeps.

**Chatter static.** Noise band-passed (Q 4) at a class centre (ChatGPT 1.2 kHz, Claude 2.0, Codex 2.8, OpenCode
3.6, local 0.8), level `−48 dB + 24 dB · log1p(r)/log1p(14,757)` per class (EMA τ 0.4 s). Offloads crackle as seeded
1 ms clicks below 40 per second and become 0.8 kHz band noise above, so the 13,876/s storm is a roar, not events.

**Collapse rule (`collapse_events_per_s`, 8).** Count launch onsets (singles, buses, warheads) in a sliding 1 s
output window. Above 8, onsets group into 125 ms bins, each one chord of its distinct nation pitches (≤ 4 voices,
highest yield first, energy-summed gain, longest length). Four or more consecutive collapsed bins become a **roll**:
a 16 Hz tremolo on the dominant nation's pitch, depth by onset count. Measured: 5 film-seconds chord in the full
piece; 41 cut-seconds collapse, peaking at 37/s (2026-07 to 09). Picture never collapses (37/s is 1.2 flashes a frame).

## 3. The radio band (bottom border)

A mirrored scrolling trace, 1,600 × 104 px, the last 20 output seconds. Above the axis, chatter as stacked areas by
class colour, height `log1p(r)/log1p(14,757)`; below, in warm grey, commits per second on the same log scale, with the
offload rate as an ember hairline. Columns come from `series.f32`, so band and static are the same numbers. Era
boundaries leave a scrolling 1 px tick. The April 2026 hole is a flat upper half over a pulsing lower half: radio
silence over a working industry. No launches on the band: band is radio and capacity, map is tests.

## 4. How density becomes the story, era by era

**Era A, 0 to 46.7 s: the void.** One own commit, five births, no launch, no radio: the year ticker counting and a
faint bell every nine seconds. The loneliness is the length.

**Era B, 46.7 to 134.1 s: radio before territory.** ChatGPT enters 2023-04 (film 48.0): a green row with 0 tests,
rings into the dark, static from 50 silent seconds up to p90 246 messages a second, generations as shades (2024-11,
2025-11, 2025-12). Two human tests with bells, twenty months apart. Then 2026-01: twelve launches in under a second,
Claude's first test inside them (coral, E4). The ear hears research for 85 s, then a burst.

**Era C, 134.1 to 668.2 s: the cascade.** March, the first month at a day per 2.4 s: 56 launches, the hum at its
peak (793 commits a second, 2026-03-17), the Windows continents fill. April: tests continue, the band goes flat (the
hole). May and June: Claude generations enter as shades (Opus 4.7 05-08 to Fable 5 06-09); median yield runs 728 to
3,331 lines a month. Codex enters 06-29 (cyan, G4), automation 07-03 (amber, D4), the first local seat 07-20 (ember,
C3, sparks, honestly 0 tests), Opus 5 07-25. July opens the MIRV era (46 MIRVs; 38 in August, 36 in September; the
largest 10 warheads on 09-23); August is the chatter peak. 09-27 OpenCode enters (violet, B4) with seven local models
in a day, HQ moves to omen-linux and the old continent dims. 10-03 the offload storm roars: the local seats answering.
Launches hold at p90 5 a second; the late story is the mix of nations and shapes, not the count.

**Ending (18 s coda).** The story clock stops at the snapshot. 0 to 3 s: last blooms decay; hum and static fade (τ
2 s). 3 to 7 s: the camera eases to the whole laid-out world; the unknown stays dark; tallies settle. 7 to 9 s:
silence. 9 to 17 s: the tally card, one row per nation in order of entry (first test, tests, yield, singles / MIRVs /
unified) over the totals. 17 to 18 s: black.

## 5. Compile: episodes, shapes, nations

**Episodes** (`compile/launches.py`, CONTRACT §8). Own commits per lineage by `ts`; a gap over `episode_gap_h`
closes an episode; sessions join on `repo` and overlap ± `session_overlap_min`; below `min_yield` it stays
infrastructure. Yield: lines Σ(ins + del); files Σ `magnitude.files` (an upper bound, no file names in the corpus);
integrations = lineages + hosts + offload backends in the window; moving pieces = depth-2 dirs + branch and worktree
events + agent classes. A host counts only if its copy existed before the episode ended: 229 launches carry ≥ 2
hosts in `meta.hosts`, mostly from later copies.

**Nation.** `nation_rule`: `commit_dominant` (CONTRACT text) or `session_over_human` (default): the dominant non-human
commit class, else the dominant overlapping session class, else human.

**Shape.** Launches on distinct lineages with overlapping windows, or sharing a session, form one engagement; ≥
`mirv_min_targets` targets is a MIRV. A `worktree` event of the lineage inside the window adds a target (commits do
not carry their worktree). A **unified** launch has band ≥ `unify_min_band` on a lineage that took ≥ 2 warheads
(itself, its worktrees, its components) within `unify_window_h`; the renderer draws converging traces first.

**Nations** (`compile/nations.json`). A class enters the legend at its first appearance (`first_ts`); its tone first
sounds at its first test. Generation chips enter by `generation_entry`: `first_test` (default; a model named on a
launch's session or trailer) or `first_seen`; of 51 generation firsts, `first_test` drops strays (a mixtral run under
the Codex CLI). `gcp-gemini` backends, tagged `local_model` by the ledger mapping, leave the ember nation through a
`local_backends` allowlist.

## 6. World layout (the composer's minimum; the cartographer leads)

Axial hex grid, laid out once from the final corpus. Continents = the five surfaces on a fixed ring in order of
first touch, GitHub an archipelago on the lower sea. Regions = (lineage, host) pairs in a seeded spiral outward by
`first_ts`, so the world grows outward as the camera widens; tiles = depth-2 dirs, `1 + floor(log10(files + 1))`
cells each. Data: `repos.json` (`id, kind, hosts, paths, first_ts, third_party, foreign_org`) and per (lineage, host,
dir) first touch and file count from events. Bridges light at a lineage's second copy. Output `layout.json`.

## 7. Timeline compilation

**Touches.** Commit dirs, file births, branches and worktrees become tile touches `(tile, s, w = log1p(n))`; a
launch adds weight 3 on its targets. Activity `a(s) = Σ w·2^(−(s − sᵢ)/h)`, `h = fog_half_life_days` in story time;
unknown before the first touch, explored after, active while `a > 0.15`. The half-life is 0.33 output s in era A
and 72 s in era C: decay reads right per era with no extra rule.

**Fog keyframes.** `fog.bin`: every 300 frames a snapshot of per-tile `(a, last_touch_s, explored)` as Float32Array
(3,108 tiles × 12 bytes × 69 snapshots = 2.6 MB), plus the touch list sorted by `s`. `render(k)` loads the nearest
snapshot at or below `k` and folds the touches since: pure, O(touches in ≤ 10 s), scrub-safe.

**Series.** `series.f32`: per frame, 12 channels (commits, births, branches, chat by 5 classes, offloads, launch
onsets, active tile count) at output rate, the one source for the band, hum, static and the left tallies.

**Cues.** `cues.json`: launch onsets `{k, launch_id, nation, generation, band, shape, warheads: [{k, tile}],
first_test, pan}`, bells and legend entries, with a per-frame `cue_offset[k]`: the sparse index RaidUI lacked.

**Camera.** Per story day, the bbox of explored tiles padded 8 % and fit to the 1,400 × 896 map viewport; smoothed
at compile in output time (critically damped, τ 3 s), never zooming in once zoomed out (the world only grows).
Written per frame to `camera.f32` (cx, cy, scale). The coda target is the full layout.

## 8. Renderer

One HTML page, `render(k)` pure over the compiled files: no `Date`, mulberry32 seeded by `launch_id`, woff2 fonts
inlined. RaidUI's `playback-controller` is the clock (`_tick` steps the export; speeds to 64×; no React); its
registry loop is the compositor. Draw order: 0 background `#07090e`; 10 continents and terrain tint (offscreen, cached by
camera key); 20 tiles by fog state (explored dim desaturated, active lit in the last conductor's hue); 30 bridges,
harbours, spurs; 40 comms beams (session open to episode start: the countdown) and ChatGPT rings; 50 offload sparks
(as an aggregate arc whose width follows the rate above 40/s); 60 launches (beam flight 0.25 s ending at impact,
flash, bloom; MIRV bus splitting into warheads; unified convergence); 80 border; 90 coda card.

Border at 1080p: top 64 px ticker; bottom 120 px band; left 220 px surface tallies; right 300 px nations in order
of entry (rows 34 px, slide-in 0.8 s): swatch, name, tests and cumulative yield (22 px), capacity (commits · files,
14 px), generation chips (8 px shades), a new chip named for 3 s at its first test.

## 9. Export pipeline and estimate

`export/run.mjs` splits frames into contiguous chunks, one Playwright page per chunk (`--disable-gpu
--force-color-profile=srgb --font-render-hinting=none`), each calling `render(k)` and capturing; chunks encode to
libx264 crf 18 yuv420p in parallel and concat; `export/audio.py` writes the WAV; ffmpeg muxes. Receipt: param_hash,
sha256 of 30 sampled frames' RGBA, WAV sha256, timings.

Estimate on the measured path (spike 01: 249 ms per frame at 5,000 tiles, render 3.4 ms; we have 3,108 tiles):
20,646 frames × 0.25 s = 86 CPU-min; 12 pages on 24 cores with 25 % contention ≈ 9 min; encode at the spike's
146 fps ≈ 2.4 min, overlapped; audio under 1 min: **about 12 min wall (86 CPU-min) for the full piece, 2 for the
cut**. Target path (spike 02): `getImageData` to a binary channel piped as rawvideo into ffmpeg, skipping
the compositor and PNG, expected 30 to 60 ms a frame (unmeasured): 10 to 20 CPU-min, about 4 min wall, inside the 30-minute bar on either reading. 4K: raster scales about 4×,
so about 29 min wall on the measured path, about 10 on the raw path.

## 10. Parameters (`compile/params.json`; each a single switch, hashed into every output)

| Parameter | Default | Moves |
|---|---|---|
| `fog_half_life_days` | 30 | decay `h` |
| `hue_axis` | actor | actor or surface hue |
| `geography` | surfaces | continent rule |
| `collapse_events_per_s` | 8 | chord and roll threshold |
| `camera` | fit_known | fit_known or fit_all |
| `third_party` | ruins | ruins or hidden |
| `era_rates` | A 4/yr, B 2.5/mo, C 2.4/day | clock segments |
| `era_bounds` | B 2023-04-01, C 2026-03-01 | era starts (arm: C 2026-01-15, +104 s) |
| `cut_90s_multiple` | auto (8.05) | cut composition |
| `episode_gap_h` | 2 | episode closing |
| `session_overlap_min` | 30 | session join |
| `min_yield` | lines 50 or files 3 | test threshold |
| `yield_bands` | log10 lines | band edges |
| `mirv_min_targets` | 2 | MIRV rule |
| `unify_window_h` / `unify_min_band` | 24 / 4 | unified rule |
| `generation_shades` | true | shade per generation or one hue per class |
| `nation_rule` | session_over_human | or commit_dominant |
| `generation_entry` | first_test | or first_seen |
| `local_backends` | omen-*, am4-*, fx99-* | ember allowlist |
| `glide_s` | 3 | era glides (0 = hard cut) |
| `cut_envelope_scale` | sqrt | envelope compression in the cut |
| `intro_s` / `coda_s` | 2 / 18 | piece frame |

## 11. Thin-slice build order (each a Lap with a receipt)

1. Clock, series, ticker, band, hum and static: a 90 s cut rendered twice, hashes equal. Time, sound and
   determinism before any map.
2. `launches.py`, `nations.json`; flashes on placeholder lineage dots, tones, bells, collapse (listen to the cut).
3. Layout, fog keyframes, camera; the full piece at 960 × 540.
4. Border: tallies, growing legend, generation chips.
5. Shapes: MIRV bus and warheads, unified convergence.
6. Parallel export at 1080p, coda card, receipt; spike 02 (raw capture) in parallel.

## 12. Open risks

- `nation_rule` departs from CONTRACT §8 text; without it Codex shows 2 tests (owner's call, CONTRACT v1.4).
- Era B crams 12 launches into 0.83 s; the `era_bounds` arm costs 104 s.
- 25 launches over 100k lines (one 2.96M) are likely vendored imports; band 6 may overstate them.
- Worktree warheads are inferred from worktree events; exactness needs per-commit copies from Merge.
- Files yield is an upper bound; `meta.hosts` includes later copies unless filtered.
- `gcp-gemini` backends are tagged `local_model`; the allowlist needs upkeep.
- Raw capture is unmeasured; 12 minutes rests on spike 01 plus parallel scaling.
- The April chat hole may read as a bug.
- Cut envelope scaling (`m^(−1/2)`) is a taste call to lap.
