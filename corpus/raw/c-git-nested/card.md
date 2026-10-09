# c-git-nested

## Source
Git repositories from nested directories on omen-c mount (Windows mount of Derek's C: drive, read-only access). Scans 8 root paths spanning work, research, extraction, retirement, orchestration, and Diana lab directories.

## Span
- Started: 2026-10-09T12:45:37Z
- Finished: 2026-10-09T12:45:39Z
- Execution time: 2 seconds
- Slices: 1 (complete in single budget)

## Coverage
- Sources seen: 14 repositories found
- Repositories yielding events: 14
- Non-repo directories: 4 (skipped)
- Events collected: 1055
- Null timestamps emitted: 9
- Out of range events: 0
- Invalid remote records: 0

## Dropped Events
All dropped counters are zero:
- null_ts: 0
- polling: 0
- decode_errors: 0

## Warnings
- **roots_missing: 10** — Some directory paths in the root list did not exist or were not accessible on the mounted filesystem at scan time. This does not prevent processing of directories that do exist.

## Repositories Found

| Label | Raw Events | Status |
|-------|-----------|--------|
| ember~66b1 | 36 | processed |
| gad~e332 | 53 | processed |
| manifest~4398 | 32 | processed |
| oddlittlebird~c5cb | 2 | processed |
| showcase-site~729f | 292 | processed |
| comfy-quest-identity-wrong-tested~1355 | 0 | empty |
| comfy-quest-incomplete~b5d0 | 111 | processed |
| Lumberjacks~96a1 | 215 | processed |
| comfy~6cac | 237 | processed |
| local-operator-workspace-20260917~f7f4 | 38 | processed |
| truth-alignment-20260908~571e | 3 | processed |
| cnc-generals~8923 | 1 | processed |
| target~4396 | 0 | empty |
| episodes~25fe | 0 | empty |

## Folded
- 4 non-repository items encountered during directory traversal were identified but not processed as repositories
- 3 repositories with zero raw events (likely empty or invalid)

## Verified
- Events SHA256: 1b11950fab6d312e4d1fa506296d44c390d74d7539714c9ee564a81582b6cc04
- All 14 repositories successfully processed
- No decode errors or polling timeouts

## Quirks & Future Improvements
- 10 roots were missing/inaccessible at scan time; these may be directories that do not exist under the read-only mount or were unmounted. Future runs should verify mount status.
- 9 events with null timestamps were emitted; these should be examined in the raw events to determine if they represent data quality issues in the source repositories or collection boundaries.
- Consider filtering out zero-event repositories if they represent repository folders without actual git history.
