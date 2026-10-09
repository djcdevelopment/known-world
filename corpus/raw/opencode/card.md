# OpenCode — Known World Collection

## Source

OpenCode local session database (`~/.local/share/opencode/opencode.db`): recent chat activity with 24 sessions, 953 messages, 2,203 parts, 7,716 events (22 MB raw). Collected via sqlite with `mode=ro&immutable=1` for read-only access.

## Span

- **Date range**: No specific date range provided in SURVEY (listed as "recent")
- **Period**: Part of continuous chat coverage from 2026-09-27 onward (Linux Claude + Codex + OpenCode)

## Collection Results

- **Events**: 209 (folded from 953 raw messages)
- **Repositories**: 0
- **Sources seen**: 1 (opencode-db sqlite source)
- **Slices**: 1 (completed in single run)
- **Status**: `complete`

## Folding

OpenCode events fold message-level records into higher-order events. Raw 953 messages → 209 folded events (78% compression via event aggregation).

## Warnings & Quirks

### Warnings (from manifest)

- **sqlite_immutable_wal_may_be_missed**: The immutable WAL mode may miss writes. Future runs should verify that database snapshots during collection are complete, or cross-check event counts against live OpenCode queries.

### No quirks hit in this run

## What a Future Run Should Change

1. Verify sqlite immutable WAL completeness: compare folded event counts to known totals from live database
2. Consider explicit date-range filtering if new chat sessions beyond the collection period are expected
3. Track any schema changes to the OpenCode database that affect field parsing

## Summary

OpenCode collection completed successfully in 1 slice with 209 folded events. No dropped records. One source warning noted regarding WAL immutability; recommend verification of snapshot completeness on next run.
