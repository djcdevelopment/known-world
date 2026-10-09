# e-births: File birth times from omen-e mount

## Source

**Source type:** fs_births (file system birth times via `stat %w`)

From SURVEY.md § 2: Non-git directories on E:\work with birth timestamps. The E: drive (Windows mount at `/mnt/omen-e-read`) contains 49 directory sources with files created between 2023-09 and 2026-10.

## Span

Earliest birth: 2023-09 (comfy directory)
Latest birth: 2026-10 (recent additions)
Collection completed: 2026-10-09T12:45:52Z

## Folded

No filtering applied. All 49 directory sources were processed; 662 events collected with 0 dropped records.

## Summary

| Metric | Value |
|--------|-------|
| Status | complete |
| Events collected | 662 |
| Git repositories | 0 |
| Directory sources seen | 49 |
| Sources skipped | 0 |
| Warnings | 0 |
| Slices required | 1 |

## Directories processed

49 sources from /mnt/omen-e-read/work:
- comfy (29,366 raw files)
- vllm-xpu-win (20,402 files)
- start (14,762 files)
- battlemage (7,210 files)
- 8350 (4,690 files)
- Plus 44 smaller sources

All birth times extracted with nanosecond precision via ntfs3 mount.

## Next run notes

- Took 7 seconds wall time, single slice
- No errors, no decode issues
- Dropped counts all zero: no null timestamps, no polling artifacts, no decoding errors
- Ready for analysis or comparison against prior runs
