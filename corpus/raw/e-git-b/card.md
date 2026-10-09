# e-git-b: Windows E: drive Git repositories (shard 1 of 3)

## Source
Windows E: drive repository scan from `/mnt/omen-e-read/work` on host omen-e. The item processes one of three shards of repositories (k=1, n=3 based on `sha1(path) % 3`).

## Span
Git history and references from repositories on the E: drive. The mount covers Derek's Windows active projects, including AI work, tooling, and game projects. Repositories span 2018–2026-10-08 (see SURVEY.md §1b for full listing).

## Collected
- **6 repositories**: RaidUI, chatGPT_parser, llamacpp-qwen38, manifest, reader, vllama
- **11,855 events**: commit logs, refs, commit metadata (no diffs)
- **1 slice**: single pass completed in budget
- **Status**: complete

## Folded
- Event-based structure: commit objects (author, committer, dates, messages) and all refs per repository
- No diffs or file contents; log-based only
- Partial clone repos (missing blob objects) trigger warning; present in `llamacpp-qwen38` (large third-party fork)

## Warnings
- `numstat_failed:partial_clone_missing_blobs` (1 warning): llamacpp-qwen38 (unslothai/llama.cpp fork, 11,272 commits) is a partial clone; cannot generate numstat; collection continues

## Dropped
No records dropped:
- `null_ts`: 0
- `polling`: 0
- `decode_errors`: 0

## Notes
- Scan depth: 1 (top-level repos only; nested repos like `start/*` are not in this shard)
- Log timeout: 600s per repository
- Shard coverage: 1 of 3 shards; future runs of e-git-b on the same host should return identical results
- Item timeout: 1800s total; completed in ~2s
