# LAP-06 radio and camera: result (2026-10-09, builder Sonnet 5.5, work item w-26069fe96149)

Code: `render/radio.js` (beams, rings, sparks, beacons, HQ ring), `render/panels.js` (surface tallies, mirrored band), `compile/camera.py`
(final form), `compile/series.py` (beams, rings, band, HQ track), `compile/synth.py` (hum, static, offload crackle, repo-born bells).
Receipts: `receipt-build.json` (corpus hashes, compile twice, camera and HQ stats), `receipt-verify.json`, `receipt-stills.json`;
`ct receipt` `receipt://91bc6e257fc451b1c55aa2a7`.

## What is drawn

- **Comms beams** HQ to region: per frame the 10 strongest session buckets (4,953 in the full piece), each fading over 12 frames; colour of the
  session class. **ChatGPT rings** (103) from the void where omen-c will rise, one per 0.3 s of traffic. **Offload sparks** one arc per seat per frame
  HQ to the seat beacon (omen-linux, AM4, FX99); beacons brighten with the recent offload rate.
- **Band** (bottom 120 px, 20 s): chatter above by class (ChatGPT, Claude, Codex, OpenCode stacked, log scale against each series' own ceiling),
  commits below in warm grey, offloads an ember hairline on the centre line, era ticks. The 2026-04 chat hole is a flat band.
- **Surface tallies** (left): C:, E:, linux, AM4, FX99 and GitHub rows in entry order, tests in 28 px figures, commits and files below; GitHub counts repos risen.
- **Bridges** light when both ends exist (their frame is the later endpoint's first frame), hairline at the lower activity of the two; harbours land the day
  the home region and its island both exist; spurs (224) decay to stubs at the 30 day half-life; notches (316); ruins hatched.
- **HQ ring** glides 2 s between surfaces; uncaptioned. It sits on omen-e from 2026-05, omen-c, omen-e again, and crosses to omen-linux on **2026-09-28**
  (frame 19,276). STRATEGY and the task expected 2026-09-27: the 7 day window with 20 percent hysteresis lags a day; `hq_window_days` is the lever.
- **Audio** as specified: hum 55 + 110 Hz at -36 + 6 log10(1 + commits/s) dBFS ceiling -24 from the first commit on (no longer gated to zero);
  static per class by log message rate (ChatGPT 1.2 kHz, Claude 2.0, Codex 2.8, OpenCode 3.6, local 0.8) ceiling -18, from each class's first message;
  offloads 1 ms clicks below 40 per second (301) and an 0.8 kHz roar above (204 frames); 54 repo-born bells at -12 dB without a bloom.

## Camera (measured)

| Measure | Value |
|---|---|
| Lookahead / smoother | 6 s box, forward-backward filter tau 4 s, clamped to the revealed box at f |
| Scale (px per world unit = hex circumradius) min / max | 1.80 / 3.88 (cap 40 never binds: the first regions are scattered across the world) |
| Era C start / before coda | 2.11 / 1.80 |
| No zoom-in from era C | scale non-increasing through era C until the coda: true |
| Revealed non-ruin tile centres outside the view (sampled every 15 frames) | 0.0 percent |

Ruins are outside the box (deviation, slice 4); islands are in it.

## Stills (`stills/`)

`migration-2026-09-25.png`, `migration-2026-09-27.png`, `migration-2026-09-29.png` (the HQ ring, bridges and the Linux continent across the sea),
`storm-2026-10-03.png` (offload sparks and the band at its loudest), `chatgpt-2025-06-01.png` (rings into the void). The luminance receipt reads fields
only 0.548, with launches 0.936.

## Deviations

- Crossing date 2026-09-28 (above). The Linux continent does not light as a block at the crossing: only 41 tiles are copy-revealed; 1,370 Linux tiles are
  native (first touched 2026), so the sea-crossing reads as the HQ ring and bridges, not a mass appearance. This is what the data holds.
- Sparks are drawn per seat per frame as an arc with a running dot (deterministic phase from the frame), not per call.
- I cannot listen; audio is measured, not heard.
