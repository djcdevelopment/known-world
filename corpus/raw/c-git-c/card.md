# c-git-c: Git repositories from Windows C: mount (omen-c)

## Source Description
This work item processes git repositories from the C:\work directory on the OMEN box (mounted read-only at `/mnt/omen-c-read/work`). The C: drive contains Derek's primary project work across 36 repositories, spanning various projects including:
- **baseline**: Core infrastructure (1358 commits, 2026-03-24 → 09-23)
- **commandcenter**: Main control plane (927 commits, 2026-07-02 → 09-23)
- **lumberjacks-platform**: Game platform (728 commits, 2026-07-04 → 09-23)
- **ComfyStewardView**: Comfy steward tooling (303 commits, 2026-03-19 → 09-15)
- And 12 additional repositories with 0–36 commits each

## Collection Span
- **Started**: 2026-10-09 12:45:08Z
- **Finished**: 2026-10-09 12:45:15Z (7-second duration)
- **Time range of sources**: 2026-03-19 → 09-23 (earliest repo to latest commit across all repos)

## Events & Repositories
- **Total events**: 3704 git events (commits, refs, tags)
- **Repositories processed**: 16
- **Sources seen**: 16 (100% coverage for this item)
- **Slices**: 1 (completed on first run, no retry needed)

## Data Quality
- **Dropped records**: 0
  - null_ts: 0
  - polling errors: 0
  - decode errors: 0
- **Warnings**: `numstat_failed:partial_clone_missing_blobs` — one numstat operation on a repo with partial clones could not enumerate file changes; event metadata still captured

## What Was Folded
- Worktrees (8 referenced in SURVEY): commandcenter-d1-guard-9f306fb, commandcenter-flash-foreman, commandcenter-hermes-fx99, commandcenter-jev-scheduler, commandcenter-local-work, hearth-execution-control-plane, gallery-stage-baseline-20260915, gallery-stage-quest-20260915, gallery-stage-steward-20260915, irc-hearth-adapter — read as part of parent repos
- Nested repos (11 shallow clones): am4-harvest/*, Diana/*, _extract/*, _retired/*, orchestration/*, research/* — captured at shallow depth

## Notes for Future Runs
- The partial-clone warning on one repo is expected (shallow clone behavior); it does not block event collection
- This collection is read-only against a BitLocker-protected mount accessed via ntfs3; performance is stable at 7 seconds
- All 16 repos in this slice completed successfully; no SKIPPEDs or partial failures
