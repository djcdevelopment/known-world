# e-git-c: Windows E: drive Git repositories (shard 2/3)

## Source
E:\work (`/mnt/omen-e-read/work`) on host omen-e. This is a sharded collection (k=2, n=3, rule="sha1(path) % n") collecting git repositories from Derek's Windows E: drive.

## Span
- Started: 2026-10-09T12:45:09Z
- Finished: 2026-10-09T12:45:12Z
- Duration: ~3 seconds

## Coverage
- **Events collected:** 360 (git commit/tag/branch events)
- **Repositories scanned:** 15 total
- **Sources seen:** 15 (all sources in scan depth 1 completed)
- **Dropped events:** 0 (null_ts: 0, polling: 0, decode_errors: 0)
- **Warnings:** none

## Repositories collected
ai-systems-research, azure-event-grid-viewer, b70tools, campfire, event-viewer, gad, gad-bot, img, llama.cpp-src, llamacpp-knee-pr, temp, work-visuals, writing, www, xpu-train

## Folding
No skipping or exclusions. The shard rule (sha1(path) % 3) selected this subset from E:\work for the third (k=2) partition.

## Execution
- **Slices:** 1 (completed in single execution)
- **Budget used:** ~3 seconds of 540s allowed
- **No retries needed**

## Quirks & future changes
None observed. Collection completed cleanly with expected performance.
