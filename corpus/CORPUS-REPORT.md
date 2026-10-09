# CORPUS-REPORT.md: the Known World corpus run

Work item w-26069fe96149, collection day 2026-10-09. Written by the Merge manager (Sonnet 5.5) from
`corpus/merged/stats.json`, `repos.json` and the raw manifests by `collect/knownworld/report.py`; counts and verdicts
only, no corpus line is quoted. Merge is `collect/knownworld/merge.py` (deterministic, stdlib only: two runs give
byte-identical output).

## 1. Totals

| Measure | Value |
|---|---|
| Raw events collected (26 items) | 217,377 |
| Merged events (`corpus/merged/events.ndjson`) | 212,498 |
| Span, first to last event | 2011-08-25T19:45:52Z to 2026-10-09T12:45:04Z |
| Git lineages (repository components) | 121 |
| Local repository records walked (all hosts, mirrors included) | 170 |
| Non-git directory lineages (file births) | 135 |
| GitHub-only lineages (listed on GitHub, no clone) | 2 |
| Sessions (distinct class + session id, `sessions.json`) | 1,155 |
| chat_session records (one per transcript file or conversation) | 2,810 |
| chat_msg records (folded per session, role, minute) | 146,432 |
| Messages folded into those chat_msg records | 476,325 |
| Actors (class + name) | 2,272 |
| Candidate lineage links (never merged) | 6 |
| Null-ts events dropped by Merge | 710 |

The first event (2011-08-25) is the GitHub account's creation date (the `repo_born` of the 2011 fork). The first
commits are 2015-08 (PoE-Item-Filter-Creator, two commits, flagged third_party because their author is not in the
identity map), 2017-12 and 2018-08; the first chat is 2023-04 (ChatGPT).

## 2. Source coverage against SURVEY.md sections 1 to 3

Status: covered = collected and verified; partial = collected with a stated hole; absent = not collected, with the
reason. Event counts are raw item totals before Merge folding.

| SURVEY row | Status | Item(s) | Events | Reason / note |
|---|---|---|---|---|
| 1a C:\work top-level repos (34 listed, 10 linked worktrees, 1 bare) | covered | c-git-a, c-git-b, c-git-c | 5,957 | 3 shards by sha1(path); records: 1 bare, 33 repos, 10 worktrees; numstat missing on one partial clone |
| 1a C: nested repos (14) | covered | c-git-nested | 1,055 | all 14 SURVEY-listed nested repos found; the 10 missing roots are work-list globs that match nothing |
| 1b E:\work top-level repos (38) | covered | e-git-a, e-git-b, e-git-c | 14,449 | records: 37 repos, 1 worktrees; numstat skipped on the llama.cpp fork (partial clone, 11,272 commits): commit counts kept, ins/del are 0 |
| 1b E: nested repos (16) | covered | e-git-nested | 11,182 | all 16 SURVEY-listed nested repos found; the 18 missing roots are globs that match nothing |
| 1c Linux repositories (~25 + ~/work/worktrees 94) | covered | linux-git | 4,811 | 31 records; worktree branches read from the parents with `--all` (121 worktree events); zero-commit repos (jepa-*, hybrid-context-trial, git-local-probe) are not walked (immutable rule, 8 excluded); commandcenter-public is a tarball snapshot, not a repo |
| 1d AM4 git repositories (11) | covered | am4-git | 389 | over ssh, read-only; 4 shallow clones (ComfyUI, level-zero-tests, libpng, llama.cpp) and a partial clone (quest-build, numstat missing) |
| 1d AM4 non-git dirs (am4-dual-nvidia-poc, vllm-e3) | covered | am4-births | 120 | v1.4: births and updates over ssh (section 12) |
| 1e FX99 git repositories (4) | covered | fx99-git | 110 | continuity, fleet, fleet.git (bare), ledger |
| 1e FX99 non-git dirs (dmos, menu, liferaft, ai-bench, apps, cookbook) | covered | fx99-births | 249 | v1.4: births and updates over ssh (section 12) |
| 1f GitHub: 50 public repos (djcdevelopment) + steppe-integrations | partial | github-list, mirror-0, mirror-1 | 115 | public view only (gh not authenticated): 54 repo_born events, 12 repos mirrored; 2 forks skipped; private repos pending auth (section 8) |
| 2 C:\work non-git dirs (omen-perception, _retired, orchestration, tools, ...) | covered | c-births | 1,115 | 38 sources; skip list honoured (dotnet9, jdk17, godot, fieldlab-postgres-data, model, venvs) |
| 2 C: root dirs (hearth-var, dirty-diffs, omen-perception-authored, tuning, assessment, AM4-provision, OMEN_prep) | partial | c-births | (in c-births) | births and (v1.4) updates. Bulk-copied dirs are flagged `bulk_copy` (173 records) but their in-record timestamps (cycle.log lines, dirty-diffs content) were not read; hearth-var/execution/events.ndjson (573 events) is not in any item |
| 2 E:\work non-git dirs (comfy, vllm-xpu-win, start, battlemage, 8350, dump, ...) | covered | e-births | 890 | 49 sources plus loose files; models skipped |
| 3 ChatGPT export, normalized (380 conversations, 19,045 messages) | covered | chatgpt | 11,259 | metadata only; 4,932 system-role messages and 12 undated records dropped and counted; titles and text never read |
| 3 Claude Code, Windows archive zip (413 jsonl) | covered | claude-zip | 17,623 | `unzip -p` of allowlisted members only; archive never extracted; 412 members seen |
| 3 Claude Code, Windows live (1,042 jsonl) | covered | claude-win | 41,294 | history.jsonl (454 lines) not read: its fields are prompt text (contract section 2) |
| 3 Codex, Windows (432 jsonl, 10.6 GB) | covered | codex-win-a, codex-win-b | 64,022 | 2 shards of 216 files; auth.json excluded |
| 3 Claude Code, Linux (481 jsonl at survey, 499 at collect) | covered | claude-linux | 9,124 | live tree: a snapshot of 12:45Z; history.jsonl not read |
| 3 Codex, Linux (50 jsonl, 51 at collect) | covered | codex-linux | 5,804 | snapshot of 12:45Z; session_index.jsonl and history.jsonl not read (thread names are text) |
| 3 OpenCode sqlite (24 sessions) | covered | opencode | 209 | opened `mode=ro&immutable=1`: WAL contents may be missed |
| 3 HEARTH ledger, Linux (472,077 lines) and Windows copy (90,784) | covered | hearth-ledger | 25,985 | 535,587 polling rows dropped and counted; 1,293 event_ids present in both copies deduped; args_preview, result_digest and error text never read |
| 3 Continuity (`ct`) ledgers: omen-linux, am4, fx99 | covered | continuity-runs | 869 | event bodies never read; imported transcript copies under `transcripts/` not read (duplicates of Claude and OpenCode sessions) |
| 3 deepagents runs and hearth-production obs-offload artifacts | covered | continuity-runs | (in continuity-runs) | 133 run directories and 401 per-call observations; counts only |
| 3 assessment transcripts (3 runs, C:) | covered | continuity-runs | (in continuity-runs) | 3 run records; counts only |
| 3 Downloads session exports (6 zips) | absent | - | 0 | SURVEY: unopened unless Scope decides they add span; Scope did not; the chat span is already continuous 2023-04 to 2026-10 without them |

