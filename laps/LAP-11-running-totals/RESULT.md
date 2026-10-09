# LAP-11 running totals: result (2026-10-09, builder Sonnet 5.5, work item w-26069fe96149)

Code: `compile/{corpus,series,build}.py` (`series.running_totals`), `compile/params.json` (`rate_window`, `births_to_nation`, `births_exclude_bulk`),
`render/{data,border,panels,card}.js` (`KW.fmt.microBar`), runner `lap.py` (build stills arms cut full). Receipts: `receipt-build.json`, `receipt-stills.json`,
`receipt-arms.json`, `receipt-export-cut.json`, `receipt-export-full.json`; `ct receipt` `receipt://14480d2cef644b1bbadea284` (cut export stage).
Videos (git-ignored): `out/full/final.mp4` 83.1 MB, `out/cut/final.mp4` 16.7 MB.

## Final totals (counts only; Derek's lineages, third-party clones and third-party-class commits excluded)

| Nation | Commits | Files changed | Lines added | Lines removed |
|---|---|---|---|---|
| human | 4,706 | 56,316 | 10,671,511 | 2,234,792 |
| ChatGPT | 0 | 0 | 0 | 0 |
| Claude | 4,391 | 30,354 | 5,005,288 | 273,092 |
| Codex | 46 | 1,057 | 169,966 | 669 |
| automation | 644 | 1,120 | 86,797 | 7,628 |
| local | 0 | 0 | 0 | 0 |
| OpenCode | 0 | 0 | 0 | 0 |
| **world** | **9,787** | **233,774 (see below)** | **18.4M lines (added + removed)** | |

| Surface | Commits | Files created | Files updated |
|---|---|---|---|
| C: | 3,722 | 25,962 | 3,543 |
| E: | 3,441 | 72,790 | 21,491 |
| linux | 2,553 | 13,030 | 141 |
| AM4 | 28 | 5,523 | 325 |
| FX99 | 43 | 1,157 | 965 |
| GitHub | 0 | 0 | 0 |

World `files` (ticker and card) = files changed in counted commits (88,847) + files created (118,462) + files updated (26,465) outside git, bulk copies excluded.
Not in any total: 1,151 third-party-class commits in Derek's lineages (11,923 files, 2,586,053 lines) and 23,451 commits in third-party clones (122,495 files, 17,227,908 lines).
Excluded bulk-copy records: 680,125 births and 62,411 updates.

## Definitions

- **Counted by** the commit's `actor.class`; commits per frame from the commit's epoch, cumulative per nation. Files changed = sum of `magnitude.files`; lines = sum of `ins` and `del`.
- **Rate**: commits in the trailing window of exactly one era unit of story time (year 365.2425 d in A, month 30.436875 d in B, week 7 d in C), found by binary search on the frame
  story-time axis, one value per frame; label `commits/yr`, `commits/mo`, `commits/wk`. The window is not normalised at the start (the first year reads what exists). Arm
  `rolling_10s` (last 300 film frames, scaled to the era unit) compiles (`receipt-arms.json`) but was not exported. Nothing else is smoothed.
- **Files created / updated** per surface: `file_birth` / `file_update` `n` by host, bulk copies excluded (`births_exclude_bulk: true`, same rule as non-git tiles). Arm
  `births_to_nation: launch_window` compiles (births inside a launch window ± 1 day on the same lineage go to that launch's nation, shown as `created~` in the rate row); default `off`.
- Micro-bars: shared log scale, zero below 10, full at 10^7.5 (about 31.6M), faint ticks at 1k, 10k, 100k, 1M; the lines row is two bars (added above, removed below).

## Layout

- **Right panel stays 320 px.** Row pitch 76 to 136 px (seven nations, 12 + 7 x 136 = 964 of 1,016 px); the map viewport is unchanged. Per nation: commits, files, lines (compact `+7.7M -2.2M`), rate; 12 px text, 8 px bars.
- Left panel 240 px, row pitch 76 to 96, two bars per surface (created, updated) under the existing counts.
- Ticker row: `commits 9.2k · files 220k · lines 14.7M` at x = 700, 14 px muted.
- Tally card: columns commits, files changed, +lines / -lines, a world row, and a third footer line (header font 18 to 16 px, columns re-spaced to 1,600 px).
- Chip fix: the legend layer clips to the panel; a chip caption wider than the room left falls back to its short form, then to an ellipsis cut, then is dropped. The artifact in
  `LAP-06 .../migration-2026-09-27.png` is the entering row (OpenCode) caught mid slide at the canvas edge (its swatch, first chip and yield line at x = 1,910), not a long caption; the slide-in is
  unchanged (12 frames) and now sits inside the clip.

## Receipts

| Check | Result |
|---|---|
| Compile twice (separate processes), full and cut | kw-data.js and audio byte-identical, both (full `ed9d5481...`, cut `86ec11cf...`) |
| 30 frames re-rendered in a fresh Chromium, reverse order, against the export's own hashes | **30 of 30 equal**, full and cut |
| Sync probe | white frame 15 only, **delta 0.0 ms**, full 688.33 s, 20,650 frames, audio 33,040,384 samples (+384); cut 90.000 s, 2,700 frames, 4,320,256 (+256) |
| Page errors | none, both |
| Launch metrics | unchanged from LAP-07: peak 19 / 43 per film second, collapsed 1.43 / 56.78 percent |

## Timing: the export, measured (10 workers, nice, bench27 running)

| Export | Wall, frames | Wall, with concat, AAC mux, probe, re-hash | Per frame |
|---|---|---|---|
| **Full piece, 20,650 frames** | **202.1 s** | **248.3 s (4.1 min)** | 9.77 ms |
| 90 s cut, 2,700 frames | 20.5 s | 26.7 s | 7.49 ms |

LAP-07 was 196.2 / 242.4 s: the panels add 3 percent. Compile 18 s full, 5 s cut. kw-data.js grew 17.3 MB (full) from the new per-frame series.

## Stills (`stills/`)

`running-2023-08-01.png`, `running-2026-03-15.png`, `running-2026-07-05.png`, `running-2026-09-27.png`, `running-2026-10-03.png`, `tally-card.png`.

## Deviations from DIRECTION

- **The 11,164 commits without numstat are not in any displayed total.** All of them sit in third-party clones (11,138 third-party class, 26 other), which launches and totals exclude. The
  footer's third line therefore says so instead of "count as commits and files, 0 lines" (the code writes that sentence if any counted commit lacks numstat; today it is 0).
- Lines are the corpus numbers uncapped (launch yield keeps its 20,000 lines per commit cap), so human 10.7M added is larger than the launch yield figure beside it (1.9M); two kinds of number on one panel.
- Bulk copies are left out of files created (742,536 files); counting them would put E: at about 573k created. Created and updated are per surface only; per nation only under the inferred arm.
- The world row on the tally card and the `files` definition (commit files + non-git creations + updates) are builder choices.
- The old `c / f` capacity line stays under the yield line (duplicating the new rows) to keep the existing look; it can go if Derek wants the panel quieter.

## For Derek to decide

1. Include third-party clones in the totals as a separate muted row? (23,451 commits, 17.2M lines, 11,164 of the commits have no line counts.)
2. Uncapped lines (18.4M, dominated by a few very large commits) or capped like launch yield?
3. Bulk copies: out (default, 680k births) or in as their own bar?
4. Rate arm: keep the era-unit window, or the 10 s rolling arm (compiled, not exported)?
5. Born-to-nation arm on (inferred, flagged `~`) or off.
