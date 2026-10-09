# Known World: c-git-b

## Source
Git repositories on the C drive mount (omen-c, `/mnt/omen-c-read/work`). This is shard 1 of 3 for the git repo collection (rule: `sha1(path) % 3`). No time constraints.

## Span
- **Started:** 2026-10-09T12:45:09Z
- **Finished:** 2026-10-09T12:45:11Z
- **Duration:** 2 seconds
- **Timeout:** 1800s total per item (one timeout_s per session)
- **Slices:** 1 (completed in one execution)

## Collected
- **Events:** 1719 commit/tag events
- **Repositories:** 14 unique repos scanned
- **Sources seen:** 14 (no skips)
- **Coverage:** Full (scan_depth=1, all repos under /mnt/omen-c-read/work enumerated)

## Repositories
1. 404~655a (43 events)
2. ComfyMods~d453 (1128 events)
3. Unfaded~1192 (15 events)
4. assessment~713e (6 events)
5. commandcenter-hermes-fx99~edc1 (0 events)
6. contextlandscape~7bf5 (73 events)
7. gallery-stage-baseline-20260915~5834 (0 events)
8. irc~8356 (47 events)
9. irc-hearth-adapter~7806 (0 events)
10. networksense~bd3e (260 events)
11. nightshift~65ce (48 events)
12. notebook~7bc6 (13 events)
13. sealcompanion~d849 (1 event)
14. valheim-profile-engine~d9f1 (14 events)

## Data Quality
- **Dropped:** 
  - null_ts: 0
  - polling: 0
  - decode_errors: 0
- **Warnings:** None
- **null_ts_emitted:** 26 (events with null commit timestamps recorded, likely detached/synthetic states)

## Quirks & Notes
- No issues encountered.
- Fast execution (2s) indicates clean, well-formed git repositories.
- 4 repos with 0 events (likely mirrors or bare repos without commit history relative to scan_depth=1 policy).
- Future runs should verify timestamp coverage on the 26 null_ts events if chronological completeness is required.

## Events SHA256
`816bdc542eb7b32c944416539ee2a9338e6adcd1a3c376ba104df2b4ddffbd21`