Chat coverage by source: ChatGPT 2023-04 to 2026-03, Claude zip 2026-05 to 06, Windows live Claude and Codex from
2026-06-29, Linux Claude, Codex and OpenCode from 2026-09-27 to the snapshot. SURVEY.md calls this continuous; the
merged corpus shows one hole: **no chat source covers 2026-04** (the ChatGPT export ends 2026-03-12 and the first
Claude transcript is 2026-05-09). Commits, births and the HEARTH ledger are the only record of that stretch. Months
before 2024-11 are sparse because the ChatGPT export holds few conversations then, not because a source is missing.

## 3. Reconciliation of commit counts

Two reconciliations. First, per item: the commit total the extractor declared in its repo records (`rev-list --count
--all`) against the commit events it emitted, and the Haiku verifiers' independent recount. Second, per repository
against the SURVEY.md figures. Merge then folds identical shas (section 5).

| Item | Repo records | Declared commits | Commit events | Declared vs events | Verifier |
|---|---|---|---|---|---|
| am4-git | 11 | 368 | 368 | match | ok |
| c-git-a | 14 | 496 | 496 | match | ok |
| c-git-b | 14 | 1,648 | 1,648 | match | ok |
| c-git-c | 16 | 3,390 | 3,390 | match | ok |
| c-git-nested | 14 | 1,020 | 1,020 | match | ok |
| e-git-a | 17 | 2,097 | 2,097 | match | ok |
| e-git-b | 6 | 11,679 | 11,679 | match | ok |
| e-git-c | 15 | 311 | 311 | match | ok |
| e-git-nested | 16 | 10,668 | 10,668 | match | ok |
| fx99-git | 4 | 102 | 102 | match | ok |
| linux-git | 31 | 4,165 | 4,165 | match | ok |
| mirror-0 | 8 | 39 | 39 | match | ok |
| mirror-1 | 4 | 3 | 3 | match | ok |

Per-repository check against SURVEY.md sections 1a, 1b, 1c and the nested lists: **116 exact, 3 differ, 0 not found**
of 119 rows. SURVEY gives no per-repository counts for AM4 or FX99; there the verifiers' recounts (AM4 368 commits in
11 repos, FX99 102 in 4) equal the manifests.

Rows that are not exact (the survey is a snapshot taken before collection; a repository that gained commits since, or
whose composite row sums several records, differs by design):

| Host | SURVEY row | SURVEY | Corpus | Delta | Verdict |
|---|---|---|---|---|---|
| omen-linux | ~/.continuity/ledger | 518 | 519 | +1 | ours +1 |
| omen-linux | ~/work/discengine | 32 | 38 | +6 | ours +6 |
| omen-linux | ~/work/lab | 30 | 31 | +1 | ours +1 |

Linux deltas are repositories that were still being committed to on 2026-10-09 (continuity ledger, discengine, lab).
Nothing in the corpus is short of a SURVEY figure without a reason listed above.

## 4. Event totals (merged)

### Per kind

| Kind | Events |
|---|---|
| chat_msg | 146,432 |
| commit | 32,121 |
| offload_call | 26,386 |
| chat_session | 2,810 |
| file_birth | 2,030 |
| file_update | 1,090 |
| branch | 790 |
| run | 235 |
| receipt | 233 |
| worktree | 204 |
| repo_born | 167 |

### Per host

| Host | Events |
|---|---|
| omen-c | 93,727 |
| omen-e | 61,602 |
| omen-linux | 45,346 |
| cloud | 11,259 |
| fx99 | 301 |
| am4 | 209 |
| github | 54 |

### Per actor class

| Actor class | Events |
|---|---|
| claude | 95,723 |
| codex | 71,842 |
| third_party | 22,670 |
| chatgpt | 11,259 |
| human | 9,141 |
| automation | 1,112 |
| local_model | 542 |
| opencode | 209 |

### Per source and kind

| Source / kind | Merged | Raw |
|---|---|---|
| chatgpt_export/chat_msg | 10,879 | 10,879 |
| chatgpt_export/chat_session | 380 | 380 |
| claude_jsonl/chat_msg | 66,023 | 66,113 |
| claude_jsonl/chat_session | 1,925 | 1,928 |
| codex_jsonl/chat_msg | 69,345 | 69,345 |
| codex_jsonl/chat_session | 481 | 481 |
| continuity/receipt | 233 | 233 |
| continuity/run | 99 | 99 |
| deepagents_runs/offload_call | 401 | 401 |
| deepagents_runs/run | 136 | 136 |
| fs_births/file_birth | 2,030 | 2,030 |
| fs_births/file_update | 1,090 | 1,090 |
| git_repo/branch | 790 | 1,670 |
| git_repo/commit | 32,121 | 35,986 |
| git_repo/repo_born | 113 | 154 |
| git_repo/worktree | 204 | 204 |
| github_api/repo_born | 54 | 54 |
| hearth_ledger/offload_call | 25,985 | 25,985 |
| opencode_db/chat_msg | 185 | 185 |
| opencode_db/chat_session | 24 | 24 |

### Per year-month

