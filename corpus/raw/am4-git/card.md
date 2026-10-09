# am4-git collection report

## Source

AM4 host git repository scan: systematically collects git repository metadata and commit history from multiple root directories on the AM4 machine:
- `~/*` — home directory repositories
- `~/.continuity/ledger` — continuity ledger repository
- `~/o1/*` — o1 project directories
- `~/baseline/*` — baseline project directories
- `~/work/*` — work directory repositories

Source type: `git_repo` on host `am4`. Single shard (k=0, n=1).

## Span and coverage

- **Timeframe**: No time filters applied (since/until both null)
- **Sources seen**: 11 git repositories successfully collected
- **Events collected**: 389 commit/push/ref events across all repositories
- **Repositories**: 11 total
- **Slices**: 1 (completed in single run, total budget 540 seconds)

## Sources collected

- ComfyUI~41c5 (1 raw entry, 3 events)
- am4bot~00aa (18 raw entries, 20 events)
- bench~9a2f (5 raw entries, 7 events)
- chatgpt_parser_run~d83c (11 raw entries, 13 events)
- continuity~da60 (56 raw entries, 58 events)
- quest-build-20260915~100e (263 raw entries, 265 events)
- sovereign-shards~263c (6 raw entries, 8 events)
- ledger~1ce6 (5 raw entries, 7 events)
- level-zero-tests~033d (1 raw entry, 3 events)
- libpng~021b (1 raw entry, 2 events)
- llama.cpp~75e1 (1 raw entry, 3 events)

## Folding and processing

No sources were skipped or excluded. All 11 repositories were successfully scanned and processed.

### Data quality

**Warnings encountered**:
- `roots_missing:93` — 93 root paths specified in the scan did not yield repositories (e.g., non-existent directories, empty directories, non-git paths)
- `numstat_failed:partial_clone_missing_blobs` — Some commit numstat calculations failed due to missing blobs in partially-cloned repositories

**Dropped records**: None
- null_ts: 0 events with missing timestamps
- polling: 0 polling records dropped
- decode_errors: 0 JSON/metadata decoding failures

## Quirks and future improvements

1. **Partial clone limitations**: The `quest-build-20260915~100e` repository (263 raw entries, 265 events) is likely a sparse/shallow clone with missing blob data. Future runs may benefit from detecting and noting shallow-clone repositories separately.

2. **Large repository**: `quest-build-20260915~100e` dominates the event count (265 of 389 events, 68%). Consider filtering by date range or commit depth if this repository's history becomes unwieldy.

3. **Root discovery**: 93 failed root paths suggests the scan configuration includes many non-repository paths. Consider maintaining an explicit inclusion list or refining root patterns for efficiency.

## Execution summary

- **Completed in 1 slice**: Run completed cleanly in 4 seconds (2026-10-09T12:45:07Z to 2026-10-09T12:45:11Z)
- **No resumption needed**: budget_s=540 provided ample headroom for all 11 sources
- **Status**: `complete` with 0 pending sources
