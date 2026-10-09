# Verification Report: e-git-c

## Item Summary
- ID: e-git-c
- Source Type: git_repo
- Host: omen-e
- Collector Status: complete
- Reported: 360 events, 15 repos, 15 sources seen

## Privacy Scan Results
- Command: `collect/knownworld/privacy_scan.py corpus/raw/e-git-c`
- Exit Code: 0 (clean)
- Scanned Files: 6
- Records: 377
- Text Lines: 48
- Unscanned: 0
- Violations: 0 ✓

## Recount Verification (Git Repositories)

### Method
For each of the 15 repositories listed in the manifest, ran:
```
git -C <repo_path> -c safe.directory='*' rev-list --count --all
```
with `GIT_OPTIONAL_LOCKS=0` environment variable.

### Results
All 15 repositories recounted:
- ai-systems-research: 22 ✓
- azure-event-grid-viewer: 47 ✓
- b70tools: 11 ✓
- campfire: 40 ✓
- event-viewer: 46 ✓
- gad: 56 ✓
- gad-bot: 2 ✓
- img: 10 ✓
- llama.cpp-src: 1 ✓
- llamacpp-knee-pr: 0 (not found, expected 0) ✓
- temp: 11 ✓
- work-visuals: 2 ✓
- writing: 35 ✓
- www: 27 ✓
- xpu-train: 1 ✓

**Total Recount: 311 commits**
**Manifest Expected: 311 commits**
**Match: ✓**

### Event Count Verification
- File: events.ndjson
- Line Count: 360
- Manifest Expected: 360
- Match: ✓

## Overall Result
- Privacy: CLEAN (no violations)
- Commits: MATCH (311 == 311)
- Events: MATCH (360 == 360)
- Dropped Events in Manifest: 0

**Status: VERIFIED ✓**