| Year-month | Total | commit | chat_msg | chat_session | offload_call | other |
|---|---|---|---|---|---|---|
| 2011-08 | 1 | 0 | 0 | 0 | 0 | 1 |
| 2014-05 | 2 | 0 | 0 | 0 | 0 | 2 |
| 2015-08 | 5 | 2 | 0 | 0 | 0 | 3 |
| 2016-06 | 1 | 0 | 0 | 0 | 0 | 1 |
| 2016-11 | 2 | 0 | 0 | 0 | 0 | 2 |
| 2017-05 | 1 | 0 | 0 | 0 | 0 | 1 |
| 2017-12 | 5 | 1 | 0 | 0 | 0 | 4 |
| 2018-01 | 1 | 0 | 0 | 0 | 0 | 1 |
| 2018-04 | 3 | 0 | 0 | 0 | 0 | 3 |
| 2018-05 | 6 | 0 | 0 | 0 | 0 | 6 |
| 2018-06 | 9 | 0 | 0 | 0 | 0 | 9 |
| 2018-07 | 12 | 0 | 0 | 0 | 0 | 12 |
| 2018-08 | 40 | 11 | 0 | 0 | 0 | 29 |
| 2018-09 | 17 | 0 | 0 | 0 | 0 | 17 |
| 2018-10 | 11 | 0 | 0 | 0 | 0 | 11 |
| 2018-11 | 3 | 0 | 0 | 0 | 0 | 3 |
| 2018-12 | 19 | 0 | 0 | 0 | 0 | 19 |
| 2019-01 | 5 | 0 | 0 | 0 | 0 | 5 |
| 2019-02 | 8 | 0 | 0 | 0 | 0 | 8 |
| 2019-03 | 11 | 0 | 0 | 0 | 0 | 11 |
| 2019-04 | 12 | 0 | 0 | 0 | 0 | 12 |
| 2019-05 | 14 | 1 | 0 | 0 | 0 | 13 |
| 2019-06 | 19 | 0 | 0 | 0 | 0 | 19 |
| 2019-07 | 6 | 2 | 0 | 0 | 0 | 4 |
| 2019-08 | 1 | 0 | 0 | 0 | 0 | 1 |
| 2019-09 | 1 | 0 | 0 | 0 | 0 | 1 |
| 2019-10 | 2 | 2 | 0 | 0 | 0 | 0 |
| 2019-11 | 2 | 2 | 0 | 0 | 0 | 0 |
| 2020-02 | 1 | 0 | 0 | 0 | 0 | 1 |
| 2020-03 | 1 | 0 | 0 | 0 | 0 | 1 |
| 2020-05 | 2 | 2 | 0 | 0 | 0 | 0 |
| 2020-06 | 1 | 0 | 0 | 0 | 0 | 1 |
| 2020-07 | 1 | 0 | 0 | 0 | 0 | 1 |
| 2020-11 | 16 | 15 | 0 | 0 | 0 | 1 |
| 2020-12 | 2 | 0 | 0 | 0 | 0 | 2 |
| 2021-03 | 10 | 0 | 0 | 0 | 0 | 10 |
| 2021-05 | 19 | 18 | 0 | 0 | 0 | 1 |
| 2021-06 | 21 | 20 | 0 | 0 | 0 | 1 |
| 2021-07 | 20 | 20 | 0 | 0 | 0 | 0 |
| 2021-08 | 35 | 35 | 0 | 0 | 0 | 0 |
| 2021-09 | 30 | 30 | 0 | 0 | 0 | 0 |
| 2021-10 | 25 | 20 | 0 | 0 | 0 | 5 |
| 2021-11 | 12 | 12 | 0 | 0 | 0 | 0 |
| 2021-12 | 13 | 13 | 0 | 0 | 0 | 0 |
| 2022-01 | 26 | 23 | 0 | 0 | 0 | 3 |
| 2022-02 | 14 | 14 | 0 | 0 | 0 | 0 |
| 2022-03 | 11 | 8 | 0 | 0 | 0 | 3 |
| 2022-04 | 4 | 4 | 0 | 0 | 0 | 0 |
| 2022-05 | 42 | 39 | 0 | 0 | 0 | 3 |
| 2022-06 | 37 | 37 | 0 | 0 | 0 | 0 |
| 2022-07 | 48 | 48 | 0 | 0 | 0 | 0 |
| 2022-08 | 23 | 23 | 0 | 0 | 0 | 0 |
| 2022-09 | 12 | 12 | 0 | 0 | 0 | 0 |
| 2022-10 | 43 | 38 | 0 | 0 | 0 | 5 |
| 2022-11 | 20 | 18 | 0 | 0 | 0 | 2 |
| 2022-12 | 49 | 49 | 0 | 0 | 0 | 0 |
| 2023-01 | 29 | 29 | 0 | 0 | 0 | 0 |
| 2023-02 | 21 | 20 | 0 | 0 | 0 | 1 |
| 2023-03 | 318 | 308 | 0 | 0 | 0 | 10 |
| 2023-04 | 217 | 204 | 6 | 2 | 0 | 5 |
| 2023-05 | 266 | 265 | 0 | 0 | 0 | 1 |
| 2023-06 | 266 | 264 | 0 | 0 | 0 | 2 |
| 2023-07 | 248 | 248 | 0 | 0 | 0 | 0 |
| 2023-08 | 270 | 269 | 0 | 0 | 0 | 1 |
| 2023-09 | 362 | 357 | 0 | 0 | 0 | 5 |
| 2023-10 | 351 | 335 | 6 | 3 | 0 | 7 |
| 2023-11 | 362 | 351 | 2 | 1 | 0 | 8 |
| 2023-12 | 345 | 339 | 0 | 0 | 0 | 6 |
| 2024-01 | 536 | 532 | 0 | 0 | 0 | 4 |
| 2024-02 | 464 | 461 | 0 | 0 | 0 | 3 |
| 2024-03 | 443 | 438 | 0 | 0 | 0 | 5 |
| 2024-04 | 526 | 522 | 0 | 0 | 0 | 4 |
| 2024-05 | 514 | 508 | 0 | 0 | 0 | 6 |
| 2024-06 | 421 | 415 | 0 | 0 | 0 | 6 |
| 2024-07 | 479 | 472 | 0 | 0 | 0 | 7 |
| 2024-08 | 415 | 389 | 0 | 0 | 0 | 26 |
| 2024-09 | 370 | 348 | 0 | 0 | 0 | 22 |
| 2024-10 | 441 | 417 | 0 | 0 | 0 | 24 |
| 2024-11 | 596 | 549 | 6 | 1 | 0 | 40 |
| 2024-12 | 431 | 371 | 34 | 5 | 0 | 21 |
| 2025-01 | 608 | 467 | 98 | 12 | 0 | 31 |
| 2025-02 | 463 | 411 | 10 | 3 | 0 | 39 |
| 2025-03 | 560 | 502 | 20 | 5 | 0 | 33 |
| 2025-04 | 419 | 394 | 17 | 3 | 0 | 5 |
| 2025-05 | 695 | 600 | 63 | 6 | 0 | 26 |
| 2025-06 | 587 | 531 | 33 | 4 | 0 | 19 |
| 2025-07 | 1,029 | 803 | 145 | 29 | 0 | 52 |
| 2025-08 | 946 | 788 | 100 | 16 | 0 | 42 |
| 2025-09 | 796 | 651 | 91 | 22 | 0 | 32 |
| 2025-10 | 790 | 666 | 73 | 17 | 0 | 34 |
| 2025-11 | 1,669 | 804 | 784 | 43 | 0 | 38 |
| 2025-12 | 3,376 | 763 | 2,535 | 51 | 0 | 27 |
| 2026-01 | 3,816 | 578 | 3,137 | 67 | 0 | 34 |
| 2026-02 | 3,211 | 684 | 2,420 | 65 | 0 | 42 |
| 2026-03 | 4,266 | 2,616 | 1,299 | 25 | 0 | 326 |
| 2026-04 | 1,122 | 928 | 0 | 0 | 0 | 194 |
| 2026-05 | 10,245 | 1,193 | 8,597 | 185 | 0 | 270 |
| 2026-06 | 10,421 | 1,139 | 8,838 | 222 | 0 | 222 |
| 2026-07 | 24,576 | 2,827 | 19,641 | 380 | 1,264 | 464 |
| 2026-08 | 56,492 | 2,583 | 52,833 | 580 | 108 | 388 |
| 2026-09 | 39,496 | 2,401 | 33,031 | 557 | 1,873 | 1,634 |
| 2026-10 | 37,467 | 862 | 12,613 | 506 | 23,141 | 345 |

## 5. Dropped counters

