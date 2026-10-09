# LAP-05 shapes: result (2026-10-09, builder Sonnet 5.5, work item w-26069fe96149)

Code: `render/launch.js` (all shapes, merge), `compile/build.py` (beam, split, warhead, converge tables), `compile/synth.py` (sounds, unchanged
from slice 3 except bells and offload crackle). Runner `lap.py` (build stills verify). Receipts: `receipt-build.json` (corpus hashes,
compile twice, picked launches, shape counts), `receipt-verify.json`, `receipt-stills.json`; `ct receipt` `receipt://3dca05f0ddb7e50b81436097`.

## What is drawn

- **MIRV** (171 launches, 590 warheads, 152 aimed at spurs): one beam from the HQ, 0.45 s (x 0.35 in the cut) to the split point at 60 percent of
  its path toward the targets' centroid, then warheads on quadratic arcs, landing in real order compressed into `warhead_spread_s`, each a bloom
  of the band set by its share of the lines (band = launch band + floor(log10 share), at least 1). Sound: the departure tone (summed band, -6 dB)
  at the launch frame, a 60 ms pip an octave up per warhead at its landing frame, panned by the target's screen x under the camera.
- **Unified** (11, all with sources): lines converge from the sites of the MIRV warheads it consolidates (up to 24) over 0.5 s, then a bloom one band larger
  (the compile raises the band, capped at 6); tone an octave down at 1.5 x length.
- **Inferred** (37, ChatGPT time-matched): a hollow core (centre alpha 5 percent) and an open ring with a gap, same hue family.
- **Collapse** (295 frames of the full piece, 1.4 percent): blooms of one region merge into one bloom of the largest band (+1 band at 4 or more
  members), colour of the largest member; beams and converging lines are not drawn in collapsed frames (no staggering, so the merge reads as one).

## Stills (`stills/`)

MIRV (human, 5 warheads, band 4, launch frame 6,907): `mirv-a` (3 frames in, beam travelling), `mirv-b` (split, warheads leaving), `mirv-c` (last
landing + 4). Unified (human, 2 sources, band 5, frame 5,031): `unified-a` (converging, 11 frames before), `unified-b` (2 before), `unified-c` (bloom).
Both picks sit in 2026-03 and 04 when the camera is wide; a still shows a beam as a thin line and warheads as arcs.

## Receipts

| Check | Result |
|---|---|
| Compile twice | kw-data.js and audio byte-identical |
| Order independence (30 frames, two Chromiums, shuffled) | 30 of 30 equal |
| Luminance, 90 s cut, 6 busiest sampled frames | fields only 0.548 (limit 0.55); with launches 0.913 (launches own 0.55 to 0.95) |

## Deviations

- Beams and converging lines are suppressed in collapsed frames; only the merged bloom shows.
- A MIRV has no bloom at its origin, only at the warheads (the departure is audible, the landing is visible).
- I cannot listen; the audio is measured (pips 517, tones 879, bells 269 incl. 54 repo-born at -12 dB).
