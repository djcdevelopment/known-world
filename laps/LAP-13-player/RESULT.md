# LAP-13 the player: result (2026-10-09, builder Sonnet 5.5, work item w-26069fe96149)

Code: `compile/{camera,marks,tiles,build}.py`, `compile/params.json`, `render/{player,data,main,fields,panels,border,stream,card}.js`, `render/index.html`, `export/{still.mjs,hashpage.mjs,serve.py}`, runner `lap.py` (build stills arms compat cut full).
Receipts: `receipt-{build,stills,arms,compat,export-cut,export-full}.json`; `ct receipt` build `2fbb`-series: cut `receipt://9d1c866aed2a1977e2e28e47`, full export `receipt://a5c4883dc16e6f8f70d42a19`.
Videos (git-ignored): `out/full/final.mp4` 102.7 MB, `out/cut/final.mp4` 23.1 MB. Player page: `render/index.html` (see Player).

## Corpus (pinned in `receipt-build.json` `inputs`)
Final compile ran after `corpus/MERGE-1e-DONE.md`: events.ndjson sha256 `b1ee0cf8fbb0...` (the value in DONE.md), repos `20640180...`, relations `9e7c60ce...`, all eight hashes in the receipt.
Compile twice (separate processes), full and cut: kw-data.js and audio byte-identical. 30 frames re-rendered in a fresh Chromium in reverse order equal the export hashes: 30 of 30, full and cut. Sync probe delta 0.0 ms, page errors none.

## Camera steering (compile/camera.py)
Box = warm tiles (weight of the trailing `camera_memory_days` window, 365 in A/B, 120 in C, evaluated at the frame's era, reaches `camera_tile_weight_min` 3.0 AND at least three touches' worth, or a births burst) + every launch target (same window) + seat beacons from first offload (frame 14099) + islands once the steering span reaches 120 + the HQ only from era C (frame 4109) or a launch within `camera_hq_launch_units` 20 of it (none before C). Pull back only, fill 0.6 to 0.8 as built. The page also receives the box dimensions (`camera_box`) so another safe area refits the same box.
Coordinator correction applied: first version had the HQ track in the box from the join; the "three touches" rule was added because one 360-file record made a lone far tile steer.

| Full piece (30 fps) | before correction | after correction |
|---|---|---|
| scale px/hex at frame 0 / 394 / 543 / end | 109.99 / 109.83 / 109.41 / 1.65 | **109.99 / 109.86 / 109.52 / 1.65** |
| tight start (scale within 90 percent of the opening) | 30.0 s (frame 900) | **30.8 s (frame 925)** |
| within 50 percent / within 25 percent | 38.1 s / 58.2 s | 39.5 s / 59.0 s |
Cut (90 s): scales 36.1 / 2.38 / 2.14 / 1.65, tight start 0.4 s (90 percent), 2.3 s (50 percent).

The HQ rule changed nothing in the numbers: the HQ was not what widened the 2023-11 view. **The ring at (816, 926) in `2023-11.png` is the first-test ring of a launch** (frame 1990, 2023-11-03, yield band 3, a non-git directory lineage far from the cluster, at world (88, 184)); the ring is its bloom. Launch targets are in the box by rule, and that launch sits 180 units from the cluster, so the camera pulls back from about 2023-09 (6 s look-ahead plus smoothing) and the cluster is small at 2023-11. A second reason is that at 2092 (2023-12) the big cluster (254 touches, 31 bursts) re-warms, which joins the islands. With launches not steering (`camera_launch_steer=none`, arm in `receipt-arms.json`): scale 45 px/hex at 2023-11 (cluster box 8.7 x 12.6 units, about 390 px wide), tight start 31.0 / 40.2 / 88.0 s. **Left as the default `all` because the rule lists launch targets; one switch to flip (open question 1).**
Arms: `revealed_all` (slice-9 steering, this corpus) 21.8 / 29.4 / 32.1 s; `weight_min_6` 52.0 / 59.5 / 62.3 s.

## Marks (compile/marks.py, marks.json; 31 marks: era 2, surface 6, nation 7, migration 1, storm 1, regime 15)
| kind | date | frame | label |
|---|---|---|---|
| nation | 2011-08-25 | 68 | human enters |
| surface | 2011-08-25 | 68 | new continent: GitHub |
| surface | 2015-08-10 | 543 | new continent: linux |
| surface | 2020-12-22 | 1187 | new continent: E: |
| era | 2023-04-01 | 1477 | era B begins |
| nation | 2023-04-17 | 1501 | ChatGPT enters |
| surface | 2024-10-26 | 2872 | new continent: C: |
| regime | 2025-04-01 | 3262 | launches: accelerating → accelerating (steeper) |
| regime | 2025-06-05 | 3420 | files: accelerating → slowing |
| surface | 2025-07-01 | 3487 | new continent: AM4 |
| regime | 2025-07-05 | 3497 | files: slowing → linear |
| regime | 2025-11-17 | 3827 | files: linear → accelerating |
| regime | 2026-01-18 | 3978 | commits: accelerating → accelerating (steeper) |
| nation | 2026-01-20 | 3983 | Claude enters |
| regime | 2026-02-13 | 4044 | files: accelerating → accelerating (steeper) |
| era | 2026-03-01 | 4109 | era C begins |
| regime | 2026-03-17 | 5237 | commits: accelerating → accelerating (shallower) |
| regime | 2026-03-17 | 5237 | files: accelerating → slowing |
| regime | 2026-03-17 | 5237 | launches: accelerating → linear |
| regime | 2026-04-16 | 7397 | files: slowing → linear |
| regime | 2026-04-16 | 7397 | launches: linear → linear (shallower) |
| regime | 2026-05-17 | 9629 | launches: linear → accelerating |
| regime | 2026-05-22 | 9989 | files: linear → slowing |
| regime | 2026-06-21 | 12149 | files: slowing → accelerating |
| surface | 2026-06-22 | 12265 | new continent: FX99 |
| nation | 2026-06-29 | 12753 | Codex enters |
| nation | 2026-07-03 | 13018 | automation enters |
| nation | 2026-07-18 | 14099 | local enters |
| regime | 2026-09-10 | 17981 | files: accelerating → linear |
| nation | 2026-09-27 | 19239 | OpenCode enters |
| migration | 2026-09-28 | 19277 | the migration: HQ crosses to linux |
| storm | 2026-10-03 | 19637 | the offload storm begins |

