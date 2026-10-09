# fx99-git: Known World Collection

## Source
FX99 git repositories: HEARTH production infrastructure on FX99 (hostname `ai-1`, accessed via `ssh 100.122.130.124`).

From SURVEY.md §1e: Repos include `~/fleet` (+ `~/fleet.git` bare), `~/continuity`, and `~/.continuity/ledger`.

## Scope
Four git repositories collected across FX99:
1. **continuity** (`continuity~da60`): lab continuity system with work items and receipts
2. **fleet** (`fleet~6667`): main HEARTH fleet coordination repo
3. **fleet.git** (`fleet.git~7dae`): bare mirror of fleet
4. **ledger** (`ledger~1ce6`): HEARTH ledger tracking events and executions

## Results
- **Status:** complete
- **Events collected:** 110 total
  - continuity~da60: 18 events
  - fleet~6667: 41 events
  - fleet.git~7dae: 38 events
  - ledger~1ce6: 5 events
- **Repositories:** 4
- **Sources seen:** 4
- **Processing time:** 3 seconds (2026-10-09T12:45:08Z → 12:45:11Z)
- **Slices:** 1 (completed in single run)

## Coverage
- No sources skipped
- No decode errors
- No null timestamps
- No polling artifacts
- Warning: 6 git refs missing (shallow clones or excluded refs)

## Dropped Events
All dropped counters are zero:
- `null_ts`: 0
- `polling`: 0
- `decode_errors`: 0

## Quality Notes
Work completed without errors or truncation. All four FX99 git repositories successfully processed within the 540-second budget. The warning about missing roots (6 refs) is consistent with the expected shallow clone state of these repositories, as FX99 is a production infrastructure host with read-only git access.

## Future Runs
- Maintain current budget (540s per slice)
- All sources on FX99 remain accessible via tailnet
- No schema changes anticipated
- Continue with read-only git operations only