| Item | null_ts | polling | decode_errors | other_role | null_ts_emitted | deduped in item | Warnings |
|---|---|---|---|---|---|---|---|
| am4-births | 0 | 0 | 0 | 0 | 0 | 0 | - |
| am4-git | 0 | 0 | 0 | 0 | 0 | 0 | roots_missing:93; numstat_failed:partial_clone_missing_blobs |
| c-births | 0 | 0 | 0 | 0 | 0 | 0 | - |
| c-git-a | 0 | 0 | 0 | 0 | 9 | 0 | - |
| c-git-b | 0 | 0 | 0 | 0 | 26 | 0 | - |
| c-git-c | 0 | 0 | 0 | 0 | 122 | 0 | numstat_failed:partial_clone_missing_blobs |
| c-git-nested | 0 | 0 | 0 | 0 | 9 | 0 | roots_missing:10 |
| chatgpt | 12 | 0 | 0 | 4,932 | 0 | 0 | - |
| claude-linux | 0 | 0 | 0 | 0 | 0 | 0 | - |
| claude-win | 0 | 0 | 0 | 0 | 0 | 0 | - |
| claude-zip | 0 | 0 | 0 | 0 | 0 | 0 | - |
| codex-linux | 0 | 0 | 0 | 0 | 0 | 0 | - |
| codex-win-a | 0 | 0 | 0 | 0 | 0 | 0 | - |
| codex-win-b | 0 | 0 | 0 | 0 | 0 | 0 | - |
| continuity-runs | 0 | 0 | 0 | 0 | 0 | 0 | - |
| e-births | 0 | 0 | 0 | 0 | 0 | 0 | - |
| e-git-a | 0 | 0 | 0 | 0 | 70 | 0 | - |
| e-git-b | 0 | 0 | 0 | 0 | 74 | 0 | numstat_failed:partial_clone_missing_blobs |
| e-git-c | 0 | 0 | 0 | 0 | 16 | 0 | - |
| e-git-nested | 0 | 0 | 0 | 0 | 79 | 0 | roots_missing:18 |
| fx99-births | 0 | 0 | 0 | 0 | 0 | 0 | - |
| fx99-git | 0 | 0 | 0 | 0 | 0 | 0 | roots_missing:6 |
| github-list | 0 | 0 | 0 | 0 | 0 | 0 | pending auth: private repos not listed |
| hearth-ledger | 0 | 535,587 | 0 | 0 | 0 | 1,293 | - |
| linux-births | 0 | 0 | 0 | 0 | 0 | 0 | - |
| linux-git | 0 | 0 | 0 | 0 | 297 | 0 | roots_missing:12 |
| mirror-0 | 0 | 0 | 0 | 0 | 4 | 0 | - |
| mirror-1 | 0 | 0 | 0 | 0 | 4 | 0 | - |
| opencode | 0 | 0 | 0 | 0 | 0 | 0 | sqlite_immutable_wal_may_be_missed |

`null_ts` = records the extractor could not bucket (dropped there); `null_ts_emitted` = records emitted with a null
`ts` (a branch with no unique commit, a bad commit date), which Merge drops. `other_role` = ChatGPT system messages
(not user, assistant or tool).

Merge-level drops and folds:

| Counter | Value |
|---|---|
| Null-ts events dropped, git_repo/branch | 702 |
| Null-ts events dropped, git_repo/repo_born | 8 |
| Duplicates folded, branch | 178 |
| Duplicates folded, chat_msg | 90 |
| Duplicates folded, chat_session | 3 |
| Duplicates folded, commit | 3,865 |
| Duplicates folded, repo_born | 33 |
| Events loaded | 217,377 |
| Events written | 212,498 |

Check: loaded 217,377 - duplicates 4,169 - null-ts 710 = written 212,498.

Claude zip against the live tree: 0 sessions overlap (the zip ends 2026-06-22, the live tree starts 2026-07-10). Three
`chat_session` and 90 `chat_msg` duplicates were found inside the Linux tree (three transcript file names occur twice
under `~/.claude/projects` with one session id) and folded. Dedupe is on the extractor's ref (session, file stem,
role, minute), because message uuids are folded away at collection; a resumed session that copies history into a new
file under a new stem would be counted twice and cannot be detected without reading message ids.

## 6. Lineage components and candidate links

| Link basis | Unions made |
|---|---|
| root | 30 |
| sha_overlap | 3 |
| worktree | 16 |

21 components hold more than one repository record; the largest has 11. Unions made: 30 by shared root, 3 by shared
sha, 16 by linked worktree. No squash mirror needed the remote-URL or root-tree rule (the `private-migration` copies
share root commits), and no shallow clone needed the boundary or remote fallback: the six shallow third-party clones
(one to six commits each) stay singleton lineages (`rooted: false`, id `github:<owner>/<name>` where a remote names
one).

Lineages that merged several records (names are directory names): 

| Lineage (first 8 of id) | Records | Hosts | Unique commits | Names |
|---|---|---|---|---|
| 6a0d3084 | 11 | omen-linux,omen-c | 1,439 | commandcenter, commandcenter-d1-guard-9f306fb, commandcenter-flash-base, commandcenter-flash-foreman, commandc |
| 09f02f35 | 8 | omen-linux,omen-c | 26 | notebook, notebook-27b, notebook-32b, notebook-cold, notebook-cold2, notebook-devstral, notebook-gemma |
| 1fe7d04a | 6 | omen-c,omen-e | 2,118 | baseline, comfy, gallery-stage-baseline-20260915, game, lumberjacks, lumberjacks-platform |
| 26c08466 | 5 | omen-e,am4 | 11,682 | llama.cpp, llama.cpp-src, llamacpp-knee, llamacpp-knee-pr, llamacpp-qwen38 |
| 168915c9 | 4 | omen-c,omen-e | 303 | comfystewardview, gallery-stage-steward-20260915, steward-spatial-lab, temp |
| 25227eda | 4 | omen-c,am4 | 373 | comfy-quest, comfy-quest-incomplete, gallery-stage-quest-20260915, quest-build-20260915 |
| 1bad53ca | 3 | omen-linux,omen-c | 18 | deepagents-linux, deepagents-poc |
| 91653aae | 3 | omen-linux,am4,fx99 | 80 | continuity |
| 0a2dd31e | 2 | omen-linux,omen-c | 36 | conductor-mirror |
| 3450a4ea | 2 | omen-c,omen-e | 37 | ember |
| 352eb10e | 2 | omen-c,omen-e | 36 | manifest |
| 447e150d | 2 | omen-e,am4 | 12 | chatgpt_parser, chatgpt_parser_run |
| 484f54f6 | 2 | omen-linux,omen-c | 25 | memsplice |
| 4bb4fbce | 2 | omen-linux,omen-c | 3 | deepagents-shot-director |
| 681d6bdf | 2 | omen-e | 48 | azure-event-grid-viewer, event-viewer |
| 7607a792 | 2 | omen-c,omen-e | 56 | gad |
| 9028819e | 2 | omen-c | 47 | irc, irc-hearth-adapter |
| ac1a64cf | 2 | fx99 | 41 | fleet |
| b54645d2 | 2 | omen-c,omen-e | 88 | steppeintegrations-site, www |
| ec52961c | 2 | omen-c,am4 | 8 | sovereign-shards |
| f69a5b1a | 2 | omen-linux,omen-e | 13 | liveview-ui-run, ui |

Candidate links (recorded in `repos.json`, none merged):

| Lineage A | Lineage B | Basis | Key |
|---|---|---|---|
| ledger (0a29dacd) | ledger (6f8bd366) | name | ledger |
| ledger (0a29dacd) | ledger (6f8bd366) | root_tree | e0aedfc141fa |
| ledger (0a29dacd) | ledger (7fb8daa9) | name | ledger |
| ledger (0a29dacd) | ledger (7fb8daa9) | root_tree | e0aedfc141fa |
| ledger (6f8bd366) | ledger (7fb8daa9) | name | ledger |
| ledger (6f8bd366) | ledger (7fb8daa9) | root_tree | e0aedfc141fa |

