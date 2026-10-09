# Strategy: composer (time first)

Strategist: composer angle, Workflow 2, 2026-10-09. Inputs: DIRECTION.md, CONTRACT.md §1/3/7, CORPUS-REPORT.md,
SURVEY.md §4/4b, spike 01, RaidUI vendor copies, the judges' six criteria. Densities below were measured on
`corpus/merged/events.ndjson` with an aggregate-only probe (counts, no corpus lines) mapped through the DIRECTION.md
era schedule. "Own" means every actor class except `third_party`.

## 0. The finding that shapes everything

Under the initial schedule the raw corpus would make era B the loudest era of the piece: 16,563 of its 16,696
commits (99.2%) are `third_party` (upstream llama.cpp history that arrived with a fork), and all 875 era A commits
but one are third-party too. Played as tones, era B would run at a mean of 191 events per film second of somebody
else's work. The honesty rule ("we show what was touched") decides it: third-party history never sounds and never
flashes. A third-party lineage appears once, at its **arrival time** (the earlier of its first own-class event and
its last third-party commit, i.e. the clone), as grey hatched ruins with one muffled thud. With that rule the real
own-class densities are:

| Era (film span) | Own tone events (commit, repo_born, branch, worktree) | Offload sparks | Chat messages |
|---|---|---|---|
| A, 0 → 46.7 s | 13 total; 39 of 47 seconds silent; max 4/s | 0 | 0 (no radio exists) |
| B, 46.7 → 134.2 s | 477; p50 1/s, p95 25/s, max 49/s; 27 silent seconds | 0 | 12,263 (all ChatGPT) |
| C, 134.2 → 668.2 s | 10,122; p50 5/s, p90 43, p95 74, p99 218, max 800/s | 26,386; p95 20/s, p99 369, max 13,876/s | 493,454; p50 6/s, p90 3,413, max 15,103/s |

Peak single frame: 3,455 audible events (the 2026-10-03 HEARTH burst). Tiles touched per frame (own): p99 18,
max 64. The reference's arc is already in this table: lonely flashes, radio into the dark, a cascade, a late
crowd of sparks. The design job is to make density legible at every one of those scales without flooding the eye
or the ear. **Peak designed for: 14,038 audible events per film second** (film second 653, 2026-10-03; 13,964 of
them Claude-to-local offloads), with own tone events peaking at 800/s (2026-03-17).

## 1. Time: the clock, the rate schedule and its glides

### 1.1 The clock is compiled, not ticked

Compile emits `clock.json`, a monotone piecewise map from film seconds `f` to story seconds `s`:
`{param_hash, fps, segments: [{f0, f1, s0, s1, kind: const|glide, r0, r1}], eras, T_story, T_coda}`. Rates are exact per calendar unit so ticker boundaries land on fixed beats: era A maps each
calendar year to 4 s, era B each calendar month to 2.5 s, era C each UTC day to 2.4 s. Era A starts 2011-08-01
(the first event is the GitHub account on 2011-08-25, so the piece opens on 3.3 s of black before the first bloom).
Measured lengths: A 46.67 s, B 87.50 s, C 534.07 s (to the 12:45Z snapshot), story total 668.24 s, plus a coda of
18.5 s: **686.7 s, 20,601 frames**.

### 1.2 Glides at era boundaries

The schedule slows twice: A→B by 7.5× (0.011 to 0.082 film s per story day), B→C by 29× (to 2.4). A hard cut
would lurch the decay, the band scroll and the reveal rate. Each boundary gets a **glide** of `glide_s` = 3 film
seconds centred on the boundary, in which `log r` follows a smoothstep from the old rate to the new. Compile
integrates the glide numerically at 1 ms and stores 10 ms knots; story-time anchoring is kept (2023-04-01 and
2026-03-01 land within 0.2 s of their schedule positions; compile reports the exact drift). `glide_s: 0` gives the
hard cut for a lap arm.

### 1.3 The ticker carries the rate

