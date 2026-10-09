# e-git-nested work item

## Source

**Type:** Git repositories (nested)
**Host:** omen-e (Windows E: mount at `/mnt/omen-e-read`)
**Span:** Partial scan; no time range specified

Scans nested git repositories under six root paths on the Windows E: drive:
- `work/start/*` — contains planner (1660 commits), precheck, precheckv2, contextforge, farmer, ashley, portmap, scarecrow, langfuse (third-party; 8359 commits)
- `work/liveView/*` — ingest, ui
- `work/vllm-xpu-win/*` — kernels (third-party; 514 commits), vllm-src (third-party; 6 commits)
- `work/comfy/seer` — single repository
- `work/battlemage/tempo-workbench` — single repository
- `work/repos/*` — multi-agent-build-blueprint (2 commits)

Total: 16 repositories enumerated.

## Folding and coverage

**Status:** Complete (exit 0)
**Events extracted:** 11182
**Repositories discovered:** 16 sources
**Sources seen:** 16 (no skips)
**Non-repository items found:** 7

## Known issues and quirks

**Warnings from manifest:**
- `roots_missing: 18` — root paths specified in worklist but not discovered during enumeration; some git directories may be missing or inaccessible

**Dropped records:**
- null_ts: 0
- polling: 0
- decode_errors: 0

No form or substance issues detected during processing.

## Iteration

**Slices:** 1 (completed in first run)
**Runtime:** 2026-10-09T12:45:36Z to 2026-10-09T12:45:45Z (9 seconds)
**Budget:** 540s (single slice, well within budget)

## Future recommendations

The warning about 18 missing roots suggests some specified paths may not be discoverable under the current mount state or search patterns. Verify that all intended nested repositories are accessible and within the specified glob patterns on a subsequent run if fresh enumeration is needed.
