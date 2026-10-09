# claude-win: Claude Code, Windows, live

## Source description

Claude Code transcript archive from Derek's Windows OMEN box, live session directory at `/mnt/omen-c-read/Users/derek/.claude/projects`.

Contains 55 project directories with 1,042 jsonl session transcript files spanning 1.2 GB uncompressed. Event records include user/assistant chat messages, attachments, queue operations, custom titles, and assistant metadata (model, usage, request IDs, effort estimates).

Span: 2026-07-10 → 2026-10-08

## Extraction results

- **Events folded**: 41,294 events extracted from 1,042 source jsonl files
- **Repos**: 0 (chat source, no git repositories extracted)
- **Sources**: 1,042 all seen, 0 skipped, 0 decode errors
- **Warnings**: none
- **Status**: complete in 1 slice (29 seconds)

## Data quality

No dropped records (null_ts: 0, polling: 0, decode_errors: 0). All sources processed successfully without form errors or timeouts.

## Future changes

No immediate changes needed. The live source continues from 2026-10-08 and can be re-run to capture newer sessions. All accessible transcript files were processed; the data structure (JSONL project archives with line-delimited records) is stable.