Top centre, JetBrains Mono. Resolution follows the era: A shows `2017·12`, B `2025·11` with the day small and
dimmed, C `2026·09·27` with a 24-hour hairline beneath it (one story hour = 0.1 s, so the diurnal pulse of the
night drains is visible as a moving notch). To the right, always, the rate in the unit that reads best at two
significant digits: `1 yr = 4 s`, during a glide `1 mo = 0.71 s`, then `1 day = 2.4 s`. The reference never changed
rate; we do, so the readout is never hidden. In the cut the readout appends the multiple: `1 day = 0.29 s · ×8.25`.
At each boundary the rate glyphs alone brighten for 0.6 s; nothing else announces the era.

### 1.4 The 90-second cut

Same compiled timeline, uniform multiple on the story part only: `m = T_story / (90 − T_coda_cut)`, with the cut
coda 9 s, so `cut_90s_multiple: auto` resolves to **m = 668.24 / 81 = 8.25**. Era A becomes 5.7 s, B 10.6 s, C
64.7 s. Nothing is time-stretched: the cut is a second `clock.json` (all segments scaled by 1/m) and the same event
list re-mapped, so flashes, collapse plans and the audio are recompiled at the cut clock. Film-time envelopes (flash
decay, tone length, glide length) stay perceptual and do not scale; density simply rises by 8.25×, and the collapse
rules below absorb it (own tone peak becomes 6,600/s; it changes nothing structurally because onsets are capped).

## 2. Two time constants: flash in film time, memory in story time

Every visual and aural response splits into a **flash** (perceptual, film seconds, constant across eras and cuts)
and **activity** (semantic, story days, the fog half-life). Flash: `F(t) = Σ_i w_i · exp(−(t − f_i)/τ_flash)`,
`τ_flash = 0.15 s`, `w_i = 0.35 + 0.65·min(1, log10(1+lines_i)/4)` (line counts: p50 10, p90 559, p99 6,439).
Activity: `A(t) = Σ_i w_i · 2^(−(s(t) − s_i)/H)` with `H = fog_half_life_days`. With H = 30 days the activity
half-life is 0.33 film s in era A (an era A touch is effectively a pure flash, as in the reference), 2.5 s in era B
and 72 s in era C (the Windows continents stay lit through summer, then dim as work moves to Linux in late
September). That is the single mechanism by which density becomes territory.

## 3. Sound

### 3.1 Mapping

| Event | Voice | Pitch / band | Gain |
|---|---|---|---|
| commit (own) | short tone: sine + 2nd and 3rd partials, 4 ms attack, τ 180 ms | human A3 220 Hz, Claude E4 329.6, Codex G4 392, OpenCode B4 493.9, local C3 130.8, automation D4 293.7 | `−24 dB + 12 dB·min(1, log10(1+lines)/4)` |
| repo_born | low bell: inharmonic partials 1, 2.0, 2.76, 5.4, 8.9 on class pitch −1 octave, τ 2.5 s | as class | −14 dB; births within 250 ms merge into one bell at +3 dB |
| branch / worktree | tone at class pitch +1 octave, τ 60 ms, −10 dB under commit | | |
| third-party arrival | muffled thud: 70 Hz sine burst through 300 Hz low-pass, τ 120 ms | | −28 dB; no tones for upstream history |
| chat_msg | band-passed static, one band per class: ChatGPT 0.9 kHz, Claude 1.4, Codex 2.0, OpenCode 2.6 (Q 0.9) | | `a = a_floor + a_max·log10(1+msgs/story-day)/4.3`, one-pole smoothing 250 ms |
| offload_call | narrow high static (4.2 kHz, Q 3) plus a 1 ms click per spark below the collapse threshold | | same log law on calls/story-day |
| unrecorded chat span (2026-04, and the clock before 2023-04 is *not* unrecorded: radio did not exist) | digital zero in the chat bands | | |

The ChatGPT years are static with no tones, except the 133 own commits (Claude, 2026-01) that close era B.

The quiet/unrecorded distinction carries the honesty rule into sound: a quiet stretch keeps a hiss floor
(`a_floor` = −54 dB); the 2026-04 hole (no chat source covers it; 928 commits do) is digital zero in the chat bands
while tones continue: territory with the radio off.

### 3.2 The collapse rule (`collapse_events_per_s`, default 8)

The ear gets at most `c` onsets per second, whatever the peak. Film time is cut into slots of `1/c` = 125 ms,
aligned to f = 0. Per slot, compile counts own tone events `E`:

