# LAP-03 thin slice: result (2026-10-09)

Grammar end to end: black map, regions as dots, launches as blooms (band table, nation hue, generation shade),
lineage-first bells and rings, nation-first octave, growing legend, hum from the commit rate and static from the chat
rate, luminance budget, collapse. Code: `compile/{build,build_cli,layout,series,synth}.py`,
`render/{palette,state,fields,launch,border,main}.js`, `export/{verify.mjs,state_node.mjs,still.mjs}`, runner
`lap.py` (stages build, verify, cut, excerpt, full). Receipts: `receipt-build.json`, `receipt-verify.json`,
`receipt-export-{cut,excerpt,full}.json`, per-export `out/*/receipt.json` and `frame-hashes.txt`.

**Corpus:** pinned merge `cache/corpus-pin-0653` (events sha256 `4e1e1c97...`), relations and chatgpt_links present and
used (13 constellation discs hold 79 joined regions, 208 loose single-dot discs). 287 regions (git lineages plus
non-git directories with activity), 1,512 launches (default session arm), 126,937 weighted touches folded to 9,511
deltas in the full piece (3,897 in the cut), checkpoints every 900 frames.

## Frame time on real content (K = 10 workers, nice, bench27 load running; CDP PNG optimizeForSpeed)

| Export | Frames | Wall (capture + encode) | ms per frame effective | capture ms per frame per worker (median) |
|---|---|---|---|---|
| 90 s cut (1080p, audio) | 2,700 | 13.7 s | **4.97** | 44.2 |
| 60 s excerpt of the full piece, from 2026-07-05 (frame 13,157) | 1,800 | 9.2 s | **4.96** | 46.4 |
| **Full piece, measured, not projected** | 20,650 | **138.5 s** frames, **184.5 s** with concat, AAC mux and probe | 6.69 | 44.6 |

The full export fits under 15 minutes with a wide margin (3.1 minutes wall), so nothing is extrapolated. STRATEGY's
estimate was about 9 minutes; the real page costs 6.7 ms per frame at K = 10 against the spine's 7.8 ms at K = 12 on
the spike page. The full mp4 is 35.7 MB (688.33 s, 20,650 frames); the cut 6.0 MB; the excerpt 3.4 MB. Videos
stay in `out/` (git-ignored).

## Receipt

| Check | Result |
|---|---|
| Compile twice, separate processes (hash seeds randomised) | kw-data.js and audio byte-identical, full and cut |
| 30 frames re-rendered in another order, in a second Chromium | **30 of 30 equal** (see the purity bug below) |
| `buildState` under Node 24 (vm sandbox, no browser) vs a Python brute-force sum, frames 7,721 / 14,273 / 19,457 | max relative error 1.5e-8, 3.4e-8, 2.8e-8 (85 / 195 / 372 active region-groups; activity up to 5,483) |
| Luminance budget at the 6 busiest sampled frames of the cut | fields only max OKLab L **0.528** (limit 0.55); with launches **0.8715** (launches own 0.55 to 0.95) |
| Sync probe, 90 s cut | white frame 15 only, click onset sample 24,000, **delta 0.0 ms**; duration 90.000 s, 2,700 frames, audio 4,320,256 (+256 AAC tail) |
| Sync probe, excerpt (probe on its first frame, click at sample 0) | white frame 13,157, **delta 0.0 ms**, 1,800 frames, 2,880,512 samples (+512 tail) |
| Sync probe, full piece | white frame 15, **delta 0.0 ms**, 20,650 frames, 33,040,384 samples (+384 tail), 688.33 s |
| Page errors | none in all three exports |
| WAV length | exactly F x 1,600 samples (full 33,040,000; cut 4,320,000) |

Combined frame-hash sha256: cut `d0aacd74...`, excerpt `b257551e...`, full `7a52cfe1...` (Chromium 1248, DejaVu Sans Mono
fallback, `--force-color-profile=srgb --font-render-hinting=none --disable-lcd-text`).

**Two defects the receipt caught, both fixed before the numbers above:** (1) the OKLCH colour cache keyed alpha by a
rounded value and returned the first caller's string, so a frame depended on what was drawn before it (the
order-independence check scored 1 of 30; now alpha is formatted per call and only the rgb prefix is cached);
(2) the first bloom cap (6) let overlapping blooms stack to L 0.998 at the cut's densest frames; the cap is now 2.5
(peak 0.87).

