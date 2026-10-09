# codex-win-a

## Source
Codex session transcripts from Windows host `omen-c` (mount `c`): `/mnt/omen-c-read/Users/derek/.codex/sessions`

Span: 2026-06-29 → 2026-10-06 | 432 jsonl files | 10.6 GB

Payload schema: line keys `timestamp type payload`; first line carries `session_id id timestamp cwd originator cli_version source thread_source model_provider base_instructions`. Metadata only (chat sources are metadata only per Derek's decision).

## Work completed

| Metric | Value |
|---|---|
| **Status** | complete |
| **Events collected** | 29,950 |
| **Sources processed** | 216 (of 216 available) |
| **Repositories** | 0 |
| **Slices** | 1 |
| **Time to completion** | 32 seconds (2026-10-09T12:46:04Z → 12:46:36Z) |

## Dropped counters
- null_ts: 0
- polling: 0
- decode_errors: 0

All events successfully parsed; no decode failures or timestamp gaps.

## Notes for future runs
- Single-slice completion at 32 seconds; ample headroom under 540 s budget
- All 216 Codex sessions from Windows archive processed without errors
- No dropped records across the span
- Manifest ready for downstream operations