- `E ≤ 1`: discrete. The tone sounds at its frame-snapped time `ceil(30·f)/30`, so the onset and its flash share a
  frame (no audio-leads-video error; the snap is inaudible at 33 ms).
- `E ≥ 2`: one **chord** strike at the first event's snapped time, one voice per class present, each voice's gain
  `g(log10(1+Σ lines of that class in slot)) + 3 dB·log2(count)`, clamped to −6 dB.
- Three or more consecutive collapsed slots: the strikes continue on the 8 Hz grid as a **roll**, softer attack
  (12 ms) and shorter decay (90 ms) so it reads as a tremolo, not a machine gun.
- More than 8 events per slot (64/s) for a class: add a sustained pad at that class pitch, gain following log rate
  through 400 ms smoothing. This is the cascade's drone: 2026-03-17/18 (1,548 human commits, 800/s at peak) becomes
  an A3 roll swelling into a pad; the September Claude-and-Codex months become an E4/G4 interval.

In era C 208 of 535 seconds exceed 8/s, so collapse is the ordinary state of the summer, not an exception; era A
never collapses, era B collapses in 19 seconds. Bells never collapse (max 5 births/s). `collapse_mode:
roll|chord|none` is a lap switch; `none` is the flood arm, kept for the lap record only.

### 3.3 Visual collapse uses the same threshold

- Per tile per frame: at most one flash; above `c` events/s on one tile its flash becomes a steady glow
  `∝ log10(rate)`, not a strobe.
- Sparks: per seat link, up to `c` particles/s; above it the HQ→seat link becomes a solid arc, width
  `1 + 2.5·log10(rate)` px. The 2026-10-03/04 burst (22,065 calls in two story days) renders as a lit filament
  for 4.8 film seconds, 13 s before the end: the climax the corpus wrote.
- **Change budget** (criterion 2): per frame, newly flashing or newly revealed tiles are capped at
  `max(8, flash_budget_frac × revealed)`, default 0.15. Excess touches queue FIFO for at most 10 frames (story
  error ≤ 3.3 h in era C) and then fold into the next flash. Compile computes the budget, so `render(t)` stays pure.
  The binding case is measured: film 149.0 (2026-03-07) touches 64 of 101 revealed tiles in one frame; the queue
  spreads it over 5 frames as a reveal wave ordered by distance from the region seed. Elsewhere the worst era C
  frame is 32 of 170 (18.8%, also queued) and 22 of 197.

## 4. The radio band

Bottom strip, 1920 × 112 px, one pixel column per film frame, so the band shows the last 64 film seconds and is a
pure function of the frame index. Each column is a stacked trace by class (ChatGPT green, Claude coral, Codex cyan,
OpenCode violet, offload ember on a separate thin lane above), height `= 104·log10(1 + rate)/4.3` where rate is
messages **per story day**, so a rate change does not inflate the trace. The rate change shows instead in the tick
marks along the band floor: month ticks in B every 75 px, day ticks in C every 72 px, year ticks in A every 120 px.
Unrecorded spans draw a dotted baseline; quiet spans a solid one. Compile stores `band.bin`: per frame 6 lanes × u8.

## 5. Density as the story, era by era

- **A (0–46.7 s), lonely flashes.** Nine repo births (bells, mostly GitHub islands), three branches, one commit;
  39 silent seconds. Ruins arrive grey and hatched as clones land. The band is a flat solid line.
- **B (46.7–134 s), radio into the dark.** No territory moves for most of 87 seconds. ChatGPT rings radiate from HQ
  into void (no cwd, so no beam), max 1,956 ring records/s, drawn as at most 8 rings/s whose radius grows with
  log rate. Static climbs from a whisper in 2023 to 2,535 messages in 2025-12. The first Claude tones (2026-01)
  close the era.
- **C (134–668 s), the cascade.** March: the bulk day (2026-03-17) is the first roll and the first big reveal wave;
  April: the radio cuts out (dotted band, digital zero) while commits keep lighting C: and E:; May to August: beams
  from HQ to regions (p99 4, max 9 class-region pairs per frame), the band at 3,000+ msgs/s, Windows continents at
  full light; 2026-07-04: the first HEARTH spark (33 that day); 2026-09-27: the Linux continent appears (442 commits,
  the day Linux Claude and Codex begin) and, with a 72 s half-life, the Windows land visibly dims over the next
  minute; 2026-10-03/04: the offload filament and the high static saturate.

