# CORPUS-REPORT.md: the Known World corpus run

Work item w-26069fe96149, collection day 2026-10-09. Written by the Merge manager (Sonnet 5.5) from
`corpus/merged/stats.json`, `repos.json` and the raw manifests by `collect/knownworld/report.py`; counts and verdicts
only, no corpus line is quoted. Merge is `collect/knownworld/merge.py` (deterministic, stdlib only: two runs give
byte-identical output).

## 1. Totals

| Measure | Value |
|---|---|
| Raw events collected (26 items) | 215,526 |
| Merged events (`corpus/merged/events.ndjson`) | 210,647 |
| Span, first to last event | 2011-08-25T19:45:52Z to 2026-10-09T12:45:04Z |
| Git lineages (repository components) | 121 |
| Local repository records walked (all hosts, mirrors included) | 170 |
| Non-git directory lineages (file births) | 78 |
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
| 1d AM4 non-git dirs (am4-dual-nvidia-poc, vllm-e3) | absent | - | 0 | no births collector over ssh in v1; not in the work-list |
| 1e FX99 git repositories (4) | covered | fx99-git | 110 | continuity, fleet, fleet.git (bare), ledger |
| 1e FX99 non-git dirs (dmos, menu, liferaft, ai-bench, apps, cookbook) | absent | - | 0 | no births collector over ssh in v1; not in the work-list |
| 1f GitHub: 50 public repos (djcdevelopment) + steppe-integrations | partial | github-list, mirror-0, mirror-1 | 115 | public view only (gh not authenticated): 54 repo_born events, 12 repos mirrored; 2 forks skipped; private repos pending auth (section 8) |
| 2 C:\work non-git dirs (omen-perception, _retired, orchestration, tools, ...) | covered | c-births | 607 | 38 sources; skip list honoured (dotnet9, jdk17, godot, fieldlab-postgres-data, model, venvs) |
| 2 C: root dirs (hearth-var, dirty-diffs, omen-perception-authored, tuning, assessment, AM4-provision, OMEN_prep) | partial | c-births | (in c-births) | file births only. Bulk-copied dirs are flagged `bulk_copy` (173 records) but their in-record timestamps (cycle.log lines, dirty-diffs content) were not read; hearth-var/execution/events.ndjson (573 events) is not in any item |
| 2 E:\work non-git dirs (comfy, vllm-xpu-win, start, battlemage, 8350, dump, ...) | covered | e-births | 662 | 49 sources plus loose files; models skipped |
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
| file_birth | 1,269 |
| branch | 790 |
| run | 235 |
| receipt | 233 |
| worktree | 204 |
| repo_born | 167 |

### Per host

| Host | Events |
|---|---|
| omen-c | 93,219 |
| omen-e | 61,374 |
| omen-linux | 44,600 |
| cloud | 11,259 |
| am4 | 89 |
| github | 54 |
| fx99 | 52 |

### Per actor class