The three candidates are the `ct` ledgers on omen-linux, am4 and fx99: same directory name and an identical root tree
(the empty bookkeeping commit), different root commits. They are separate ledgers by design, so they stay unmerged.
Name-only and remote-only matches among the other lineages produced no further pairs: every repository that shares a
name or a remote across hosts also shares a root commit and is already one lineage.

Joins by path (chat, deepagents and ledger events to a lineage, by host and depth-2 path, Windows case-folded):

| Source | To a git lineage | To a non-git dir lineage | Unmatched path | No path |
|---|---|---|---|---|
| chatgpt_export | 0 | 0 | 0 | 11,259 |
| claude_jsonl | 46,676 | 4,737 | 15,807 | 821 |
| codex_jsonl | 43,697 | 2,635 | 17,763 | 5,731 |
| continuity | 0 | 0 | 0 | 332 |
| deepagents_runs | 133 | 0 | 3 | 401 |
| hearth_ledger | 0 | 0 | 0 | 25,985 |
| opencode_db | 14 | 0 | 195 | 0 |

ChatGPT, HEARTH ledger and `ct` events carry no path, so they stay unjoined (`repo` null). Unmatched paths are working
directories that hold no repository (home, scratch, `work/trial`, worktrees, directories since deleted).

## 7. Items that failed verification, and why

One item of 26 returned `verify_ok=false`:

- **claude-linux**: verify_ok=false, privacy_ok=false: the scan flagged one text line over 400 characters in card.md
  (the card, not a corpus record); all counts matched. Fixed by reflowing the card line; privacy_scan.py now exits 0
  on corpus/raw.

Verifier remarks that were not failures:

- **codex-win-a**: privacy scan counted 29,952 records against 29,950 events: the two extra are manifest.json and
  checkpoint.json, which the scanner counts as records; no delta in events.
- **codex-linux**: verifier recount differed from the manifest raw sum by 13 lines (0.02%): the Linux session trees
  are live and grew between the collect and the verify; the corpus is a snapshot of 12:45Z.
- **c-births**: privacy scan counted 609 records against 607 events (manifest and checkpoint); no delta.

No quirk described a toolkit bug, so no extractor was patched and no item was re-run. Quirks that matter for later
runs: partial clones lose numstat (ins/del 0, `meta.no_numstat`) in am4-git (quest-build), c-git-c and e-git-b
(llamacpp-qwen38); `roots_missing` warnings count work-list globs that matched nothing, not repositories that failed.

After the card fix, `privacy_scan.py corpus/raw` and `privacy_scan.py corpus/merged` both exit 0.

## 8. GitHub list and auth state

`gh` is installed but **not authenticated**: the manifest warning is `pending auth: private repos not listed`, and the
mirror phase reported `auth: unavailable`. The list is the public view (unauthenticated budget 60 requests per hour):
54 repo_born events (djcdevelopment 50, steppe-integrations 4; 4 forks). Private repositories named in SURVEY
(404-isolate, isolate, notebook, steppeintegrations-site, the E: privates) are present in the corpus through their
local git history, but **their GitHub-side metadata (`created_at`, size, language) is pending**: after `gh auth
login`, re-run `github-list` and `clone_mirrors.py` to add them. Of the 54 listed repositories, 52 matched a lineage
by remote URL and 2 (the forks open-notebook and personal_website) have no clone and stay GitHub-only lineages. Mirror
phase: 12 cloned (`mirror-0` 8 repos, `mirror-1` 4), 2 forks skipped.

## 9. Local-seat arm

The local-seat arm (repo cards for the Linux repositories through `local_generate`, graded against the Haiku arm for
substance and form) was **deferred**: the 30B and both AM4 tool seats are absent under the bench27 all-27B hold on
2026-10-09. This is recorded, not re-routed: no cloud or other seat was substituted (H-2). No repository cards exist
from any arm, so the Haiku-versus-30B-versus-AM4 grading table and its three capability records are empty. The Haiku
arm wrote per-item cards (`corpus/raw/<item>/card.md`), which are source cards, not repo cards.

## 10. Chat session counts against file counts

| Item | Source files | Sources seen | chat_session records | Messages folded | Raw lines or rows |
|---|---|---|---|---|---|
| chatgpt | 2 files (conversations + messages) | 2 | 380 | 19,045 | 19,425 |
| claude-zip | 412 zip members | 412 | 405 | 69,096 | 97,929 |
| claude-win | 1,042 jsonl | 1,042 | 1,025 | 206,077 | 315,055 |
| claude-linux | 499 jsonl | 499 | 498 | 49,018 | 84,774 |
| codex-win-a | 216 jsonl | 216 | 215 | 63,221 | 379,454 |
| codex-win-b | 216 jsonl | 216 | 215 | 67,097 | 401,641 |
| codex-linux | 51 jsonl | 51 | 51 | 7,269 | 62,505 |
| opencode | 24 sessions in 1 db | 1 | 24 | 953 | 953 |

Session records are one per transcript file that held at least one user or assistant line; files with none
(queue-operation only, empty) produce no record (claude-zip 7, claude-win 17, claude-linux 1, codex-win-a 1,
codex-win-b 1, codex-linux 0). Claude subagent transcripts share their parent's session id, so the 1,925 Claude
records make 498 distinct sessions in `sessions.json` (`segments` says how many files each had). By class: chatgpt
380, claude 498, codex 253, opencode 24.

## 11. Limits and open items

- `repos.json` carries `third_party` by the CONTRACT rule (derek_share under 0.05, or a foreign org with no Derek
  identity) and `foreign_org` separately: resonantOS and showcase-site, where Derek has some commits, are
  `third_party: false, foreign_org: true`; the renderer may treat `foreign_org` as third-party.
- Region (`repos.json.region`) is null for every lineage: it is assigned by Compile (and by the deferred local-seat
  arm), not by Merge.
- Branch events cannot be matched across copies by name (the extractor hashes the repository path into the ref); Merge
  dedupes them per lineage and birth second, keeping the busiest copy. 178 were folded.
- Lineage ids of rootless components are not root shas: empty or one-commit clones carry `github:<owner>/<name>`
  (lower case) when a remote names one, else a `dir:` id (one empty local repo).
- Commit `ins`/`del` are 0 where numstat was unavailable (`meta.no_numstat`): about 11.5 thousand raw commit events,
  mostly the llamacpp-qwen38 partial clone (11,272 commits).
- Linux Claude and Codex trees are live; the corpus is the 12:45Z snapshot. A later run will add the sessions since
  then (this one included).
- Windows `hearth-var/execution/events.ndjson` (573 events) and the in-record timestamps of the bulk-copied C:
  directories are not collected (section 2).
- AM4 and FX99 non-git directories are collected from v1.4 (`am4-births`, `fx99-births`, section 12); non-git
  omen-linux directories likewise (`linux-births`).
- GitHub private repositories and fork metadata are pending authentication (section 8).

