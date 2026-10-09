# Verification: continuity-runs

**Status:** VERIFIED

## Privacy Scan
- Result: CLEAN (violations=0)
- Files scanned: 6
- Records scanned: 871 (includes manifest/checkpoint metadata)

## Recount
- events.ndjson: 869 lines (matches manifest "events": 869)
- repos.ndjson: 0 lines (matches manifest "repos": 0)
- Source breakdown: 328 + 2 + 2 + 133 + 401 + 3 = 869 ✓
- Sources seen: 6 (matches manifest coverage)

## Verification Result
- Privacy OK: YES
- Recount matches manifest: YES
- Deltas from declared drops: NONE
  - null_ts: 0 (expected 0)
  - polling: 0 (expected 0)  
  - decode_errors: 0 (expected 0)

## Recount Method
Line count verification via `wc -l` on collected files (events.ndjson, repos.ndjson) compared against manifest.json source array and checkpoint.json records. No discrepancies within tolerance of declared drops.
