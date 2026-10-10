# Evidence hunt: make the scale of AI development felt

Derek's direction, 2026-10-10: the animation expresses the scale and magnitude of local AI and AI development,
including how his own work scaled. The map, score, sound and counters should reveal that change together.
Goal `G-known-world`. Receipt `br-20261010-134823-70316e83`.

## What we need to see

| Question | Measure | Visual possibility | Required evidence |
|---|---|---|---|
| How much was built? | commits, file touches, raw line changes, distinct projects | expanding land and accumulating counters | git IDs, numstat, filesystem provenance; copies folded |
| How fast did work arrive? | invocations, sessions, output tokens per story day | score density and activity pulses | event times, measured usage, explicit missing coverage |
| How much ran at once? | concurrent jobs/invocations; occupied hosts/models | simultaneous activity across territory, optional lab view | paired lifecycle starts/ends with IDs; actual placement |
| How widely did it spread? | projects, hosts, models, clients, collaborators | geography, connections, model entries | stable identities, relationships and first dated evidence |
| How much did the lab explore? | distinct trials and configurations; repeats per regime | a research region with accumulating experiments | campaign/run/trial IDs and configuration records |
| What useful capability accumulated? | reviewed findings and accepted deliveries, corrections retained | persistent discoveries after activity subsides | reviewer verdicts, revisions and links to source evidence |

Totals and rates are separate. A logarithmic visual scale can keep the map legible without capping the numeric
total. Line changes are not current lines of code; file touches are not unique files. Tokens are activity, not
quality. A completed inference is not an accepted delivery. Hardware presence is not utilization.

The film stays in 2026. Discovery may inspect earlier records to recover provenance and identity; earlier events
do not silently enter the year's counters. Client and model are separate attributes: Antigravity can run a model
that also appears through another client. One event has one identity and several useful attributes, not two counts.

## The repeatable workflow

1. **Enumerate mechanically.** `collect/discovery/roots.json` is the source registry. The scanner lists directories,
   git markers and structured-file counts; it never opens source file contents. Each root has depth, time, file
   and candidate limits. Broad roots find leads; focused child roots resolve gaps. Roots on the same host/mount
   run serially, with at most four host groups active. Remote work uses the same scanner over read-only SSH.
2. **Give local scouts small packets.** `prepare_scouts.py` makes one bounded packet per root. Local models get
   directory metadata, approved source maps or schema probes through HEARTH `files=`, never arbitrary transcripts.
   Their task is to propose concrete next evidence, not invent the missing fields. Prefer the utility family for
   a small packet; use reasoning for cross-source reconciliation. The door selects the live local provider.
3. **Review the leads.** Every response is a candidate. A frontier caller checks paths, counts, ID/time semantics
   and privacy. Accept individual leads, not an entire plausible report. Record actual model/backend/job, token
   cap, substance verdict, form issues and rejected claims. No cloud fallback when a local lane refuses.
4. **Inspect structure, then follow evidence.** `probe_evidence.py` accepts explicit paths only. SQL probes select
   schema and counts, not data/BLOB values; bounded JSON probes emit keys/types, never scalar values. Source maps
   locate raw evidence but do not become measurements. Follow-up roots are added with their reason. No automatic
   execution of a model's proposed shell command or path.
5. **Collect through a source-specific allowlist.** Before a new collector emits animation events, define its
   allowed fields, timestamp meanings, stable IDs, dedupe keys, source authority and uncertainty. Reuse the
   existing collectors for git/Claude/Codex; do not replace them with file/line counts. The recipe table below is
   the backlog, not a claim these collectors have already been built.
6. **Reconcile and preview.** Preserve request → job → invocation → artifact → review links. Fold copies; retain
   retries as attempts. Count observations separately from unique work. Compare one late-date still and an
   eight-second excerpt before a full export. The next visible change must answer one question in the table above.

Models do not have filesystem tools on `local_generate`. The scanner/prober acts as their eyes, the scout selects
promising leads from the packet, and the frontier validates/follows those leads. This keeps searches reproducible
and bounds both model context and operator review. Stop a scout role if review costs more than doing its task directly.

### Run discovery

From `/home/derek/work/known-world`, choose a NEW output directory for each inventory:

```bash
python3 collect/knownworld/discover.py --roots collect/discovery/roots.json --out corpus/discovery/NEW-ID
python3 collect/knownworld/prepare_scouts.py --inventory corpus/discovery/NEW-ID --out corpus/discovery/NEW-ID/packets
python3 collect/knownworld/probe_evidence.py --roots collect/discovery/roots.json --sources PATH-TO-PROBE-WORKLIST.json --out corpus/discovery/NEW-ID/schemas.json
PYTHONDONTWRITEBYTECODE=1 python3 collect/check_discovery.py
```