## 12. File activity extension (v1.4)

Section 7 of the v1.4 request; numbered 12 here because sections 7 to 11 already exist. Source `fs_births` now emits
`file_update` beside `file_birth`: one record per (depth-2 directory, day), counted only when the file's last-modified
day differs from its birth day. Items: `c-births`, `e-births`, `linux-births`, `am4-births`, `fx99-births`. Counts
only.

| Item | Status | file_birth records | Files folded (births) | Bulk-copy births | file_update records | Files folded (updates) | Bulk-copy updates | Sources | Skipped | Files with null mtime |
|---|---|---|---|---|---|---|---|---|---|---|
| am4-births | complete | 109 | 18,372 | 59 | 11 | 2,393 | 2 | 2 | 0 | 0 |
| c-births | complete | 607 | 174,498 | 107 | 508 | 34,863 | 146 | 38 | 0 | 28,661 |
| e-births | complete | 662 | 81,408 | 66 | 228 | 12,499 | 28 | 49 | 0 | 0 |
| fx99-births | complete | 52 | 3,873 | 14 | 197 | 3,475 | 31 | 6 | 0 | 0 |
| linux-births | complete | 600 | 28,769 | 101 | 146 | 5,474 | 82 | 49 | 0 | 0 |
| total |  | 2,030 | 306,920 | 347 | 1,090 | 58,704 | 289 |  |  |  |

Per host and year-month, file activity = files folded into births + updates (merged corpus, after dedupe):

| Year-month | am4 | fx99 | omen-c | omen-e | omen-linux |
|---|---|---|---|---|---|
| 2014-05 | 0 | 0 | 0 | 2 | 0 |
| 2016-06 | 0 | 0 | 1 | 0 | 0 |
| 2016-11 | 0 | 0 | 10 | 0 | 0 |
| 2017-05 | 0 | 0 | 3 | 0 | 0 |
| 2017-12 | 0 | 0 | 115 | 0 | 0 |
| 2018-01 | 0 | 0 | 2 | 0 | 0 |
| 2018-04 | 0 | 0 | 240 | 0 | 0 |
| 2018-05 | 0 | 4 | 48 | 0 | 0 |
| 2018-06 | 0 | 21 | 0 | 0 | 0 |
| 2018-07 | 0 | 182 | 0 | 0 | 0 |
| 2018-08 | 0 | 68 | 41 | 0 | 0 |
| 2018-09 | 0 | 216 | 0 | 0 | 0 |
| 2018-10 | 0 | 18 | 0 | 0 | 0 |
| 2018-11 | 0 | 3 | 1 | 0 | 0 |
| 2018-12 | 0 | 26 | 8 | 0 | 0 |
| 2019-01 | 0 | 6 | 0 | 0 | 0 |
| 2019-02 | 0 | 17 | 0 | 0 | 0 |
| 2019-03 | 0 | 158 | 0 | 0 | 0 |
| 2019-04 | 0 | 15 | 0 | 0 | 0 |
| 2019-05 | 0 | 49 | 0 | 0 | 0 |
| 2019-06 | 0 | 135 | 0 | 0 | 0 |
| 2019-07 | 0 | 9 | 0 | 0 | 0 |
| 2019-08 | 0 | 0 | 1 | 0 | 0 |
| 2019-09 | 0 | 0 | 123 | 0 | 0 |
| 2020-02 | 0 | 0 | 15 | 0 | 0 |
| 2020-03 | 0 | 0 | 0 | 5 | 0 |
| 2020-06 | 0 | 0 | 2 | 0 | 0 |
| 2020-07 | 0 | 0 | 3 | 0 | 0 |
| 2020-12 | 0 | 0 | 0 | 19 | 0 |
| 2021-03 | 0 | 0 | 65 | 6 | 0 |
| 2021-10 | 0 | 0 | 14 | 4 | 0 |
| 2022-01 | 0 | 0 | 6 | 2 | 0 |
| 2022-03 | 0 | 0 | 9 | 0 | 0 |
| 2022-05 | 0 | 0 | 11 | 28 | 0 |
| 2022-10 | 0 | 0 | 26 | 12 | 1,683 |
| 2022-11 | 0 | 0 | 0 | 0 | 57 |
| 2023-02 | 0 | 0 | 0 | 0 | 57 |
| 2023-03 | 0 | 0 | 75 | 1 | 0 |
| 2023-04 | 0 | 0 | 18 | 0 | 0 |
| 2023-06 | 0 | 0 | 0 | 12 | 60 |
| 2023-08 | 0 | 0 | 0 | 0 | 58 |
| 2023-09 | 0 | 0 | 156 | 1 | 0 |
| 2023-10 | 0 | 0 | 14 | 3 | 58 |
| 2023-11 | 0 | 0 | 285 | 142 | 0 |
| 2023-12 | 0 | 0 | 1 | 73 | 0 |
| 2024-01 | 0 | 0 | 6 | 0 | 0 |
| 2024-02 | 0 | 0 | 0 | 0 | 61 |
| 2024-03 | 0 | 0 | 4 | 18 | 0 |
| 2024-04 | 0 | 0 | 0 | 1 | 0 |
| 2024-05 | 0 | 0 | 0 | 1 | 0 |
| 2024-06 | 0 | 0 | 61 | 7 | 0 |
| 2024-07 | 0 | 0 | 5 | 10 | 0 |
| 2024-08 | 0 | 0 | 21 | 178 | 0 |
| 2024-09 | 0 | 0 | 152 | 95 | 0 |
| 2024-10 | 0 | 0 | 124 | 33 | 0 |
| 2024-11 | 0 | 0 | 1,311 | 60 | 0 |
| 2024-12 | 0 | 0 | 205 | 32 | 0 |
| 2025-01 | 0 | 0 | 204 | 45 | 0 |
| 2025-02 | 0 | 0 | 73 | 89 | 0 |
| 2025-03 | 0 | 6 | 63 | 20 | 10 |
| 2025-05 | 0 | 0 | 0 | 27 | 330 |
| 2025-06 | 0 | 0 | 0 | 21 | 0 |
| 2025-07 | 0 | 0 | 75 | 19 | 0 |
| 2025-08 | 0 | 0 | 430 | 109 | 0 |
| 2025-09 | 0 | 0 | 0 | 12 | 0 |
| 2025-10 | 0 | 0 | 18 | 118 | 0 |
| 2025-11 | 0 | 6 | 193 | 22 | 0 |
| 2025-12 | 0 | 0 | 0 | 6 | 0 |
| 2026-01 | 1,930 | 0 | 540 | 61 | 0 |
| 2026-02 | 38 | 0 | 2 | 6 | 0 |
| 2026-03 | 141 | 0 | 258 | 24,576 | 0 |
| 2026-04 | 0 | 0 | 6 | 4,389 | 0 |
| 2026-05 | 16 | 6 | 4,456 | 31,297 | 13 |
| 2026-06 | 0 | 8 | 60,249 | 5,059 | 0 |
| 2026-07 | 0 | 24 | 66,347 | 0 | 0 |
| 2026-08 | 0 | 2,961 | 16,083 | 6,542 | 0 |
| 2026-09 | 18,640 | 937 | 56,899 | 20,744 | 18,679 |
| 2026-10 | 0 | 2,473 | 283 | 0 | 13,177 |
| total | 20,765 | 7,348 | 209,361 | 93,907 | 34,243 |

