# mirror-1: Four public GitHub repositories (Path of Exile and steppe-integrations)

## Source

Four public GitHub repositories mirrored from GitHub:
1. **PoE-Item-Filter-Creator** — Path of Exile item filter creation tool
2. **POEscripter** — Path of Exile scripting tool
3. **threat-trace** — from steppe-integrations
4. **waypoints** — Path of Exile waypoints utility

These are open-source projects in Derek's GitHub account (djcdevelopment) and the steppe-integrations organization.

## Collection span

- **Started**: 2026-10-09T12:52:23Z
- **Finished**: 2026-10-09T12:52:23Z
- **Duration**: instantaneous (1 slice)
- **No time range filters**: since=null, until=null

## What was folded

All four repository histories were scanned with no time filtering (complete history from each mirror clone).

## Collection results

- **Total events**: 10
- **Total repositories**: 4
- **Sources seen**: 4
- **Slices taken**: 1 (completed in first budget allocation)
- **Events SHA256**: 412d36d70255441b127e33f99af83e10403a13a074f2d5e6741f28279ced78f0

### Per-source breakdown

| Source | Label | Events | Raw items |
|--------|-------|--------|-----------|
| PoE-Item-Filter-Creator.git | feb9 | 5 | 2 |
| POEscripter.git | 1886 | 1 | 0 |
| threat-trace.git | 2f5c | 1 | 0 |
| waypoints.git | 445c | 3 | 1 |

## Quirks and observations

- All four repositories completed successfully in one slice with no timeouts
- No null timestamps, polling errors, or decode errors
- No warnings emitted
- Repositories with zero raw items (POEscripter, threat-trace) were successfully scanned but produced no raw event data beyond the base record

## Future runs should

- Verify that the mirror clones remain current (consider adding a pre-collection sync step if not already handled upstream)
- Monitor whether raw event count distributions change meaningfully across subsequent runs