Use `--only SOURCE-ID ...` for a focused scan. `complete` means complete within the declared depth/exclusions,
not a whole-disk claim. Missing, unreadable and budget-limited sources remain explicit. Symlinks are not followed.
Do not rescan all roots merely because one needs another pass. The inventory preserves the scanner and root
configuration and their hashes. Source files, mounts and immutable experiment directories are never written.

`collect/discovery/scout_workflow.js` runs in Codex's `functions.exec` tool environment. Its worklist is
`collect/discovery/scouts.json`: set the task receipt, packet paths and a fresh destination. It preserves existing
candidates, caps parallel calls at two (one in the current utility-lane worklist), and flags cap-reaching outputs
for review. It dispatches local calls only. It does not turn a report into a verdict or execute its suggestions.

## Collection recipes, in priority order

| Priority / source | Known way to look | Extract / join | Time and counting rule | Display use |
|---|---|---|---|---|
| 1. HEARTH execution | Windows `hearth-var/execution/projection.sqlite`; authorized execution APIs/source schema for current Linux | events: `event_id`, `request_id`, `job_id`, `invocation_id`, `event_type`, `timestamp`; job status | pair invocation.started with succeeded/failed by invocation ID; half-open intervals; incomplete spans explicit | actual concurrency, dispatch/completion rate, call vs job totals |
| 1. HEARTH dispatch | existing Linux/Windows ledger collector | event ID, caller, executing backend/model, measured usage; propose stable job links through approved schema | dedupe event copies; submission tool duration is not execution time; do not merge job ID with task ID | model flow and token activity; Gemini-backed calls |
| 1. Antigravity/Gemini | `.gemini/antigravity[-cli]/conversations/*.db`, Gemini roots and evidenced backend names | trajectory/cascade IDs, typed step counts; client separate from model | DB count is not session count; sampled schema has no plain timestamp/model columns; require documented metadata decoder before dating | recover missing client/model presence; undated evidence stays off the time axis |
| 2. Lab registry | `lab-rnd/research/state/events/*.json` | event sequence/at; record ID/kind/revision/status; later explicit evidence links | same object across revisions counted once for current state; preserve transitions for history | attempts, investigations, findings; distinguish review from execution |
| 2. Benchmarks | AM4 `~/bench`, local `lab-rnd/research/evidence`, Windows `hearth-var/experiments` and `work/benchmark` | campaign/run/trial/cell IDs, configuration, measured latency/throughput, outcome provenance | trial identity includes run; repeated cell IDs are not duplicates across trials; folders/summary exports are not new trials | experiment density, model × configuration breadth, regimes |
| 2. MechNet/planning | `lab-rnd/EVIDENCE.md` → planning-spine manifest, research notes → Windows `work/commandcenter/campaign/results` | schedule/plan IDs linked to execution/harvest records | scheduled work is not executed work; narrative and manifest are navigation only | planning fan-out and actual multi-project delivery |
| 2. Fleet/remote activity | AM4 `~/am4-fleet-node/results`, `~/am4bot/runs`; FX99 `~/fleet` | task/run IDs and measured lifecycle metadata once schema confirmed | snapshots are repeated observations, not new jobs; host copies folded | growing multi-machine activity |
| 3. Lever ledger | `lever-ledger/slices/*.jsonl` with source evidence | observation ID, dates, related IDs, source paths; reviewed interpretation | a knowledge entry is not an experiment; link originals and duplicates, retain withdrawn verdicts | accumulated learning that remains after activity fades |
| Existing. Git and non-git | current worklist + newly discovered git markers/directories | SHA lineage, numstat, timestamps, birth/update provenance | imported trees/copied timestamps and third-party history remain separate; raw counts vs visual scaling | territory and production magnitude |
| Existing. Claude/Codex/OpenCode | existing per-client extractors and newly found roots | native session/message IDs, usage, cwd, model and roles | streamed records and mirrors deduped; session span does not prove continuous computation | score, collaboration and attributed project activity |

Each collector must declare `source`, native ID, event time, observed/captured time, timestamp precision, host,
client, model/backend (or unknown), project mapping evidence, measured/estimated provenance, coverage and dedupe
rule. These are requirements for a future contract revision, not extra keys silently added to the current events.
No energy, dollar savings, human-hours saved or causal productivity multiplier is inferred from token/commit counts.

