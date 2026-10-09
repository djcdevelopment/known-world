# LAP-01 launch strip: result (2026-10-09, builder Sonnet 5.5, work item w-26069fe96149)

Code: `compile/launches.py`, `nations.py`, `corpus.py`, `names.py`, `clock.py`, `strip.py`, `common.py`, `params.json`;
runner `lap.py`, waterfall `parity.py`. Corpus: v1.4 merge, 212,498 events, snapshot 2026-10-09T12:45:04Z;
`relations.json` and `chatgpt_links.json` both present at compile time and used. Counts only; no corpus line printed.
Images: `strip-session.png`, `strip-time_window.png`, `strip-compare.png` (default arm above, control arm below).

## Counts, both arms (third party excluded; non-git episodes included in launch totals)

| Measure | PROBE-00 | Spine (13:00Z, older corpus) | **session (default)** | **time_window (control, 12 h cap)** | session_or_nation (info) |
|---|---|---|---|---|---|
| Git episodes (2 h gap) | 1,207 | 935 | 1,001 | 1,001 | 1,001 |
| Git tests (min yield) | 1,047 | 827 | 902 | 902 | 902 |
| Non-git tests (= launches) | n/a | 133 (births only) | 343 | 343 | 343 |
| Git launches | 415 | 816 | **886** | **374** | 534 |
| all launches | n/a | 949 | **1,229** | **717** | 877 |
| single / MIRV / unified (all) | 215 / 200 (unified not separate) | 746 / 54 / 16 (git) | 1,181 / 41 / 7 | 514 / 197 / 6 | 676 / 193 / 8 |
| single / MIRV / unified (git only) | | | 838 / 41 / 7 | 171 / 197 / 6 | 333 / 193 / 8 |
| Bands 1..6 (all) | (5 log bins) | 52/289/341/109/21/4 (git) | 212/403/423/165/20/6 | 148/174/221/142/26/6 | 158/235/305/150/23/6 |
| Nations of launches | h165 cl236 cx10 au4 | | human 544, claude 568, codex 73, automation 16, chatgpt 28 (inferred) | h382 cl273 cx28 au6 chatgpt 28 | h444 cl324 cx67 au14 gpt 28 |
| MIRV warheads, max | 10+ | 8+ | 58 (one fleet launch) | 29 | 59 |
| First tests (new lineage) | | | 223 | 200 | 211 |
| Nation firsts / generation firsts (launches) | | | 5 / 13 | 5 / 11 | 5 / 12 |
| Commits over the 20,000-line cap | | | 84 | 84 | 84 |

Non-git launches (343): human 296, Claude 11, Codex 8, ChatGPT-inferred (time only) 28. First non-git test 2017-05-01
(spine: 2020-12; it counted births only and no updates).

First appearances (default arm, `nations.json`): human first event 2011-08-25, first test 2017-05-01; ChatGPT
2023-04-17 (first inferred test 2024-12-20); Claude 2026-01-20; Codex 2026-06-29 (first test 2026-07-02);
automation 2026-07-03; local seats 2026-07-18 (135 launches with a seat participating, 0 tests); OpenCode 2026-09-27
(0 tests, 0 launch windows). 37 generation rows, 13 enter (a chip enters at its first test).

## Waterfall from PROBE-00 (`waterfall.json`, reproducible with `parity.py`)

| Step | Episodes | Tests | Git launches | single / MIRV / unified |
|---|---|---|---|---|
| PROBE-00 parity switches | 1,207 | 1,047 | **415** | 208 / 200 / 7 (probe: 215 singles = 208 + 7) |
| exclude `third_party`-class commits in own lineages | 1,001 | 902 | 356 | 165 / 186 / 5 |
| lines cap 20,000 per commit | 1,001 | 902 | 356 | unchanged (cap moves bands only) |
| span cap 12 h | 1,001 | 902 | 374 | 174 / 195 / 5 |
| worktree births as targets (control arm) | 1,001 | 902 | **374** | 171 / 197 / 6 |
| `engagement_union: session` (default arm) | 1,001 | 902 | **886** | 838 / 41 / 7 |

My implementation reproduces PROBE-00 exactly (415 launches, 200 MIRV) under its switches, so the numbers compare.
Reasons for each difference:

