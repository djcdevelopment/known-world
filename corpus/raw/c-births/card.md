# c-births work item

## Source
**File system births (fs_births)** on the C: drive mount (`/mnt/omen-c-read/work`). This source collects birth timestamps and file counts from non-git directories on the Windows C: drive, mirrored to the Linux omen-c mount point.

The C: drive contains major project trees and work-in-progress artifacts: omen-perception (50K+ files, 2026-06 → 10), orchestration (33K+, 2026-09), tools (18K+), worktrees (10K+), research (6K+), and many smaller supporting directories (valheim-capture, JEPA, Diana, am4, etc.).

## Span
Work item execution: 2026-10-09 12:45:39Z → 12:45:44Z (5 seconds elapsed)

## Coverage
- **Sources seen**: 38 directories
- **Events collected**: 607 (birth timestamps and directory sizes)
- **Repos**: 0 (fs_births does not extract repository data)
- **Slices**: 1 (completed in single 540s budget slice)

## Folded
Nothing folded or dropped. All 38 directory sources processed successfully:
- 0 null timestamps
- 0 polling retries
- 0 decode errors
- 0 records skipped

## What was collected
Birth timestamps and file counts for 38 non-git directory trees on the C: drive:
- Large trees: hearth-var (1,215 files), omen-perception (50,760), orchestration (33,660), tools (18,722), worktrees (10,774), research (6,076)
- Medium trees: valheim-capture (4,728), comfy-quest-test-artifacts-20260812 (1,906), github-runner-deepnorthtesting (939)
- And 28 smaller supporting directories

## Quirks and notes
None. Execution clean, no warnings, no errors. Coverage complete.

## For the next run
- No changes needed. Source is stable and coverage complete.