## First hunt, 2026-10-10

Evidence: [summary](corpus/discovery/20261010/SUMMARY.json), first inventory and focused follow-up under
`corpus/discovery/20261010{,-followup}/`; private packets and source paths are not a public export.

- **45 roots inspected:** 40 complete within declared bounds, four partial, one missing. **10,132 unique candidate
  directories** across hosts; this is a discovery count, not a work count. The broad Linux work, C: work, E: work
  and E: omen scans hit limits (C: also had two permission errors). Focused scans covered the promising lab/remote
  roots. AM4 `~/ai-bench` was missing; `~/bench` was found and scanned separately.
- **Windows execution:** 64 jobs, 573 lifecycle events, 125 artifact rows. July 31–August 19, 2026 snapshot:
  61 execution successes, three failures. All 64 invocation intervals pair; peak overlap is **two**, with
  1,854.216 summed invocation-seconds. This is a small historical slice, not the lab's ceiling, useful-delivery
  rate or measured GPU busy time. No WAL sidecar was present at inspection.
- **Research registry:** 849 event files resolve to 56 attempt objects, 52 investigations, 257 artifacts,
  95 findings, 34 questions, three goals and 18 decisions. Event dates October 1–5. Those are registry object
  counts, not 849 experiments or 95 proven capabilities.
- **AM4:** the benchmark inventory found 4,550 JSON files directly in `results_full/meta`, plus other benchmark
  groups. Fleet results and 82 bot-run JSONL files are additional source leads. Trials/models/times require
  schema-specific extraction; no experiment count is inferred from those files.
- **FX99:** a large `~/fleet/snapshots` history surfaced. Repeated snapshots must be folded into state changes;
  counting each snapshot as new work would inflate the story.
- **Antigravity:** 62 Linux and 113 Windows conversation DB files. Three DB schemas sampled per host; trajectory
  and step tables exist, timestamps/model names are not simple columns. No message/BLOB data was selected.
- **MechNet:** its research source map led to campaign results on the Windows C: copy. The Linux path named in
  that map is absent. A missing Linux folder was not evidence that the historical work did not happen.

Six local scout calls were used: four source/schema reviews and two narrowly scoped utility hunts. Reports,
actual route metadata and per-scout verdicts live under `corpus/discovery/20261010/scouts/`. Broad 27B prose was
useful for leads but required corrections; claims based on mtime, counts-as-parallelism, borrowed schemas and raw
transcript commands were rejected. The reusable worklist uses small source packets and constrained output.

Five focused scanner/prober checks cover credential exclusion, symlinks, no source opens during enumeration,
budget/missing status, output boundaries, scalar-value suppression and SQL counts without row/BLOB emission.
No full render or broad test campaign was run. No new evidence has yet been added to the published animation.

## Next collection slice

Start with execution lifecycles and Gemini dispatch identity: these have native IDs and timestamps already.
Then collect the lab registry and a representative AM4 benchmark format, using MechNet's Windows results as the
planning join. Antigravity metadata decoding is its own bounded investigation. Keep broad-scan gaps queued by
child directory; do not hide them behind the large number of sources already found.

Review the first integrated result as two synchronized states: the current map and the same moment with recovered
activity/counters. That will show whether the newly counted work makes the scaling visible before another full film.

## Integrated follow-up, 2026-10-10

LAP-17 added the 1,057 evidenced Gemini HEARTH calls. [LAP-18](laps/LAP-18-activity/RESULT.md) implements
`collect/knownworld/activity.py` and a pinned metadata sidecar for Windows execution intervals, the research
registry and Antigravity summary stores. The latter, unlike the individual conversation DBs, have explicit
last-update dates and workspace URIs: no BLOB decoder or transcript access was needed. These sources now drive
distinct counters and score rows, with conservative project pulses. Numeric line totals are uncapped while
launch weights remain bounded. The local HEARTH counter excludes 88 tool observations that may duplicate calls.

The AM4 archive resolves to 4,533 distinct valid result IDs, with 17 invalid JSON files; measured durations exist
but dates do not survive in the inspected result/manifest format. MechNet's inspected schedule/result IDs do
not match. Both remain explicit dating gaps. Next evidence would be an execution log keyed by those native
job/plan IDs, not another benchmark or dates inferred from filesystem metadata. Broad discovery gaps remain
those recorded above. The public film has not been replaced.

## Historical recovery completed, 2026-10-10