| Actor class | Events |
|---|---|
| claude | 95,723 |
| codex | 71,842 |
| third_party | 22,670 |
| chatgpt | 11,259 |
| human | 7,290 |
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
| fs_births/file_birth | 1,269 | 1,269 |
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
| 2015-08 | 5 | 2 | 0 | 0 | 0 | 3 |
| 2017-12 | 4 | 1 | 0 | 0 | 0 | 3 |
| 2018-08 | 12 | 11 | 0 | 0 | 0 | 1 |
| 2019-05 | 1 | 1 | 0 | 0 | 0 | 0 |
| 2019-07 | 2 | 2 | 0 | 0 | 0 | 0 |
| 2019-10 | 2 | 2 | 0 | 0 | 0 | 0 |
| 2019-11 | 2 | 2 | 0 | 0 | 0 | 0 |
| 2020-05 | 2 | 2 | 0 | 0 | 0 | 0 |
| 2020-11 | 16 | 15 | 0 | 0 | 0 | 1 |
| 2020-12 | 2 | 0 | 0 | 0 | 0 | 2 |
| 2021-05 | 19 | 18 | 0 | 0 | 0 | 1 |
| 2021-06 | 21 | 20 | 0 | 0 | 0 | 1 |
| 2021-07 | 20 | 20 | 0 | 0 | 0 | 0 |
| 2021-08 | 35 | 35 | 0 | 0 | 0 | 0 |
| 2021-09 | 30 | 30 | 0 | 0 | 0 | 0 |
| 2021-10 | 20 | 20 | 0 | 0 | 0 | 0 |
| 2021-11 | 12 | 12 | 0 | 0 | 0 | 0 |
| 2021-12 | 13 | 13 | 0 | 0 | 0 | 0 |
| 2022-01 | 23 | 23 | 0 | 0 | 0 | 0 |
| 2022-02 | 14 | 14 | 0 | 0 | 0 | 0 |
| 2022-03 | 8 | 8 | 0 | 0 | 0 | 0 |
| 2022-04 | 4 | 4 | 0 | 0 | 0 | 0 |
| 2022-05 | 39 | 39 | 0 | 0 | 0 | 0 |
| 2022-06 | 37 | 37 | 0 | 0 | 0 | 0 |
| 2022-07 | 48 | 48 | 0 | 0 | 0 | 0 |
| 2022-08 | 23 | 23 | 0 | 0 | 0 | 0 |
| 2022-09 | 12 | 12 | 0 | 0 | 0 | 0 |
| 2022-10 | 38 | 38 | 0 | 0 | 0 | 0 |
| 2022-11 | 18 | 18 | 0 | 0 | 0 | 0 |
| 2022-12 | 49 | 49 | 0 | 0 | 0 | 0 |
| 2023-01 | 29 | 29 | 0 | 0 | 0 | 0 |
| 2023-02 | 20 | 20 | 0 | 0 | 0 | 0 |
| 2023-03 | 309 | 308 | 0 | 0 | 0 | 1 |
| 2023-04 | 212 | 204 | 6 | 2 | 0 | 0 |
| 2023-05 | 266 | 265 | 0 | 0 | 0 | 1 |
| 2023-06 | 264 | 264 | 0 | 0 | 0 | 0 |
| 2023-07 | 248 | 248 | 0 | 0 | 0 | 0 |
| 2023-08 | 269 | 269 | 0 | 0 | 0 | 0 |
| 2023-09 | 357 | 357 | 0 | 0 | 0 | 0 |
| 2023-10 | 345 | 335 | 6 | 3 | 0 | 1 |
| 2023-11 | 358 | 351 | 2 | 1 | 0 | 4 |
| 2023-12 | 340 | 339 | 0 | 0 | 0 | 1 |
| 2024-01 | 533 | 532 | 0 | 0 | 0 | 1 |
| 2024-02 | 462 | 461 | 0 | 0 | 0 | 1 |
| 2024-03 | 438 | 438 | 0 | 0 | 0 | 0 |
| 2024-04 | 525 | 522 | 0 | 0 | 0 | 3 |
| 2024-05 | 513 | 508 | 0 | 0 | 0 | 5 |
| 2024-06 | 416 | 415 | 0 | 0 | 0 | 1 |
| 2024-07 | 477 | 472 | 0 | 0 | 0 | 5 |
| 2024-08 | 398 | 389 | 0 | 0 | 0 | 9 |
| 2024-09 | 353 | 348 | 0 | 0 | 0 | 5 |
| 2024-10 | 425 | 417 | 0 | 0 | 0 | 8 |
| 2024-11 | 560 | 549 | 6 | 1 | 0 | 4 |
| 2024-12 | 413 | 371 | 34 | 5 | 0 | 3 |
| 2025-01 | 586 | 467 | 98 | 12 | 0 | 9 |
| 2025-02 | 432 | 411 | 10 | 3 | 0 | 8 |
| 2025-03 | 546 | 502 | 20 | 5 | 0 | 19 |
| 2025-04 | 419 | 394 | 17 | 3 | 0 | 5 |
| 2025-05 | 689 | 600 | 63 | 6 | 0 | 20 |
| 2025-06 | 586 | 531 | 33 | 4 | 0 | 18 |
| 2025-07 | 1,023 | 803 | 145 | 29 | 0 | 46 |
| 2025-08 | 940 | 788 | 100 | 16 | 0 | 36 |
| 2025-09 | 796 | 651 | 91 | 22 | 0 | 32 |
| 2025-10 | 781 | 666 | 73 | 17 | 0 | 25 |
| 2025-11 | 1,660 | 804 | 784 | 43 | 0 | 29 |
| 2025-12 | 3,374 | 763 | 2,535 | 51 | 0 | 25 |
| 2026-01 | 3,809 | 578 | 3,137 | 67 | 0 | 27 |
| 2026-02 | 3,208 | 684 | 2,420 | 65 | 0 | 39 |
| 2026-03 | 4,190 | 2,616 | 1,299 | 25 | 0 | 250 |
| 2026-04 | 1,104 | 928 | 0 | 0 | 0 | 176 |
| 2026-05 | 10,165 | 1,193 | 8,597 | 185 | 0 | 190 |
| 2026-06 | 10,354 | 1,139 | 8,838 | 222 | 0 | 155 |
| 2026-07 | 24,488 | 2,827 | 19,641 | 380 | 1,264 | 376 |
| 2026-08 | 56,454 | 2,583 | 52,833 | 580 | 108 | 350 |
| 2026-09 | 38,651 | 2,401 | 33,031 | 557 | 1,873 | 789 |
| 2026-10 | 37,330 | 862 | 12,613 | 506 | 23,141 | 208 |

## 5. Dropped counters

| Item | null_ts | polling | decode_errors | other_role | null_ts_emitted | deduped in item | Warnings |
|---|---|---|---|---|---|---|---|
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
| fx99-git | 0 | 0 | 0 | 0 | 0 | 0 | roots_missing:6 |
| github-list | 0 | 0 | 0 | 0 | 0 | 0 | pending auth: private repos not listed |
| hearth-ledger | 0 | 535,587 | 0 | 0 | 0 | 1,293 | - |
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
| Events loaded | 215,526 |
| Events written | 210,647 |

Check: loaded 215,526 - duplicates 4,169 - null-ts 710 = written 210,647.

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
- AM4 and FX99 non-git directories have no collector.
- GitHub private repositories and fork metadata are pending authentication (section 8).

Reproduce: `.venv/bin/python -I collect/knownworld/merge.py && .venv/bin/python -I collect/knownworld/report.py &&
.venv/bin/python -I collect/knownworld/privacy_scan.py corpus/merged` from `~/work/known-world` with
`PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 GIT_TERMINAL_PROMPT=0`.

