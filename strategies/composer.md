# Strategy: composer (time first), rev 2

Composer angle, Workflow 2, 2026-10-09, DIRECTION rev 2; supersedes the rev 1 file. Densities come from an
aggregate-only probe of `corpus/merged/events.ndjson` (counts only) running the CONTRACT §8 episode rule at the
DIRECTION defaults (third-party and `foreign_org` lineages excluded), mapped through the era schedule.

## 0. What the probe measured

| Measure | Value |
|---|---|
| Own lineages with commits / own depth-2 tiles / third-party tiles | 99 / 2,032 / 1,076 |
| Episodes / launches (at or above min yield) | 935 / 850 |
| Engagements (one beam each; launches on different lineages with overlapping windows) | 524, of which 170 MIRVs (2 to 10 warheads) |
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
Rates are exact per calendar unit so ticker boundaries land on fixed beats: A one calendar year = 4 s from
2011-08-01, B one month = 2.5 s from 2023-04-01, C one UTC day = 2.4 s from 2026-03-01 to the 12:45Z snapshot.
Measured: A 46.66 s, B 87.48 s, C 534.08 s, story total 668.22 s; plus `intro_s` 2 (black, then the 2011-08-25
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

**Sync rule.** An event at story time `s` maps to output `f(s)`; its visual onset is frame `k = ceil(30·f)` and its
audio onset sample is `1600·k` (48 kHz / 30 fps = 1,600 samples per frame, exact). Sound and picture never disagree
by even one sample, by construction.

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

(length `0.12·1.6^(b−1)`, bloom `0.4·1.5^(b−1)`, radius `6·1.54^(b−1)`; bands are `floor(log10 lines)` per CONTRACT,
`yield_bands` swaps the edges.)

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

A mirrored scrolling density trace 1,600 × 104 px showing the last 20 output seconds, newest at the right edge.
Above the axis, the chatter: stacked areas by class colour, height `log1p(r)/log1p(14,757)` of the half-band. Below
the axis, in warm grey, the industry: commits per output second on the same log scale; offload rate as an ember
hairline riding the lower edge. Columns are precomputed per frame in `series.f32` (section 7) so the band and the
static are the same numbers. Era boundaries leave a 1 px tick that scrolls off; the April 2026 hole (no chat source)
is a flat line above the axis while the lower half keeps pulsing: radio silence over a working industry, shown
because it is true. No launches on the band: the band is radio and capacity, the map is tests.

## 4. How density becomes the story, era by era

**Era A, 0 to 46.7 s: the void.** One own commit, five own births, no launch, no radio. A dark field, the year
ticker counting, a faint bell every nine seconds on average. Grey ruins may surface (third-party arrivals; lap
variable `third_party`). The loneliness is the length: 46 s of almost nothing.

**Era B, 46.7 to 134.1 s: radio before territory.** ChatGPT enters in 2023-04 (film 48.0): a green legend row with
0 tests, broadcast rings into the dark, static rising from 50 silent seconds to p90 246 messages per second; model
generations appear as shades (auto 2024-11, gpt-5-1 2025-11, gpt-5-2 2025-12). Against it, two isolated human tests,
each with a bell, sixteen months apart. Then 2026-01: twelve launches in under a second, Claude's first test inside
them, a coral row and E4 entering. February is silent. The ear hears research for 85 s, then a burst.

**Era C, 134.1 to 668.2 s: the cascade.** The rate drops to a day per 2.4 s and the ticker says so. March is the
migration month: 56 launches, the commit hum at its peak (793 per second on 2026-03-17), the Windows continents fill.
April: tests continue, the band goes flat (the hole). May and June: Claude's generations enter as shades (Opus 4.7
05-08, Haiku 4.5, Sonnet 4.6, Opus 4.8, Fable 5 06-09); singles grow (median yield 728 to 3,331 lines a month).
2026-06-29 Codex enters (cyan, G4); 07-03 automation (amber, D4); 07-20 the first local seat (ember, C3, as sparks;
it conducts no test, honestly 0 in its row); Opus 5 07-25. July opens the MIRV era: 46 MIRVs that month, 38 in
August, 36 in September, the largest a 10-warhead engagement on 09-23. August is the chatter peak (52,833 records).
09-27 OpenCode enters (violet, B4) with seven local models in one day, and HQ moves to omen-linux as the old
continent dims. 2026-10-03: the offload storm, the 0.8 kHz band roars: the local seats answering. Launch rate holds
at p90 5 per second; the mix of nations, not the count, is the late story.