[LAP-19](laps/LAP-19-benchmark-history/RESULT.md) integrates the available dated benchmark and fleet evidence.
The latest sidecar is `corpus/activity/20261010-final.json`. Its coverage records are part of the compiler receipt.
The source gaps are documented in `corpus/activity/historical-coverage.json`; discovery is bounded, not a claim
to have searched every byte of every disk.

To repeat canonical execution recovery:

1. Run `python3 collect/knownworld/prepare_execution_jobs.py --out corpus/activity/NEW-worklist.json`.
   It selects native job IDs from run manifests and four explicitly named companion files, skipping prose fields.
2. Edit the input/output constants in `collect/discovery/recover_executions.js`, then execute it through Codex
   `functions.exec`. It reads owned jobs with `hearth.get_execution`, four at a time; it never starts inference.
   Only allowlisted lifecycle/model/usage metadata survives; unavailable jobs remain explicit.
3. Review the frozen recovery and set the collector's canonical API path to that reviewed file. Collect into a
   new activity sidecar and update `compile/params.json`. Keep prior snapshots for comparison.
4. Compile the 90-second data, render a late still and an eight-second excerpt into a fresh output directory.
   Use `.venv/bin/python collect/check_activity.py` for the six focused fixtures; no benchmark is required.

The reproduced worklist contains the same 565 native jobs and source-path links as the original recovery.
Forty-two copied thinking-run manifests collapse to 257 runs with 543 distinct jobs. Another 22 jobs come
from companion metadata for other run formats; their canonical invocations have dates, while enclosing run
dates remain unknown. These are separate views of existing work and are never summed into dispatch totals.

FX99 backup recipe: read only `~/backups/omen-linux/hearth-production/runs/*/conductor/result.json`, selecting
`plan_id` and `promotion.risk.computed_at` plus relative source path. Six results were found; two have explicit
dates. The reviewed metadata is `corpus/activity/fx99-conductor-backup.json`. Four undated records stay out of
the animation. None matches the two September MechNet plan IDs still being sought.

### Conductor GitHub mirror verified

Derek's GitHub lead resolves to the private `djcdevelopment/conductor` repository, documented in
`commandcenter-linux-flash/docs/conductor-github-sync.md`. Its sole current branch, `main`, points to
`aa7b2d81621db066f222dc6847329f59b83a612c`; its last push was July 3, 2026. All 36 GitHub commit SHAs match
the local mirror and the merged corpus exactly. The Windows mirror, migrated Linux mirror and GitHub clone
already fold into lineage `0a2dd31e35fa9ce6ee6518316bcc728a5feea44d`; adding another copy would add no history.
Evidence: `corpus/activity/conductor-github-coverage.json`. This verifies the current GitHub code history,
not completeness of the VM's later work or September run artifacts. Sync was manual, according to its source
documentation. Repeat with metadata-only `gh api` commit/branch lookups and compare native SHAs to the corpus;
no repository content, token or credential-store reads are needed.

## Windows research shapes recovered October 10

Follow `laps/LAP-22-windows-research/RESULT.md` and `corpus/discovery/20261010-windows-bench/`.
Search patterns now include `seat.physical-attempt.v1`, `run.record-attempt.v1`, explicit runner `started_at`/`finished_at`, native llama-bench `test_time`, source SHA references, and server timing blocks. Prefer retained native IDs over log totals; inspect archival `hearth/var/seats` as well as gateway ledgers. Preserve source timestamp derivation. Configuration measurements, physical attempts, runner campaigns and telemetry samples are different units. Derived score/receipt summaries and content SHA changes are leads, never extra attempts.

## Search by shape, including ignored and historical data

LAP-23 adds `collect/knownworld/hunt_shapes.py` and `recover_trials.py`. Search known Windows/Linux/AM4/FX99 roots by learned schema keys and format families, with explicit exclusions and source coverage. Include gitignored experiment outputs (`rg --files --hidden --no-ignore`). Use size only to choose a safe reader. Inspect representative metadata first, then parse complete recognized native families. Expand format detection when an uncovered source has a new shape.

When a public numeric export has `source_sha256` but no dates, trace its source through Git history rather than dropping it or assigning the export date. Verify both raw Git blob and CRLF checkout hashes. Memsplice recovered 59 removed artifacts this way, including 60 explicitly dated rows. Raw arrays and repeated native benchmark samples are measurable work; summaries, rescoring, telemetry, fake/dry adapters and mirrored exports are overlapping evidence. Report configurations, repeated trials, experiment records, native runner campaigns and direct inference separately. Surface verified undated result totals on the ending card with an explicit undated label, never place them on an invented date.
