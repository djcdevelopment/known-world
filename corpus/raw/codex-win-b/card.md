# codex-win-b

## Source description
Codex JSONL sessions from Windows host omen-c (Derek's Codex client). Collected from `/Users/derek/.codex/sessions` directory. This is shard 1 of 2 (split by SHA1 hash of session path).

## Span
No explicit time bounds (since/until both null in worklist). Full session history from the mount.

## Coverage
- 216 source files (Codex session JSONL files)
- 34,072 events (total records across all sessions)
- 0 repositories (metadata-only source)
- Complete read: 0 skipped, 0 null_ts, 0 polling, 0 decode_errors

## Slices
1 slice (completed in single run).

## Folding
Sessions are metadata-only per task rules; no transcript content ingested.

## Quirks
None encountered.

## Next run guidance
- Re-run to pick up any new Codex sessions added since this collection
- Consider time-bounding future runs if session count grows (until parameter in worklist)