**Ending (18 s coda).** At the snapshot the story clock stops. 0 to 3 s: last blooms decay in output time; hum and
static fade with τ 2 s. 3 to 7 s: the camera eases (critically damped, τ 1.5 s) from the explored fit to the whole
laid-out world; the unknown stays dark. Tallies finish counting. 7 to 9 s: silence. 9 to 17 s: the final tally card,
one row per nation in order of entry: first test date, tests, cumulative yield, shapes (singles, MIRVs, unified);
under it the totals (launches, lineages, tiles explored, commits, messages). 17 to 18 s: black.

## 5. Compile: episodes, shapes, nations

**Episodes** (`compile/launches.py`, CONTRACT §8). Own commits per lineage sorted by `ts`; a gap over `episode_gap_h`
closes an episode. Sessions join when their `repo` matches and their span overlaps the window ± `session_overlap_min`.
Below `min_yield` the episode stays infrastructure. Yield: lines = Σ(ins + del); files = Σ `magnitude.files` (an
upper bound: distinct file names are not in the corpus; recorded as such); integrations = distinct lineages + hosts
present at the time + offload backends called in the window; moving pieces = distinct depth-2 dirs + branch and
worktree events in the window + distinct agent classes. A host counts only if that host's copy existed before the
episode ended (its `repo_local` first_ts), else every pre-migration commandcenter episode would read multi-host
(229 launches carry ≥ 2 hosts in `meta.hosts`, mostly later copies).

**Nation.** `nation_rule`: `commit_dominant` (CONTRACT text) or `session_over_human` (default): the dominant non-human
commit class, else the dominant overlapping session class, else human.

**Shape.** Group launches into engagements: launches on distinct lineages whose windows overlap, or that share a
session id, form one engagement; ≥ `mirv_min_targets` targets is a MIRV, `warheads` = targets. Worktrees inside one
lineage count as separate targets when a `worktree` event of that lineage falls in the window (commits do not carry
their worktree; a Merge addition `meta.copies` per commit would make this exact). A **unified** launch is a launch of
band ≥ `unify_min_band` (4) on a lineage that received ≥ 2 warheads (on itself, its worktrees or its lineage
components) within `unify_window_h`; its `unifies` lists them and the renderer draws converging traces before the
blip.

**Nations** (`compile/nations.json`). A class enters the legend at its first appearance of any kind (`first_ts`);
its tone first sounds at its first test. A generation chip enters by `generation_entry`: `first_test` (default:
the model named on a joined session or trailer of a launch) or `first_seen`. The probe found 51 generation firsts;
`first_test` keeps the legend to models that conducted work and drops strays (a mixtral run under the Codex CLI).
Offload backends that are not local seats (`gcp-gemini`, `gcp-gemini-pro` are tagged `local_model` by the ledger
mapping) are reclassified by a `local_backends` allowlist so the ember nation stays honest.

## 6. World layout (the composer's minimum; the cartographer leads)

Axial hex grid. Continents = the five surfaces placed on a fixed ring in order of first touch (omen-c, omen-e,
omen-linux, am4, fx99), GitHub as an archipelago on the lower sea. Regions = (lineage, host) pairs packed in a
seeded spiral from the continent centre outward in order of `first_ts`, so the world grows outward as the camera
widens. Tiles per region = distinct depth-2 dirs, each `1 + floor(log10(files + 1))` cells. Data: `repos.json`
(`id, kind, hosts, paths, first_ts, third_party, foreign_org`), plus from events per (lineage, host, dir): first touch,
cumulative file count. Bridges join regions of one lineage on two continents and light at the second copy's first
touch. Output `layout.json`: tile id → (q, r, continent, region, lineage). Laid out once from the final corpus.

## 7. Timeline compilation

**Touches.** Every commit's `files` dirs, every `file_birth`, branch and worktree event becomes a tile touch
`(tile, s, w)` with `w = log1p(n)`; launches add a touch of weight 3 on every target tile. Activity
`a(s) = Σ w·2^(−(s − sᵢ)/h)` with `h = fog_half_life_days` in story time; state = unknown before the first touch,
explored after, active while `a` exceeds 0.15. Era A's half-life is 0.33 output s, era C's 72 s: decay reads
right in each era without a separate rule.

**Fog keyframes.** `fog.bin`: every 300 frames a snapshot of per-tile `(a, last_touch_s, explored)` as Float32Array
(3,108 tiles × 12 bytes × 69 snapshots = 2.6 MB), plus the touch list sorted by `s`. `render(k)` loads the nearest
snapshot at or below `k` and folds the touches since: pure, O(touches in ≤ 10 s), scrub-safe.

**Series.** `series.f32`: per frame, 12 channels (commits, births, branches, chat by 5 classes, offloads, launch
onsets, active tile count) at output rate, the one source for the band, hum, static and the left tallies.

