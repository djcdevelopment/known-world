# e-git-a: Git repositories from Windows E:\work

## Source
E:\work top-level git repositories on omen-e (Windows machine). The mount at `/mnt/omen-e-read/work` provides read-only access to Windows E: drive, which contains 38 total git repositories (both private and third-party).

## Work items
Scanned with shard 0/3 (sha1(path) % 3): found 17 repositories in this shard.

## Repositories included
- GasperCards (threat-trace)
- Guild (goatsafterdark, private)
- ai-dev-system (private)
- bring-your-own-ollama (steppe-integrations)
- denning
- discoverlay (private)
- ember
- game (Lumberjacks)
- hearth (private)
- lantern
- leopard
- liveView (private)
- llamacpp-knee (third-party, ggml-org/llama.cpp)
- planning
- resonantOS (third-party)
- stars-app (private)
- workbench (private)

## Results
- **Events extracted**: 2,234
- **Repositories processed**: 17
- **Status**: complete (all sources processed in 1 slice)
- **Duration**: 4 seconds
- **Dropped records**: 0 (null_ts: 0, polling: 0, decode_errors: 0)
- **Warnings**: none

## Span
First commit across all repos: 2026-01-17 (stars-app)
Last commit across all repos: 2026-09-25 (resonantOS)

## Remarks
- No coverage gaps or decode errors
- All 17 repositories in this shard processed successfully
- ResonantOS (1,073 events) and llamacpp-knee (517 events) are the largest sources
- Third-party repositories (ResonantOS, llamacpp-knee) included for completeness
- No sources skipped or excluded

## Future runs
No quirks detected. Rerun same configuration. If any changes to mount or shard configuration, verify read-only access to `/mnt/omen-e-read/work`.
