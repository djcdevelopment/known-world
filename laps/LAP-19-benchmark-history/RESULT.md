# LAP-19: recovered benchmark and fleet history

The animation now includes 257 distinct dated benchmark runs, 629 paired HEARTH invocations and 23 dated
fleet-result observations. Five activity rows add their rhythms to the score; exact known project links pulse
on the map. Counters retain separate units so the same work is not added repeatedly to a single grand total.

At the pinned October 9 snapshot: 22,672 local dispatch records, 1,057 Gemini calls, 160 Antigravity conversation
observations, 56 research attempts, 52 investigations and 95 findings. Git totals show 18,447,909 line changes.

## What was recovered

- 299 thinking-run manifests fold to 257 runs after removing 42 copies; 543 distinct execution jobs.
  Actual enclosing run intervals overlap at most twice. These are recorded runs, not accepted capabilities.
- Canonical HEARTH lookups recovered all 565 requested jobs: the 543 above plus 22 linked from other run formats.
  Combined with the 64 Windows archive invocations, there are 629 distinct intervals: 625 succeeded, four failed.
  Peak recorded invocation overlap is five; this is partial history, not GPU utilization or the machine's ceiling.
- 21 Windows campaign result observations plus two dated Conductor results from an FX99 backup. Their timestamps
  are explicit promotion-risk computations, not guessed completion dates. Archive location does not place work
  on a host or map region. Native plan IDs dedupe observations across sources.

## Remaining source limits

AM4 retains 4,533 valid image-benchmark results across six model labels, but their execution dates were discarded.
The result/manifest format and benchmark SQLite tables lack timestamps; ComfyUI's timestamped asset tables are
empty. Seven linked trace IDs were unavailable from the surviving Jaeger endpoint, which lists only its own
service. These results remain documented coverage and do not appear at invented dates.

Derek identified Conductor as an old AM4 Windows Hyper-V VM, possibly migrated to Linux or FX99. Bounded read-only
searches of both hosts, backup roots, FX99 attached-drive directories and mounted Windows VM locations found no
VM disk or matching September MechNet plan archive. Six older conductor results survived in FX99's omen-linux
backup; none matches the missing plans. The original hostname does not resolve. No VM was started or mounted.
An offline disk or another backup could still contain that history; no further operator action is needed for
the integrated preview. Detailed bounds and gaps live in `corpus/activity/historical-coverage.json`.

Antigravity remains last-update observations, with one invalid date and 14 observations after the pinned cutoff
excluded. Its Windows WAL may contain additional history. No conversation bodies, titles or summary BLOBs were
collected. Broad discovery limits from the first hunt remain explicit in EVIDENCE-HUNT.md.

## Validation and artifacts

Six focused fixtures passed in 0.018 seconds. Source records reconciled against decoded counters at frames
1800, 2427 and 2520; independent interval comparisons matched both overlap peaks. The reusable worklist reproduced
all 565 job IDs and source links. Final numeric line changes decoded exactly. System Python lacked NumPy, so the
fixture command was rerun successfully in the existing project environment.

Landscape and portrait stills rendered without browser errors. The final eight-second excerpt rendered 240 frames
in 8.132 seconds. Audio SHA-256 and all 845 launches match the earlier build; no new benchmark or full film render
was run. This is a local preview; the published film was not replaced.

- [Landscape](stills/final-02520.png) and [portrait](stills/portrait-02520.png)
- [Eight-second preview with sound](excerpt-final/history-8s.mp4)
- `build-cut/`: full 90-second interactive data, audio and receipt
- `validation.json`: source reconciliation and bounded checks
- HEARTH engineering receipt: `br-20261010-143007-ec99eaee`

Rebuild: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I compile/build_cli.py --cut 90 --out laps/LAP-19-benchmark-history/build-cut`.
The repeatable discovery and canonical recovery workflow is in EVIDENCE-HUNT.md.