## 6. The ending (coda 18.5 s; 9 s in the cut)

1. 0–1.5 s: the story clock stops at the snapshot; the ticker freezes on `2026·10·09 12:45Z` and the rate readout
   becomes `now`. Activity decays on a coda half-life of 2 film seconds so everything settles to *explored*.
2. 1.5–7.5 s: the camera pulls back to the bounding box of all explored tiles (12% padding), ease-in-out. The
   unknown stays black; dim land includes everything that went quiet.
3. Tallies settle: odometer digits finish rolling by 3 s; static fades over 2 s; tones ring out.
4. 7.5–10.5 s: digital silence.
5. 10.5–18.5 s: the final tally card (per class: commits, files, messages; per surface; span; "third-party ruins:
   11 lineages, not counted").

## 7. World layout (summary; the cartographer leads)

Axial hex grid. Continents: `omen-c`, `omen-e` (west), `omen-linux` (east), `am4` and `fx99` (islands off Linux),
the GitHub archipelago (south sea). Regions: the 201 `repos.json` lineages, one per (lineage, host); the 21
multi-host lineages get bridges that light when both copies exist. Tiles: own depth-2 directories (3,053 measured),
`ceil(1.5·log2(1 + files))` hexes each, seeded on a hex spiral by `(first_ts, id)` and grown by BFS ring fill.
Needs from `repos.json`: `id kind hosts paths first_ts third_party foreign_org remotes`; from events: tile first
touch and file count (`file_birth.n`; for git tiles a touch-count proxy). HQ sits on the host of the operator's
sessions (omen-c, then omen-linux after the migration), gliding over 6 film s.

## 8. Timeline compilation (Python 3.14 + numpy, deterministic)

Stages write hashed files to `compile/out/<param_hash>/`: `clock.json` (§1); `events.bin`, columnar, sorted by
film time (f f64, kind u8, class u8, tile u32, lines u32, n u32, flags u8; a touch table for multi-tile commits),
with third-party arrival times; the change-budget flash list (§3.3); per-tile activity keyframes every 30 frames,
float16, 687 × 3,053 × 2 B = 4.2 MB, from which the page computes `A = A_key·2^(−Δs/H) + Σ touches in (key, t]`
exactly; `camera.bin`, per-frame `(cx, cy, scale)` from the explored bbox through a critically damped spring
(τ 3 s) run forward in compile, scale monotone (the world only grows); `tally.bin`, cumulative u32 per class ×
(commits, files, messages) and per surface; `band.bin` (§4); `voices.json`, onsets `{f, kind, class_mask, gains}`
after collapse plus per-class static envelopes at 100 Hz.

## 9. Audio synthesis

`compile/synth.py` renders `voices.json` at 48 kHz stereo with numpy: tones and bells additively, static from PCG64
noise seeded by `(param_hash, block)` through biquad band-passes, a soft limiter at −1 dBFS, pan by the event's
continent x. About 32 M samples, under a minute of CPU. Alignment holds by construction: synth and renderer read the
same `f_i`, and discrete onsets are frame-snapped. Output `audio.wav` with its sha256.

## 10. Renderer structure (one HTML page, Canvas 2D)

From RaidUI: `clock.js` (playback-controller without React; `seek(frame)` for export; speeds 0.25× to 64×),
`state.js` (the render-state pattern with preallocated typed arrays; binary search into `events.bin` for the
one-second flash window), `layers.js` (the registry compositor: zIndex order, save/restore, try/catch), `fog.js`
(offscreen explored mask cached by reveal count, the shape-raster cache key), `audio-preview.js` (WebAudio playback
of `audio.wav` for scrubbing only). No `Math.random` or `Date.now`; jitter from mulberry32 seeded by tile id; fonts
inlined. Draw order: background `#07090e`; sea and archipelago; explored terrain with surface tint; ruins hatching;
activity fill (last-touch class hue, or surface hue); bridges, spurs, harbours; beams and rings; sparks and arcs;
flashes (`lighter`); the border in screen space: left surface tallies, right class tallies (20 px tabular mono),
bottom radio band, top ticker. The map occupies the inner 1600 × 860.

## 11. Export pipeline and estimate

Node driver (Playwright 1.64, chromium-1248, pinned): P = 12 browser instances (24 cores, 105 GB free), each owning
a contiguous frame range. Per frame: `render(k/30)`, then CDP `Page.captureScreenshot` clipped to the canvas with
`optimizeForSpeed: true`, bytes piped to a per-worker ffmpeg (`image2pipe` → libx264 crf 18, preset fast, `-g 60`,
2 threads) writing a closed-GOP segment; nothing touches disk but segments. Concat demuxer joins segments without
re-encode; a final pass muxes `audio.wav` as AAC 192k. Each worker logs sha256 of every 30th frame's RGBA
(`getImageData`) into a receipt `{bundle_sha, param_hash, frame, rgba_sha}`; a re-render of any frame must match.

Against spike 01 (249 ms per frame at 5,000 tiles, nearest to our ~3,000 plus border), one page needs 86 min. At P = 12 with an assumed 0.6 parallel efficiency the capture throughput is
28.8 fps, so **about 12 min of capture, 15 min end to end** (compile 1, synth 1, concat and mux 1). At 0.35
efficiency it is 22 min, still under the 30 min criterion. The cut (2,700 frames) takes about 2 min. 4K: capture
cost scales with pixels (about 1 s per frame per page), so the 4K cut is about 8 min and the full 4K piece about an
hour unless raw capture (CDP `getImageData` over binary IO, skipping PNG) lands; the first 4K target is the cut.

## 12. Parameter table (each a single switch in `params.json`; its hash names the output)

| Switch | Default | Values | Compile stage it reads | Re-synth audio? |
|---|---|---|---|---|
| `fog_half_life_days` | 30 | any > 0 | activity | no |
| `hue_axis` | actor | actor, surface | renderer palette (bundle flag) | no |
| `geography` | surfaces | surfaces, lineage (one land per lineage) | layout | no |
| `collapse_events_per_s` | 8 | any > 0 | budget, voices | yes |
| `camera` | fit_known | fit_known, fixed_final, fit_active | camera | no |
| `third_party` | ruins | ruins, hidden, history (upstream as grey flashes, −24 dB ticks, collapsed) | index | yes |
| `era_rates` | A 4/yr, B 2.5/mo, C 2.4/day | any per era | clock (everything downstream) | yes |
| `cut_90s_multiple` | auto (8.25) | auto or a number | clock (cut) | yes |
| composer additions: `glide_s` 3, `tau_flash_s` 0.15, `flash_budget_frac` 0.15, `collapse_mode` roll, `coda_s` 18.5/9, `pitch_map`, `static_bands` | | | clock, budget, voices | some |

## 13. Thin-slice build order

1. `clock` and a ticker-only page; check monotonicity, era lengths, glide drift.
2. `events.bin`, budget and voices; reproduce this density table as the compile's receipt.
3. `synth` plus a black video with ticker and band only: the first watchable Run and the test of the arc in sound
   alone (if era B does not read as radio into the dark here, no map will fix it).
4. Layout v0, fog states, activity keyframes. 5. Flashes, change budget, camera. 6. Border tallies.
7. Beams, rings, sparks, bridges, harbours, spurs, ruins.
8. Parallel export; measure throughput at P = 4, 8, 12, 16; frame-hash receipts.
9. Coda, tally card, the 90-second cut. 10. Lap 1: one switch per Run.

## 14. Open risks

- The 2026-10-03/04 offload burst (22,065 calls) is the loudest moment; it must be checked against the ledger
  (caller and tool mix) to confirm it is real work and not a polling class the drop rule missed.
- The 2026-03-17/18 human commit burst (1,548) may be a bulk import or migration; if so, the cascade's opening is an
  artefact and needs a `meta` rule, not a mute.
- Third-party arrival times are heuristic; a fork with later own commits may surface late or early.
- Parallel capture scaling is unmeasured; bench27 vLLM load shares the CPU. Step 8 measures before any claim.
- Git tiles have no file counts in the corpus; tile area uses a touch-count proxy until `ls-tree` counts exist.
- Era C is 8.9 minutes; May to August may read as monotone (lap `era_rates.C`). Rolls fill 39% of era C seconds
  (lap `collapse_mode`).
- Software raster determinism across Chromium runs (text antialiasing) must be confirmed by the frame-hash receipt.
