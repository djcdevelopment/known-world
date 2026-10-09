# claude-linux Work Item Results

## Source Description

**Source:** Claude Code, Linux (`~/.claude/projects`)  
**Type:** JSONL metadata export from Claude Code session logs  
**Host:** omen-linux (this system)  
**Span:** 2026-09-27 to 2026-10-09  

### Source Details

This corpus item processes Claude Code session and message logs from the Linux host. The logs contain:
- 12 project directories worth of session metadata
- 481 JSONL lines (341 are subagent session logs under `<session>/subagents/*.jsonl`)
- Original uncompressed size: 411 MB

**Schema:** Event objects with keys: `parentUuid`, `isSidechain`, `promptId`, `type`, `message` (with role/content), `uuid`,
`timestamp`, `permissionMode`, `origin`, `promptSource`, `userType`, `entrypoint`, `cwd`, `sessionId`, `version`, `gitBranch`.
Assistant messages add `message.model`, `message.usage`, `requestId`, and `effort`. Special types include `queue-operation`,
`cost-state`, and `atis-latch`. Only the metadata subset allowed by CONTRACT.md section 2 is read; message content is never read.

Additional logs from `~/.claude/history.jsonl` contain 213 display/pastedContents entries.

### Processing Notes

- **Events collected:** 9,124 (from 499 JSONL source files)
- **Repositories discovered:** 0 (metadata only, not extracted)
- **Processing status:** Complete in 1 slice (5 seconds)
- **Dropped records:** 0 (null_ts: 0, polling: 0, decode_errors: 0)
- **Warnings:** None

### Folding and Transformations

Chat traffic is folded to one `chat_msg` record per (session, role, minute) plus one `chat_session` record per transcript file
(CONTRACT.md section 1); 84,774 raw lines became 9,124 events. Timestamps are validated; no message text is kept.
(Card line reflowed by the Merge manager on 2026-10-09: the original had one line over the 400-character text limit of the privacy scan.)

### Future Runs

No changes needed. Processing completed successfully without errors or truncation. The source remains stable at 12 project directories on the Linux host.