- **Lower bound.** A filesystem keeps one last-modified time per file, so a file edited on ten days counts as one
  update day; update frequency and density are floors. A file whose mtime day equals its birth day is a birth only.
- **Null rule.** Births use the birth time (mtime if the filesystem has none); a mtime before 2005 (the 1970 and 1980
  placeholders) or in the future yields no update and is counted in the manifest as `update_null_mtime` (column
  above). Copied files can carry an mtime earlier than their birth: those count as updates on the mtime day.
- **Bulk copies.** A record is flagged `bulk_copy` when 80 percent or more of its files share birth seconds that hold
  100 or more files; the flagged counts are in the table. They are kept, not removed.
- **Skipped.** Nothing in these five items was skipped (no timeouts); never-walk directories (models, checkpoints,
  venvs, .venv, node_modules, .cache, .git, ComfyUI/models), credential-bearing files and symlinked roots are pruned
  inside the walk. `~/work/worktrees`, `~/work/amux` and `~/work/known-world` (this corpus) are excluded from
  `linux-births`; git repositories with commits stay with `*-git`.
- **Overlap.** Non-git directories can hold nested git repositories (for example under `trial`): their files count
  here and their commits in `linux-git`. Compile should treat file activity inside a directory that is also a lineage
  as density, not as new work.

Reproduce: `.venv/bin/python -I collect/knownworld/merge.py && .venv/bin/python -I collect/knownworld/report.py &&
.venv/bin/python -I collect/knownworld/privacy_scan.py corpus/merged` from `~/work/known-world` with
`PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 GIT_TERMINAL_PROMPT=0`.


## 13. Relations and ChatGPT links (task 1b)

`corpus/merged/relations.json` (`collect/knownworld/relations.py`) and `corpus/merged/chatgpt_links.json` (`collect/knownworld/chatgpt_links.py`). Both run with the system `python3 -I` (PyYAML is absent from `.venv`) from the repo root; output is deterministic and `privacy_scan.py corpus/merged` exits 0 with new validators in `allowlists.py`.

### 13a. Manifest repos joined to lineages

| Measure | Count |
|---|---|
| manifest repos (12 yaml files plus the jepa graph, lower-cased) | 88 |
| joined to a lineage | 83 |
| joined by dirname | 11 |
| joined by github | 72 |
| unjoined | 5 |
| lineages with no manifest entry | 179 |

Join order: github slug (basis `github`; the scanner forbids a key named `slug`), directory basename of `local_path`,
repo name, aliases, known renames. The name, alias and rename steps matched nothing new: the five renames join by
slug. Unjoined: resume, tempo, tempo-viewer, tensor, wow-code. `tempo` (the GAD centrepiece), `tempo-viewer` and `wow-
code` sit outside the collected roots (`E:\World of Warcraft`); `resume` has only the name-only candidate `resume-
linux`, which is never auto-merged; `tensor` has no clone.

### 13b. Edges

| Type | Edges |
|---|---|
| bridges_traffic_to | 1 |
| consumes | 73 |
| contract | 32 |
| control_plane_for | 1 |
| data_source | 1 |
| depends_on | 64 |
| describes_topology_for | 3 |
| extracted_from | 2 |
| hosts_awareness_for | 1 |
| leases_hardware_to | 3 |
| parent | 2 |
| produces_data_for | 31 |
| replaces | 2 |
| verifies | 7 |

| Scope | Edges |
|---|---|
| cross-constellation | 10 |
| intra | 213 |

10 self-edges dropped from the jepa graph (SURVEY said 8; 10 after lower-casing). 5 jepa edges target a constellation name, not a repo (`dst_kind: constellation`). 24 edges have `since: null` because an endpoint is unjoined. `since` is the later endpoint first_ts from this corpus; the jepa `valid_from` is kept only as `inferred_valid_from`.

### 13c. Integrations, top 10 lineages by count

| Lineage | Total | contracts out/in | data_sources | depends out/in | cross-constellation |
|---|---|---|---|---|---|
| baseline | 20 | 1/4 | 0 | 1/13 | 1 |
| b70tools | 12 | 3/0 | 0 | 1/8 | 0 |
| comfy-quest | 9 | 2/2 | 0 | 2/3 | 0 |
| commandcenter | 9 | 2/1 | 0 | 0/4 | 2 |
| manifest | 7 | 2/0 | 0 | 0/0 | 5 |
| selfiestick | 7 | 2/1 | 0 | 1/3 | 0 |
| isolate | 6 | 2/0 | 0 | 1/2 | 1 |
| comfystewardview | 5 | 0/1 | 0 | 3/1 | 0 |
| img | 5 | 0/3 | 0 | 2/0 | 0 |
| ingest | 5 | 1/1 | 0 | 2/1 | 0 |

59 lineages carry at least one integration. Intra-repo contracts are excluded.

### 13d. ChatGPT conversations

| Year | Conversations | With projects |
|---|---|---|
| 2023 | 6 | 0 |
| 2024 | 6 | 0 |
| 2025 | 211 | 0 |
| 2026 | 157 | 14 |
| total | 380 | 14 |

Conversations with a lineage match: 14; distinct lineages matched: 5 (ai-dev-system, ai-systems-research, liveview, stars-app, writing). Artifacts by type: code 3512, execution_output 367. Activity calendar: 189 days as the `chatgpt_activity` series.
Only drive-letter paths count (D: maps to omen-e); relative, `/mnt/data`, `C:/Users` and `C:/Python312` paths are dropped. All 14 conversations with projects date from 2026; SURVEY's 2025 drive-path claim (from the graph nodes) is not in these projections, so 2023-25 attribute by time only.



## 14. Repositories outside the work trees (task 1c)

Work items `e-root-git-a`, `e-root-git-b` (shards 0/2 and 1/2 of 41 E: repository paths), `c-root-git` and `e-root-births`, all `complete`, no skipped sources, privacy scan exit 0 on each and on `corpus/merged`. Repository paths come from a bounded find (maxdepth 5 below the E: root, `work` and the skip list excluded; C: `assessment` and `tuning` maxdepth 4) and are listed in `make_worklist.py` (`E_ROOT_REPOS`) so nested repositories are found. The find matched SURVEY 1g and added five repositories it did not name: `HANDOFF/_backup_staging/projects/meal-planner`, `omen/CC/GeneralsReplays` (a submodule of `omen/CC`), five `omen/steward-multi-era/deploy-worktree-creator-*` worktrees, `omen/CC` and `Tempo-worktrees/{agent-a, agent-b, agent-c, stream-f-gamma}`. `C:\Users\derek` holds no repositories at depth 4.

### 14a. Repositories found, by root