- **1,207 to 1,001 episodes**: 1,151 commits by third-party-class authors sit in own lineages (forks and clones with
  Derek share over 5 percent; one fork alone holds 842 of them and about 520k lines). That is upstream history, not an
  operator engagement; dropped (`exclude_third_party_commits`). (The spine's one 2.96M-line launch may be this kind of import; not checked.)
- **Cap and span**: the cap changes bands only (84 commits); the 12 h cap splits chains PROBE-00 let run to 30 h.
- **Control 374 vs session 886**: the whole gap is grouping. Time proximity glues unrelated lineages worked within 2 h
  (and chains), session sharing only joins what one session touched.
- **Session arm vs the spine's 816**: different corpus (1,001 episodes now against its 935; the v1.4 merge and a later snapshot), and my MIRV targets count worktree births inside the episode window; no spine prototype to diff, so
  these two are the explained part, not an exact reconciliation.
- **Non-git 343 vs 133**: updates (file_update) added, bulk copies excluded (294,025 bulk-copied files not counted).

## What the grouping arm shows (for Derek's Verdict)

- Only **258 of 902 git tests have any joined session**, and only 6 sessions touch two lineages. Claude chat starts
  2026-05-08 and Codex 2026-06-29 in the corpus, so the session arm cannot see an engagement before then: it shows
  MIRVs only from worktree births (36 of 41 are one lineage with worktrees) plus the 6 multi-lineage sessions.
  The operator's curve (singles, then MIRVs, then unified) is still visible but thin: 41 MIRVs, 17 in 2026-09.
- The control arm shows the cascade Derek described (MIRVs from 2026-03, parity by May) but by proximity, which also
  merges coincidence. In March to May its MIRVs have no session behind them to prove them.
- Chaining in the session arm: p50 launch span 0.41 h; three outliers: a 33.6 h fleet MIRV of 58 targets, a 175.5 h
  two-target MIRV (a long session bridging two lineages), two launches 20 to 21 h.
- `session_or_nation` (STRATEGY's flooding arm) gives 193 MIRVs of 534 git launches, 36 percent.

## Receipt (`receipt.json`)

Input hashes (events, repos, sessions, hosts, actors, stats, relations, chatgpt_links), params hash
`ad9f2f0f...` (default; arms add one key), code hashes, output hashes (launches.json and nations.json per arm) and
the PNG hashes are in `receipt.json`. Compile twice, separate processes with randomised hash seeds
(`python -I`): byte-identical for all three arms. Whole lap runtime 5.5 s.

## Addendum: re-run on the later merge (pinned `cache/corpus-pin-0653`, task 1 re-merge of 06:53Z)

The collection worker re-merged the corpus while this lap was running (events 217k to 220k+, more non-git births from
the E: and C: roots). The numbers above are on the earlier merge, whose input files were overwritten (the receipt keeps
its hashes, the bytes are gone). Slice 3 therefore pins a copy of the new merge (`KW_CORPUS`), and slice 1 was re-run on
it: results in `merge-pin/` (same code, same switches; PNGs, receipts, `waterfall.json`).

| Measure | session (default) | time_window (control) | session_or_nation |
|---|---|---|---|
| Git episodes / tests | 1,054 / 954 | 1,054 / 954 | 1,054 / 954 |
| Non-git launches | 574 | 574 | 574 |
| Git launches | 938 | 390 | 560 |
| All launches | 1,512 | 964 | 1,134 |
| single / MIRV / unified | 1,458 / 47 / 7 | 749 / 209 / 6 | 921 / 204 / 9 |
| Bands 1..6 | 307/482/476/205/32/10 | 243/241/255/174/41/10 | 253/307/342/186/36/10 |
| Nations (human, chatgpt, claude, codex, automation) | 716 / 76 / 616 / 88 / 16 | 555 / 76 / 294 / 34 / 5 | 620 / 76 / 345 / 79 / 14 |
| Git tests with a joined session | 294 of 954 | same | same |

PROBE-00 parity on this merge is 429 launches (it was exactly 415 on the earlier one), so the same implementation holds;
the waterfall now runs 429, 372, 372, 390, 390, 938. The grouping gap (390 against 938 git launches) and the session
blindness before Claude chat begins (2026-05-08) are unchanged; compile twice is byte-identical for all three arms.
