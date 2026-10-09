# LAP-02 clock and sync: result (2026-10-09)

Code: `compile/clock.py` (schedule, glides, cut), `compile/audio.py` (skeleton), `compile/build_data.py`,
`render/{index.html,data.js,border.js,main.js}` (ticker-only), `export/{frames.mjs,encode.py,probe.py,run.py}`,
runner `laps/LAP-02-clock-sync/lap.py`; receipts `receipt-probe10.json`, `receipt-all.json`, per-export
`out/*/receipt.json` with per-frame sha256 (`frame-hashes.txt`). Videos stay in `out/` (not committed).

## Clock (defaults, snapshot 2026-10-09T12:45:04Z)

| Measure | STRATEGY | Built |
|---|---|---|
| Frames / seconds | 20,646 / 688.2 | **20,647 / 688.242** (story 668.242 + intro 2 + coda 18; 688.242 x 30 = 20,647.3) |
| Era lengths A / B / C | 46.7 / 87.5 / 534.1 s | 47.2 / 87.7 / 533.3 s (the glide windows straddle the base boundaries) |
| Boundary seconds B / C | 48.7 / 136.2 | 49.21 / 136.94 (the boundary date is reached inside its 3 s glide) |
| 90 s cut | m = 8.05 | m = 8.0511, 2,700 frames, intro 1 s, story 83 s, coda 6 s; ticker `1 day = 0.30 s · x8.05` |

Glide: log-rate smoothstep, 3 s, integrated at 1 ms. Placement is solved so both window ends sit exactly on the base
schedule (bisection), so every frame outside the windows and the total are the base values; the rate is continuous
into the window (era mean rates). The strategy's "centred on the boundary" cannot also keep the total (centred
glides shorten the piece by 1.66 s, measured), so the boundary date lands 0.5 to 0.8 s off the base second instead.
Month and day lengths are exact per calendar unit outside the windows.

## Pipeline (CDP captureScreenshot PNG optimizeForSpeed, one Chromium per worker, K = 10 workers, nice, ffmpeg x264 -threads 3 per worker)

| Export | Frames | Wall (frames) | ms per frame effective | capture ms per frame per worker (median) |
|---|---|---|---|---|
| 10 s probe export (frames 0 to 300, 30-frame segments) | 300 | 1.81 s | 5.24 (startup-dominated) | 33.8 |
| 90 s cut, ticker only, run A | 2,700 | 13.26 s | 4.82 | 42.6 |
| 90 s cut, run B | 2,700 | 12.62 s | 4.59 | 41.6 |

The ticker is nearly free to draw, so these are the floor of the pipeline under bench27 load (the spine's spike
measured 7.8 ms at K = 12 on a 20k-tile page); real content is slice 3's number. Resume by segment verified (a rerun of
the 10 s export skipped all segments).

**The 90 s cut rendered twice: all 2,700 frame hashes equal** (combined sha256 `f15c60ad479b53d1...` both runs).
Page errors: none.

## Sync probe (white frame at f_p = 15, 1 ms click at sample 15 x 1,600 = 24,000)

| Check | Result |
|---|---|
| Video frames | 300 of 300 (cut: 2,700 of 2,700) |
| Container duration | 10.000 s (cut 90.000 s) |
| Decoded white frame | frame 15 only, t = 0.5000 s |
| Decoded click onset / peak | sample 24,000 / 24,000, t = 0.5000 s; **delta 0.0 ms** (limit 1 ms) |
| Audio samples decoded | 480,256 = 480,000 + 256 (cut: 4,320,256 = 4,320,000 + 256) |
| MP4 edit lists | audio media_time 1,024 (AAC priming removed on decode); duration exact |

The 256 extra samples are the AAC encoder's final-frame padding; the edit list's duration trims it in players and
`ffmpeg -t` trims it on decode. The probe's pass rule allows 0 to 1,023 tail samples, exact start, and exact container
duration. **ffprobe is absent on this host**: `ffmpeg -i` for duration and a raw decode for counts stand in, plus a
direct read of the `elst` atoms.

## Deviations and notes

- Fonts: JetBrains Mono is absent; Chromium falls back to `monospace`, which `fc-match` resolves to DejaVu Sans Mono.
  Hashes hold per Chromium build (1248) and this font; a machine with JetBrains Mono will render different pixels.
- Chromium launched with `--force-color-profile=srgb --font-render-hinting=none --disable-lcd-text` for stable text.
- `audio.py` is the skeleton: seeded PCG64 noise at -70 dBFS, soft-knee limiter, the sync click; tones are slice 3.
- The probe white frame is drawn when `probe_f` is set in the data (intro frame 15 by default).