| Root | Repository | Commits (rev-list --all) | Notes |
|---|---|---|---|
| E: | gemini | 1 | |
| E: | HANDOFF/_backup_staging/projects/meal-planner | 3 | |
| E: | helloworld/old-goat-new-tricks | 17 | = llmquest |
| E: | omen/bf6-highlights-retired-20260828 | 12 | shares a root commit with omen/clippy |
| E: | omen/CC | 1754 | |
| E: | omen/CC/GeneralsReplays | 4 | submodule of omen/CC |
| E: | omen/clippy | 20 | |
| E: | omen/DMos | 72 | 7 linked worktrees (DMos-actor-controls, -chronicle, -chronicle-salience, -command-freshness, -rc1, -rehearsal, -secrets) |
| E: | omen/imagegen | 10 | |
| E: | omen/menu | 126 | |
| E: | omen/tensor | 2 | |
| E: | resume | 24 | 3 linked worktrees (resume-wt: claude-seat-receipts, gemini-proof-snapshot, linux-proof-review-20261006) |
| E: | World of Warcraft/code | 2 | = manifest wow-code |
| E: | World of Warcraft/Tempo | 295 | 11 linked worktrees (Tempo-wt-A, -A-1b9, -B..-F, Tempo-worktrees/{agent-a, agent-b, agent-c, stream-f-gamma}) |
| E: | World of Warcraft/tempo-viewer | 8 | |
| E: | omen/steward-multi-era/deploy-worktree-creator-{carousel, compact, explorer, guide, heatmap} | 0 (worktree records) | 5 linked worktrees of ComfyStewardView |
| C: | assessment | 5 | the work/assessment copy has 6 |
| C: | tuning | 1 | |

Totals: E: 41 repository records (15 repositories with their own history, 26 linked-worktree records); C: 2. Raw events: e-root-git-a 2134, e-root-git-b 318, c-root-git 10. Commit counts of the 15 E: repositories and 2 C: repositories equal `git rev-list --count --all` run by a second path; the 26 worktree records carry 0 commits by design (the `.git` file points at a Windows path; the toolkit resolves them through the parent's `.git/worktrees`, all 26 resolved).

### 14b. Duplicate lineages against existing records

| New record(s) | Lineage after merge | Joined with | Basis |
|---|---|---|---|
| omen/DMos and its 7 worktrees | 1 lineage, 72 commits | nothing else (no DMos copy under work/) | worktree |
| World of Warcraft/Tempo and its 11 worktrees | 1 lineage, 295 commits | nothing else | worktree |
| World of Warcraft/tempo-viewer, code | 1 lineage each | nothing else | root |
| resume and its 3 worktrees | 1 lineage, 26 commits | omen-linux `~/work/resume-linux.git` | root |
| omen/steward-multi-era/deploy-worktree-creator-* (5) | ComfyStewardView lineage, 303 commits | work/ComfyStewardView, gallery-stage-steward-20260915, steward-spatial-lab, E work/temp | worktree |
| omen/clippy, omen/bf6-highlights-retired-20260828 | one lineage, 20 commits | the clippy.git mirror clone; no clippy copy under work/ | root |
| omen/imagegen | 1 lineage, 10 commits | E work/img | root |
| omen/CC | 1 lineage, 1754 commits | C work/research/cnc-generals | root |
| helloworld/old-goat-new-tricks | 1 lineage, 17 commits | the llmquest.git mirror clone | root |
| omen/CC/GeneralsReplays, omen/menu, omen/tensor, gemini, meal-planner | new, 1 lineage each | none | |
| C assessment, tuning | existing git lineages | the work/ copies (same lineage; commits 6 and 1) | root |

`omen/menu` did not join the fx99 `~/menu` record (no shared history; no candidate record was produced). The births lineages `dir:omen-c:assessment` and `dir:omen-c:tuning` (from `c-births`) remain separate `dir` lineages from the git lineages of the same directories.

### 14c. Births and updates (e-root-births)

51 sources, 0 skipped. 1946 events: `file_birth` 1243 records covering 491,667 files, `file_update` 703 records covering 30,172 files (58 files had a null mtime).

| Top directory | Births (files) | Updates (files) |
|---|---|---|
| omen (non-repo children, e.g. steward-multi-era) | 464,167 | 22,594 |
| World of Warcraft (non-repo children) | 4,748 | 2,964 |
| repo-audit | 9,363 | 755 |
| _migration | 6,639 | 1,049 |
| continuity-evidence | 2,826 | 319 |
| HANDOFF | 1,262 | 1,240 |
| tmp | 1,258 | 1,172 |
| BF6-Highlights | 776 | 7 |
| wtviewer-skin-previewshots | 524 | 48 |
| wool | 37 | 0 |
| New folder | 22 | 22 |
| cold-storage | 15 | 1 |
| linux | 12 | 0 |
| loose files at the E: root (`.`) | 8 | 1 |
| IndexCard, hiking | 3 each | 0 |
| helloworld (loose), .claude, writing | 2, 1, 1 | 0 |
| wsl, wt, msdownld.tmp | no files | |

Recount by `find -type f` with the same prunes: 491,673 against 491,667 (difference 6, not isolated).

### 14d. Merged totals and relations

| Measure | Before | After |
|---|---|---|
| events_loaded | 217,377 | 221,785 |
| events_out (merged) | 212,498 | 216,753 |
| repo records | 170 | 213 |
| lineages | 258 (git 121, dir 135, github_only 2) | 309 (git 130, dir 177, github_only 2) |
| multi-record components | 21 | 30 |
| link basis (root / sha_overlap / worktree) | 30 / 3 / 16 | 37 / 4 / 42 |
| actors | 2,272 | 2,334 |
| name/root_tree candidates | 6 | 6 |
| null-ts events dropped | 710 | 760 |
| commit copies folded | 3,865 | 3,953 |

| Relations coverage | Before | After |
|---|---|---|
| manifest repos | 88 | 88 |
| joined | 83 | 88 |
| unjoined | 5 (resume, tempo, tempo-viewer, tensor, wow-code) | 0 |
| joined by github / dirname | 72 / 11 | 75 / 13 |
| lineages with no manifest entry | 179 | 226 |
| edges with `since: null` | 24 | 7 |
| edges | 223 | 223 |

resume, tensor and wow-code joined by directory name; tempo and tempo-viewer joined by GitHub slug. ChatGPT links are unchanged (380 conversations, 14 with lineages).

### 14e. Skipped and caveats

- Not walked for births: `work`, ComfyUI, SteamLibrary, pip-cache, .pnpm-store, Comfy-Desktop, Program Files, Recovery, $RECYCLE.BIN, System Volume Information, msdownld.tmp, Audacity, ISO, `World of Warcraft/_retail_` (game client), models; `*.pcm` files excluded in `fs_find.py`.
- No git repositories were found below maxdepth 5 or inside `World of Warcraft/_retail_`; `Comfy-Desktop`, `ComfyUI` and `SteamLibrary` were not searched for repositories.
- Toolkit changes made for this task: `git_repo.py` reads a submodule (`.git` file with a relative `gitdir` into a parent `.git/modules`) as a full repository; `fs_births.py` keys E: root loose files as `dir:<host>:.`; `fs_find.py` excludes `*.pcm`; `relations.py` and `chatgpt_links.py` write through a temporary file and `os.replace`; `make_worklist.py` takes optional id prefixes so a run writes only the named items. `pyyaml` is now installed in `.venv` (`uv pip install --python .venv/bin/python pyyaml`), so `relations.py` runs under the venv. Merge outputs were written to `corpus/.merge-tmp` and moved into `corpus/merged` with `os.replace` file by file.