## What the grammar does, counts only (I cannot listen; this is measured audio plus the stills I looked at)

- **Audio level.** Full piece RMS per minute (dBFS): -44, -41, -32, -36, -35, -29, -30, -29, -25, -25, -25, -31; peak
  -4.3 dBFS. Era A and the ChatGPT years are near-silent (static only, below -40), which is the intended "radio before
  territory"; the loudness arrives with era C. The 90 s cut climbs from -39 to **-17 dBFS RMS** in its last 40 s (peak
  -2.6), so the cut is dense and loud; the excerpt sits at -25 to -30.
- **Collapse is the sound of the cut.** 76 percent of the cut's frames are collapsed (2,043 of 2,700), 193 of its 399
  chord bins are 16 Hz roll; only 111 launches sound as individual tones (1,512 launches in 83 s, peak 11 starting in
  one frame). In the full piece collapse covers 927 frames (30.9 s, 4.5 percent): STRATEGY expected about 8 s, but the
  merge has 1,512 launches against the spine's 816, and the sliding window threshold of 8 per second is hit by fleets.
  Whether 31 s of chords is right, or the threshold should rise, is a taste call for Derek.
- **Bells.** 267 lineage-first bells (the first test on each new lineage), with their rings; in March the bells and
  nation-first octaves are the only pitch variety. 5 nation-first doublings (Claude, Codex, automation, plus human and
  ChatGPT).
- **Legend (seen).** Rows enter in order human (2011-08-25), ChatGPT (2023-04-17, tests 76 after the inferred
  non-git bursts, all `time` matches, none `path+time`), Claude (2026-01-20, not 2025-10: the earlier date is a Claude
  trailer in a third-party lineage), Codex (06-29), automation (07-03), local (07-18, stays at 0 tests, 135 launches with a
  seat), OpenCode (09-27, 0 tests, 0 launch windows). Generation chips (13): Claude 7 (opus-4 282 tests, sonnet-4 19, haiku-4 3, fable-5 175, sonnet-5 7,
  opus-5 126, and a bare `opus` with 2 tests from trailers that carry no version), Codex 2 (gpt-5 66, gpt-6 15), automation 4
  (cc-builder-2, omen-worker-1, am4-worker-1, ct). `major` granularity folds opus-4.5 to 4.8 into one chip. Local and
  OpenCode have no chip because chips enter at a first test.
- **Map (seen).** With the fixed-world camera the explored region cluster fills about a third of the map area at the end
  and 2 to 6 px dots read as a dim scatter; blooms are legible, lineage rings read as expanding circles at the far discs.
  A fit-known camera (slice 6) is needed for this to look like a map.
- **Dead rows.** Local and OpenCode rows show a 0 and nothing else because sparks and participations are slice 6; they
  read as broken until the radio layer exists.

## Deviations from STRATEGY (each with its reason)

- Camera `fixed_world` (the control arm), not `fit_known`: slice 6 builds the smoother; the map positions are screen
  pixels computed once from the packing.
- Regions are one dot per lineage (not lineage x host regions with tiles): tiles and the atlas are slice 4. Activity is per
  region and class group, not per tile; the same exact decay formula and checkpoints, as asked.
- MIRV and unified are only approximated: warhead blooms at each target region and pips on collapse-free launches;
  the converging unified lines and the split beam (slice 5) are not drawn. Sound: MIRV departure at -6 dB plus a 60 ms
  octave pip per warhead, unified an octave down at 1.5 x length, as in section 6.
- Collapse is audio-only plus the luminance cap; the per-region visual merge is slice 5.
- Hum is gated to zero when no commit falls in the second (STRATEGY's formula never reaches silence); static likewise.
- Offload crackle, repo-born bells without a test, the radio band, tallies per surface, bridges, harbours, coda card:
  not in slice 3.
- Cut envelopes scale by m^(-1/2) = 0.352 for tone length, bloom life and bells; the legend's "new chip named for 3 s"
  scales with it (about 1 s in the cut).
- Corpus pinned in `cache/`: the merge changed under the run (see LAP-01 addendum).
