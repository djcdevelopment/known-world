# PROBE-00: launches under the payload model, default thresholds (2026-10-09)

Run by the frontier session over `corpus/merged/events.ndjson`, `repos.json`, `sessions.json` with `probe.py` (this
directory). Purpose: does the payload model (DIRECTION.md) produce a Hashimoto-like event count and the shape
evolution Derek described, before any renderer exists. Counts only; no corpus line was printed.

Thresholds (DIRECTION.md defaults): episode gap 2 h on one lineage; a test needs ≥ 50 lines or ≥ 3 files; a launch
is a cluster of tests whose starts fall within 2 h of each other across lineages; MIRV = a launch touching ≥ 2
lineages; nation = the dominant AI class among the episode's commits, else the class of a session overlapping the
window by ± 30 min, else human. Third-party lineages (`third_party: true` in repos.json) excluded.

## Headline

| Measure | Value |
|---|---|
| Derek's lineages with commits | 102 |
| Episodes (gap 2 h) | 1,207 |
| Tests (min yield) | 1,047 |
| **Launches** (clusters) | **415** |
| Single / MIRV | 215 / 200 |
| Max warheads in one launch | 10+ (3 launches at 10 or more) |
| With third-party lineages included (wrong, for the record) | 2,697 launches, 2,415 of them third-party |

415 launches over the era-C span (about 9 minutes of film at 2.4 s per day) is one flash every 1.3 s on average:
inside the original's range (2,053 over 14 min). Per-commit flashing would have been 32,121 events.

## Shape per month (single / MIRV)

| Month | single | MIRV |
|---|---|---|
| 2018-08 … 2025-07 | 9 | 0 |
| 2026-01 | 12 | 0 |
| 2026-03 | 24 | 11 |
| 2026-04 | 27 | 13 |
| 2026-05 | 26 | 26 |
| 2026-06 | 44 | 27 |
| 2026-07 | 23 | 47 |
| 2026-08 | 16 | 36 |
| 2026-09 | 31 | 29 |
| 2026-10 (to the 9th) | 3 | 11 |

The operator's curve Derek described is in the data: singles only until 2026-01, MIRVs appear in March, reach parity
in May, dominate in July and August (the fleet and worktree era), and remain half the launches in September.

Warheads per launch: 1: 215 · 2: 85 · 3: 46 · 4: 23 · 5: 24 · 6: 10 · 7: 3 · 8: 4 · 9: 2 · 10+: 3.

## Yield (lines = insertions + deletions per launch)

| Band | Launches |
|---|---|
| < 100 | 28 |
| 100 to 1k | 109 |
| 1k to 10k | 154 |
| 10k to 100k | 92 |
| ≥ 100k | 32 |

Five orders of magnitude: log10 bands work as the visual size scale. The ≥ 100k band needs a look in the thin slice
(vendored or generated code inflating lines; files and moving pieces may be the better size for those).

## Nation of launch

human 165 · claude 236 · codex 10 · automation 4. Codex reads low because Codex rarely authors commits; its sessions
only set the nation when a Codex session overlaps an episode with no AI trailer. The builder should weigh sessions
and trailers together (lap variable).

## First appearances (the industry's curve; the growing legend)

Per nation: human 2017-12-22 · chatgpt 2023-04-17 · claude 2025-10-06 · codex 2026-06-29 · automation 2026-07-03 ·
local_model 2026-07-20 · opencode 2026-09-27.

Per model generation (raw names; the compile layer must canonicalise `opus-4.7` / `opus-4-7`, `fable-5-1` /
`fable-5.1`, and map seat names like `am4-dense-27b` to their model): gpt-5-1 2025-11 · opus-4.5 2025-12 ·
sonnet-4.5 2026-01 · opus-4.6, haiku-4.5 2026-02 · sonnet-4.6, gpt-5-3 2026-03 · opus-4.7 2026-04 · opus-4.8 2026-05/06
· fable-5 2026-06-09 · gpt-5.5 / gpt-5.4 (Codex) 2026-06-29 · builders cc-builder-1..3, am4-worker-1, omen-worker-1
2026-07-03 · sonnet-5 2026-07-04 · gpt-5.6 2026-07-10 · gpt-oss-120b (local) 2026-07-20 · opus-5 2026-07-25 · gemini
3.5 flash / 3.1 pro (local lane) 2026-07-30 · fable-5.1 2026-08-28 · qwen3-30b-a3b, phi4, qwen14b (local) 2026-09-04 ·
gpt-6 2026-09-06 · qwen3.8-27b, am4-dense-27b 2026-09-22 · opus-5.5 2026-09-26 · opencode with qwen3.6-35b, gemma-4-31b,
devstral 2026-09-27 · gpt-6.1 2026-09-30 · sonnet-5.5 2026-10-01.

Sixty-odd generations enter in a year. The legend cannot list them all at once: generations are shades of their
class hue and only the class names stand in the border (lap variable `generation_shades`), with a generation's first
test marked by a brief name caption at the flash.

## What the builder takes from this

- The thresholds produce the right order of magnitude; keep them as `params.json` defaults.
- Exclude third-party lineages from launches; they are territory, never tests.
- Compute launches once in `compile/launches.py` (CONTRACT.md §8), deterministic; this probe is the reference
  for its counts (415 / 215 / 200 at these parameters).
- Yield bands log10; investigate the ≥ 100k band.
- Canonical generation names before `nations.json`.