**Cues.** `cues.json`: sorted launch onsets with `{k, launch_id, nation, generation, band, shape, warheads: [{k, tile}],
first_test, bell, pan}`, plus bells and legend entries. A per-frame bucket index (`cue_offset[k]`) replaces the
search; this is the sparse event index RaidUI lacked.

**Camera.** Per story day, the bbox of explored tiles padded 8 % and fit to the 1,400 × 896 map viewport; smoothed
at compile in output time (critically damped, τ 3 s), never zooming in once zoomed out (the world only grows).
Written per frame to `camera.f32` (cx, cy, scale). The coda target is the full layout.

## 8. Renderer

One HTML page, `render(k)` pure over the compiled files, no `Date`, no unseeded random (mulberry32 keyed by
`launch_id`), fonts inlined as woff2. Clock: RaidUI's `playback-controller` with `_tick` as the export stepper and a
speed list to 64×; React dropped. Compositor: RaidUI's registry loop (clear, base, overlays by zIndex, save/restore,
per-overlay try/catch). Draw order: 0 background `#07090e`; 10 continents and terrain tint (offscreen, cached by
camera key); 20 tiles by fog state (explored dim desaturated, active lit in the last conductor's hue); 30 bridges,
harbours, spurs; 40 comms beams (session open to episode start: the countdown) and ChatGPT rings; 50 offload sparks
(as an aggregate arc whose width follows the rate above 40/s); 60 launches (beam flight 0.25 s ending at impact,
flash, bloom; MIRV bus splitting into warheads; unified convergence); 80 border; 90 coda card.

Border at 1080p: top 64 px ticker and rate; bottom 120 px band; left 220 px surface tallies (commits, tiles
explored, tests landed); right 300 px nations, rows 34 px in order of entry, slide-in 0.8 s: swatch, name, tests
(22 px), cumulative yield (`1.2M lines`, 22 px), capacity line (commits · files, 14 px), generation chips (8 px
shades) beneath; a new chip's name shows for 3 s at its first test. Up to 8 class rows fit with room.

## 9. Export pipeline and estimate

`export/run.mjs` splits frames into contiguous chunks, one Playwright page per chunk (`--disable-gpu
--force-color-profile=srgb --font-render-hinting=none`), each calling `render(k)` and capturing; chunks encode to
libx264 crf 18 yuv420p in parallel and concat; `export/audio.py` writes the WAV; ffmpeg muxes. Receipt: param_hash,
sha256 of 30 sampled frames' RGBA, WAV sha256, timings.

Estimate on the measured path (spike 01: 249 ms per frame at 5,000 tiles, render 3.4 ms; we have 3,108 tiles):
20,646 frames × 0.25 s = 86 CPU-min; 12 pages across 24 cores with 25 % contention ≈ **9 min**; encode at the
spike's 146 fps ≈ 2.4 min, overlapped per chunk; audio under 1 min; **about 12 min wall for the full piece, about
2 min for the cut**. Target path (spike 02): `getImageData` to a binary channel piped as rawvideo into ffmpeg, skipping
the compositor and PNG, expected 30 to 60 ms a frame (unmeasured) → about 4 min wall. 4K: raster scales about 4×,
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

1. `clock.json`, `series.f32`, ticker and band only, with hum and static: a 90 s cut, rendered twice, hashes equal,
   A/V offset zero by the sample rule. Proves time, sound and determinism before any map.
2. `launches.py` and `nations.json` with launch flashes on placeholder lineage dots, tones, bells, collapse; the
   cut's 41 collapsed seconds listened to.
3. Cartographer layout, fog keyframes, camera; the full piece at 960 × 540 for review.
4. Border: tallies, growing legend, generation chips.
5. Shapes: MIRV bus and warheads, unified convergence.
6. Parallel export at 1080p, coda card, receipt; spike 02 (raw capture) in parallel.

## 12. Open risks

- `nation_rule` departs from CONTRACT §8 text; without it Codex shows 2 tests. Owner's call, CONTRACT v1.4.
- Era B's first light crams 12 launches into 0.83 s; the default keeps it, the `era_bounds` arm costs 104 s.
- 25 launches over 100k lines (one 2.96M) are likely vendored imports or bulk copies; band 6 may overstate them.
- Worktree targets are inferred from worktree events; exact MIRV detection needs commit copies in Merge.
- Files yield is an upper bound (no distinct file names); `meta.hosts` includes later copies unless filtered.
- `gcp-gemini` backends are tagged `local_model`; the allowlist must be maintained.
- The raw capture path is unmeasured; the 12-minute estimate rests on spike 01 and parallel scaling.
- April 2026 has no chat source; the flat band is honest but may read as a bug without the ticker's help.
- Envelope scaling in the cut (`m^(−1/2)`) is a taste call to lap.