Regime fit: log10(cum+1) on a daily grid, binary segmentation, min segment 365.2 d (A), 30.4 d (B), 30 d (C), words from the raw cumulative (`idle`, `linear` = constant rate, `accelerating`, `slowing`; same word on both sides gets `(steeper)` or `(shallower)`). Offload storm: first day the trailing 7-day offload count reaches 25 percent of its peak.
The ticker hairline (exported video) carries one 1 px kind-coloured tick per mark and a playhead, drawn at y 62 over the whole timeline (portrait: y 51).

## Player (`render/index.html`)
Serve over http (a file:// page cannot fetch the WAV): `.venv/bin/python -I export/serve.py 8765`, then
`http://127.0.0.1:8765/render/index.html?data=../laps/LAP-13-player/build-full/kw-data.js` (audio defaults to `audio.wav` beside the data; `&audio=none`; on file:// the note button opens a picker). Query: `f=` start frame, `s=` speed index, `play=1`.
- Transport inside the radio band plate (landscape; no safe-area overlap) or its own plate under the band (portrait): `--  -  play  +  ++`, speeds 1, 1.5, 2, 3, 4 (`--` to 1, `++` to 4), speed shown, date shown. Keys: space, Left/Right seek 5 film s, `[` `]` speed, Home/End.
- Scrubber: era segments shaded, hashmarks from marks.json (hover: date and label; click on a mark seeks to it; drag seeks). Nation rows, surface rows and stream lanes show names on hover; portrait swatches by tap.
- Stream header rule: a lane is named only when its pitch is 18 px or more; 18 to 30 px two staggered rows of 7 characters, 30 px or more one row of 14; the rest keep their entry label and show on hover.
- Audio: compiled WAV, one AudioBufferSourceNode, playbackRate = speed (no pitch correction: 2x sounds an octave up). The film position is read from the audio clock minus the reported output latency, so picture and sound cannot drift apart: bound = one frame (33 ms) plus the latency uncertainty; measured over 3 s at 1x, 2x, 4x in headless Chromium the position trailed the audio clock by 0 to 43 ms (one rAF step at 4x); seek and speed change re-anchor the node (seek to 1500 landed within 11 ms). The decoded 90 s cut is 35 MB; the full WAV decodes to 264 MB (heavy on a phone).
- Speed never touches the export (the export loads no player code); a changed window size reloads the page keeping place and speed.

## Portrait (viewport taller than wide; `hud_portrait`)
Logical frame 450 px wide, height from the aspect; ticker 56 px top (date, rate, totals, hashmark hairline); a 30 px strip of nation swatches with test counts that expands on tap into a compact nation panel (mini rows when short); a `surfaces` tap opens the tallies (exclusive with nations); band 84 px and transport plate 64 px at the bottom; stream hidden (`stream: hidden` is the only implemented value); camera refit from `camera_box`; tally card has a portrait layout. Stills at 390x844 and 1080x1920 in `stills/portrait-*`.
**1920x1080 export path unchanged:** 30 frames rendered with the slice-9 renderer (git archive `0054343`) and with the new page in `compat=slice9` mode (no hairline, old header) on the same data: **30 of 30 equal** (`receipt-compat.json`). The default page differs (hairline, header rule) by design.

## Timing (10 workers, nice)
Full 20,656 frames: frames wall 227.2 s, with concat, mux, probe, re-hash **273.5 s (4.6 min)**, 10.98 ms per frame (before correction 271.2 s). Cut 2,700 frames: 23.1 s / 29.4 s. Compile 65.7 s full, 4.7 s cut.

## Deviations
- **Slope unit:** the literal reading (log10 per the era's rate unit: year, month, week) finds 0 regime marks at 0.5 and 1 at 0.25; the default is `marks_slope_unit: year` (per year in every era), 15 marks. Arm `era` kept.
- Constant-rate words read `linear` (the spec examples use both `linear` and `steady`).
- A tile needs three touches' worth besides the weight (a single heavy record is a lone file unless a births burst).
- Landscape wider than 16:9 widens the logical frame (clamped 1440 to 2560); the page reloads on resize.
- Portrait stream hidden, not a strip.
- The tight start under this corpus is far longer than LAP-12's 2 s because the corpus changed (1e) and the steering is warm-only; the pull-back runs 2020 to 2023 and reaches world scale by 2023-11.

## For Derek to decide (counts only)
1. Launch targets steer the box (default) or only warm tiles (`camera_launch_steer=none`): 1 switch; it decides whether 2023-11 is tight.
2. `camera_tile_weight_min` 3.0 or 6.0: 1 value (tight start 30.8 s vs 52.0 s).
3. `marks_slope_unit` year or era; threshold 0.5.
4. Portrait stream: hidden or a strip: 1 build.
5. Audio fetch needs http: serve script or a file picker: 1 choice.
