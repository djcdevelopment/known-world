# claude-zip: Claude Code Windows archived sessions

**Source:** Claude Code, Windows, archived
**Path:** `/mnt/omen-e-read/work/claude-20260623T084942Z-3-001.zip` (212 MB)
**Archive date:** 2026-06-23
**Session span:** 2026-05-09 → 2026-06-22

## What was collected

413 JSONL files extracted from a zipped `~/.claude` directory (50 project directories, 410 MB uncompressed). The archive contains Claude Code project transcripts from Derek's Windows machine during May–June 2026.

Schema notes:
- Line type ∈ user / assistant / attachment / queue-operation / last-prompt / custom-title
- Keys: `parentUuid isSidechain promptId type message{role,content} uuid timestamp permissionMode origin promptSource userType entrypoint cwd sessionId version gitBranch`
- Assistant messages add: `message.model message.usage requestId effort`

## Folding

Nothing was dropped during collection.

**Coverage:**
- 17,623 events extracted across 412 individual zip sources (zip members)
- 0 repositories
- No errors, null timestamps, polling events, or decode failures
- All 412 sources processed successfully in 1 slice (12 seconds)

## Warnings

None. Smooth complete run.

## Future runs

No known quirks or adjustments needed. If re-run, expect identical results and same processing time.
