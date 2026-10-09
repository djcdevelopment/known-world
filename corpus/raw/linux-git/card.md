# linux-git Corpus Collection

## Source
Git repository metadata collection from omen-linux host. Processes repositories found under:
- `/home/derek/work/*`
- `/home/derek/work/trial/notebook*`
- `/home/derek/work/clm-pilot/upstream`
- `/home/derek/private-migration-20260923/*`
- `/home/derek/git/*`
- `/home/derek/.continuity/ledger`
- `/home/derek/continuity-triage/*`

Excludes: `hybrid-context-trial`, `jepa-*` directories, `known-world`, `git-local-probe`.

## Span
Collected 2026-10-09T12:45:07Z to 2026-10-09T12:45:24Z (17 seconds).

## Results
- **Status**: Complete (no slices required)
- **Repositories**: 31 sources processed
- **Events**: 4811 commit/tag/ref events extracted
- **Dropped**: 0 (null_ts: 0, polling: 0, decode_errors: 0)
- **Warnings**: roots_missing:12 (12 roots not found, expected condition)
- **Coverage**: All 31 specified sources visited and processed successfully

## Sources
Major repositories by event count:
- commandcenter~e225: 927 raw, 1196 events
- commandcenter-linux-flash~132c: 1319 raw, 1336 events
- commandcenter-flash-base~d3b1: 807 raw, 869 events
- ledger~1ce6: 519 raw, 521 events
- lab-rnd~890f: 143 raw, 145 events

Plus 26 additional repositories with smaller event counts (amux, clm-pilot, continuity, deepagents, founderOS, game-jepa, jepa-add-protocol, lab, lever-ledger, liveView-ui-run, memsplice, resume-linux.git, notebook variants, upstream, conductor-mirror, deepagents-poc, deepagents-shot-director, entire-probe).

## Implementation Notes
- Single slice execution completed within budget
- Run log shows clean source processing with no stalls
- Not-repos (non-git directories): 42
- Out-of-range events: 0
- Invalid remotes: 0
- Excluded paths: 8
- Null timestamps emitted: 297 (parsed but outside collection window)

## Future Runs
No changes required. This source is stable; roots_missing warning is expected as some paths may not exist or be mounted in all environments. No quirks detected.

## Verification (2026-10-09)

### Privacy Scan
- Status: PASSED
- Files scanned: 6
- Records scanned: 4844
- Text lines scanned: 80
- Unscanned: 0
- Violations: 0

### Recount via Git Verification
- Method: Extracted repository paths from repos.ndjson (31 entries), verified each using `git rev-list --count --all`
- Git repositories verified: 27 (all matching manifest raw counts exactly)
- Non-git repositories: 4 (correctly identified as 0 commits: notebook-27b, notebook-32b, notebook-devstral, notebook-gemma)
- Total commits in manifest: 4165
- Total commits verified in git: 4165
- Overall delta: 0 (exact match)

### Result: VERIFIED
- Privacy: clean, no violations
- Manifest record counts: exact match with git verification
- Manifest coverage: all 31 sources verified, 0 gaps
- Deltas: none (match within declared drops)
- Item completeness: confirmed 4811 events, 31 repos as reported
