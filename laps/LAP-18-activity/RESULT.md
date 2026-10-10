# LAP-18: recorded execution and research activity

The default preview now shows dated Antigravity conversations, Windows HEARTH execution history and the lab
research registry. New score rows show their separate rhythms; thin map rings identify exact workspace matches
for conversations and the research registry's owning repository. They imply neither code changes nor model
attribution. Landscape and portrait counters show the same evidence. The prior sound and launch weights remain.

## Final totals at the pinned 2026-10-09T15:41:09Z cutoff

| Measure | Count | Meaning |
|---|---:|---|
| Line changes | 18,447,909 | 15,931,735 additions + 2,516,174 removals; counted git numstat, uncapped |
| Local HEARTH calls | 22,672 | Dispatch records with evidenced local backends; excludes 88 tool observations |
| Gemini HEARTH calls | 1,057 | Existing Gemini backend records, preserved from LAP-17 |
| Antigravity conversations | 160 | One observation at each conversation's last recorded update, not creation |
| Windows HEARTH executions | 64 | 61 succeeded, three failed; paired invocation endpoints, July–August slice |
| Peak recorded invocation overlap | 2 | Exact timestamps, half-open intervals; not the lab's ceiling or GPU utilization |
| Research attempts | 56 | Distinct native registry object IDs at first recorded appearance |
| Research investigations | 52 | Distinct registry objects, separate from attempts |
| Research findings | 95 | Finding records, not automatically accepted capabilities |

The former line cap reduced the world counter to about 7.9 million. Numeric totals now use uncapped numstat
and float64 storage; the 20,000-line launch-yield cap still bounds motion. The ticker labels cumulative file
touches and line changes explicitly. The local nation row retains all 22,760 offload records, now labelled
records; the new HEARTH dispatch counter excludes observations that may duplicate an actual call.

## Coverage

The Antigravity summary stores contain 175 rows: one has an invalid zero date, and 14 valid observations lie
after the film's pinned cutoff. The 160 in-range conversations are not a complete timeline of their messages;
their last-update timestamps are shown as such. The Windows store has a WAL sidecar; immutable SQL reads may
omit its newest rows. No message, preview, title or summary BLOB was selected. Seventy-five conversation/project
links and 203 registry/repository links collapse into 67 frame/region activity pulses. Unknown projects stay
off the map; an exact workspace match is required.

AM4's `results_full/meta` archive has 4,533 distinct result job IDs across six model labels, plus 17 invalid JSON
files. Those valid results contain 103,155.960 summed recorded wall-seconds, which is not elapsed time or GPU busy
time. Neither the inspected result format nor its manifest retains execution timestamps. They remain undated
coverage in `corpus/activity/am4-benchmark-coverage.json`; no new benchmark was run. The inspected MechNet schedule
has a dated completion observation, but its `lap-fx99`/`lap-am4` IDs do not match either result's native plan ID.
No execution count or date was invented for that join.

## Validation and preview

Four focused fixture checks passed in 0.011 seconds: half-open/empty intervals, metadata-only conversation
dedupe and invalid dates, exact project joins, and unpaired execution endpoints. Source aggregates reconciled
to decoded counters at frames 1800, 2427 and 2520; raw numstat matched the final float64 counter exactly. The 7B
FX99 review found no concrete chronology bug; its scope and frontier verdict are saved in `local-review.json`.
No generated code was applied.

Two builds took about four seconds each. Stills in both orientations and an eight-second excerpt rendered
without browser errors. Audio SHA-256 and the 845 launch count match LAP-17. The excerpt was refreshed after
the local-dispatch counter correction; no full video export or publication was performed.

- `stills/final-02520.png`: final landscape preview, complete snapshot counters
- `stills/portrait-02520.png`: portrait preview
- `excerpt-final/activity-8s.mp4`: eight-second excerpt with the existing soundtrack
- `build-cut/`: interactive data, audio and compiler receipt
- `validation.json`: source reconciliation and focused-check evidence
- HEARTH receipt: `br-20261010-141148-30ab5f21`

Rebuild: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I compile/build_cli.py --cut 90 --out laps/LAP-18-activity/build-cut`
Refresh sources into a new sidecar with `python3 collect/knownworld/activity.py --out corpus/activity/NEW-ID.json`,
then set `activity_file` to it. Workspace joins are pinned to the `repos.json` hash; a changed source map requires
recollection. Use `--set activity_file=null` for a deliberate comparison without the sidecar.
