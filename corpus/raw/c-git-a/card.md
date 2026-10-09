# Verification Report: c-git-a

**Item ID:** c-git-a  
**Source Type:** git_repo  
**Host:** omen-c  
**Date:** 2026-10-09

## Verification Status
**PASS** — All checks passed. No data quality issues found.

## Privacy Scan
- **Status:** Clean (no violations)
- **Files scanned:** 6
- **Records examined:** 550
- **Text lines processed:** 57
- **Violations:** 0

## Data Count Verification

### Events and Repositories
| Item | Expected | Observed | Delta | Status |
|------|----------|----------|-------|--------|
| events.ndjson lines | 534 | 534 | 0 | ✓ |
| repos.ndjson lines | 14 | 14 | 0 | ✓ |
| Total git commits | 496 | 496 | 0 | ✓ |

### Per-Repository Commit Counts (Git Rev-List Verification)
All 14 repositories counted via alternative method (git rev-list --count --all):

| Repository | Manifest | Git Rev-List | Delta | Status |
|------------|----------|--------------|-------|--------|
| comfy-quest | 266 | 266 | 0 | ✓ |
| commandcenter-jev-scheduler | 0 | 0 (worktree) | 0 | ✓ |
| deepagents-poc | 1 | 1 | 0 | ✓ |
| deepagents-shot-director | 3 | 3 | 0 | ✓ |
| deepnorthtesting | 46 | 46 | 0 | ✓ |
| djcdevelopment | 1 | 1 | 0 | ✓ |
| hearth-execution-control-plane | 0 | 0 (worktree) | 0 | ✓ |
| ismodded | 10 | 10 | 0 | ✓ |
| isolate | 20 | 20 | 0 | ✓ |
| memsplice | 24 | 24 | 0 | ✓ |
| steppeintegrations-site | 88 | 88 | 0 | ✓ |
| steward-spatial-lab | 17 | 17 | 0 | ✓ |
| totemalert | 16 | 16 | 0 | ✓ |
| vulkancliff | 4 | 4 | 0 | ✓ |

### Dropped Records
- null_ts: 0
- polling: 0
- decode_errors: 0

### Coverage
- Sources seen: 14 / 14
- Sources skipped: none
- Invalid remote records: 0
- Out-of-range records: 0

## Collection Metadata
- **Status:** complete
- **Started:** 2026-10-09T12:45:10Z
- **Finished:** 2026-10-09T12:45:12Z
- **Duration:** 2.2 seconds
- **Slice count:** 1

## Conclusion
The c-git-a item (git_repo collection from omen-c:work) has been verified complete and accurate. All event and repository counts match between manifest, checkpoint, and independent git verification. No privacy violations detected. No data quality issues identified.

**Verified By:** Claude Code  
**Verification Method:** Privacy scan + manifest cross-check + git rev-list verification  
**Verification Date:** 2026-10-09
