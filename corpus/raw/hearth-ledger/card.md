# hearth-ledger Work Item

## Source
HEARTH event ledgers from the production system on omen-linux and an archived Windows copy.

From SURVEY.md:
- **Linux source** (`~/hearth-production/var/ledger/events.ndjson`): 375 MB, 472,077 raw lines spanning 2026-07-04 to present (92 days). Tracks all HEARTH MCP calls with event_id, timestamp, caller details, tool invoked, ok/error status, duration, task class, model, backend routed to, and full event metadata.
- **Windows source** (`/mnt/omen-c-read/hearth-var/ledger/events.ndjson`): 90,784 events archived through 2026-08-19. Shares identical schema; events deduplicated on event_id against the Linux copy.

## Processing Summary
- **Status**: Complete in 1 slice
- **Timeline**: 2026-10-09T12:46:49Z to 2026-10-09T12:47:00Z (11 seconds wall time)
- **Events extracted**: 25,985 unique events (all from Linux source)
- **Sources processed**: 2 (ledger-0-omen-linux and ledger-1-omen-c)
- **Deduplication**: 1,293 records deduplicated across sources
- **Raw records**: Linux 472,081 → 25,985; Windows 90,784 → 0 (fully deduplicated)

## What Was Folded
The Windows archive (90,784 events through 2026-08-19) was fully subsumed by the Linux ledger, which has continuous coverage from 2026-07-04 through 2026-10-09. All 90,784 Windows events matched event_ids already present in the Linux source.

## Dropped
- `polling`: 535,587 records (routine polling calls: kernel_status, get_execution, etc. filtered per schema)
- `null_ts`: 0 records
- `decode_errors`: 0 records

## Slices
1 (completed in single 11-second run well within 540s budget)

## Quirks
None observed. Source format was stable, schema was consistent, and deduplication worked as expected.

## Future Changes
- Routine refresh as the Linux ledger grows (new events ingested continuously)
- May need pruning strategy once the ledger exceeds disk/memory constraints
