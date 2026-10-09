# SURVEY.md: what exists, where, and how big (read-only surveys, 2026-10-09)

Three survey agents (Windows mounts; Linux; GitHub + AM4) plus direct probes (FX99, credentials, encoders). Nothing
here is content: counts, spans, paths and schema keys only. The Scope agent turns this into the work-list.

## 0. Hosts and surfaces

| Host id | What | Access |
|---|---|---|
| `omen-c` | Windows C: of the OMEN box, BitLocker via dislocker FUSE + ntfs3, **read-only** | `/mnt/omen-c-read` |
| `omen-e` | Windows E: (was D: before 2026-07; Claude project dirs say `D--`) | `/mnt/omen-e-read` |
| `omen-linux` | this host | local |
| `am4` | AM4 box | `ssh 10.44.0.2` (key auth, no prompt) |
| `fx99` | FX99 box, hostname `ai-1` | `ssh 100.122.130.124` (tailnet name `fx99`; key auth, no prompt) |
| `github` | github.com/djcdevelopment (User, created 2011-08-25) | `gh api` once authenticated; https clones already work via the stored git credential (never read it) |

Birth time (`stat %w`) is populated on both ntfs3 mounts with ns precision. Bulk-copied dirs on C: (`hearth-var`,
`dirty-diffs`, `assessment`, `tuning`, `omen-perception-authored`) share one birth stamp 2026-08-19 09:33: use in-record
timestamps there. E: ctime is a mass attribute change (2026-03-17); ignore ctime and atime. `1980-01-01` = zip
extraction = null. A `find` over one `work/*` dir on a mount can take tens of seconds; keep timeouts; the FUSE layer
stalls under fan-out (max 3 concurrent per mount).

## 1. Git repositories

Author identities that are Derek: `derek`, `dciula`, `Derek Ciula`, `DjcDevelopment`. AI work is in
`Co-Authored-By` trailers (Claude Opus 5 / 5.5 / 4.8, Fable 5 / 5.1, Sonnet 5 / 5.5 / 4.6, Codex, cc-builder-1/2) and
as direct authors (`Codex`, `cc-builder-*`, `am4-worker-1`, `omen-worker-1`, `Claude Sonnet 5.5`, `Claude` in ashley).

### 1a. C:\work (`/mnt/omen-c-read/work`), top-level repos (36)

| Dir | Remote | First → last | Commits | Refs |
|---|---|---|---|---|
| 404 | djcdevelopment/404-isolate (private) | 2026-09-17 → 09-23 | 43 | 2 |
| archify | tt-a1i/archify (third-party) | 2026-08-30 | 1 | 1 |
| articleblitz | djcdevelopment/articleblitz | 2026-07-11 | 7 | 4 |
| assessment | none | 2026-08-18 → 08-19 | 6 | 1 |
| baseline | djcdevelopment/baseline | 2026-03-24 → 09-23 | 1358 | 34 |
| ComfyMods | redseiko/ComfyMods (third-party) | 2021-05 → 2026-09 | 1128 | 87 |
| comfy-quest | djcdevelopment/comfy-quest | 2026-07-01 → 09-15 | 266 | 6 |
| ComfyStewardView | djcdevelopment/ComfyStewardView | 2026-03-19 → 09-15 | 303 | 5 |
| commandcenter | djcdevelopment/commandcenter | 2026-07-02 → 09-23 | 927 | 257 |
| contextlandscape | djcdevelopment/contextlandscape | 2026-07-29 → 09-23 | 73 | 15 |
| deepagents-poc | none | 2026-09-17 | 1 | 1 |
| deepagents-shot-director | none | 2026-09-12 | 3 | 2 |
| deepnorthtesting | djcdevelopment/deepnorthtesting | 2026-09-12 → 10-08 | 46 | 3 |
| djcdevelopment | djcdevelopment/djcdevelopment | 2026-08-28 | 1 | 2 |
| irc | djcdevelopment/irc | 2026-07-30 → 09-23 | 47 | 18 |
| ismodded | djcdevelopment/ismodded | 2026-09-12 → 10-08 | 10 | 3 |
| isolate | djcdevelopment/isolate (private) | 2026-08-07 → 09-16 | 20 | 4 |
| lumberjacks-platform | djcdevelopment/lumberjacks-platform | 2026-07-04 → 09-23 | 728 | 4 |
| memsplice | djcdevelopment/memsplice | 2026-09-21 | 24 | 5 |
| networksense | djcdevelopment/networksense | 2026-07-03 → 09-14 | 260 | 4 |
| nightshift | none | 2026-09-12 → 09-13 | 48 | 1 |
| notebook | djcdevelopment/open-notebook-hearth-integration (private) | 2026-07-20 → 09-23 | 13 | 6 |
| sealcompanion | none | 2026-09-16 | 1 | 1 |
| SelfieStick | djcdevelopment/SelfieStick | 2026-09-15 → 10-08 | 11 | 3 |
| sovereign-shards | djcdevelopment/sovereign-shards | 2026-08-11 → 09-08 | 8 | 3 |
| steppeintegrations-site | djcdevelopment/steppeintegrations-site (private) | 2026-04-09 → 09-23 | 88 | 6 |
| steward-spatial-lab | none | 2026-08-23 → 09-03 | 17 | 1 |
| totemalert | djcdevelopment/TotemSentinel | 2026-08-12 → 10-08 | 16 | 4 |
| tuning | none | 2026-07-03 | 1 | 1 |
| Unfaded | djcdevelopment/Unfaded | 2026-09-13 → 10-08 | 15 | 5 |
| valheim-profile-engine | djcdevelopment/valheim-profile-engine | 2026-09-16 → 10-08 | 14 | 3 |
| vulkancliff | djcdevelopment/vulkancliff | 2026-08-23 → 08-24 | 4 | 2 |
| windtunnel | djcdevelopment/windtunnel | 2026-07-10 → 09-03 | 10 | 3 |

C: worktrees (`.git` is a file pointing at `C:/work/<parent>/.git/worktrees/<name>`, unreadable from Linux; read
history from the parent): commandcenter-d1-guard-9f306fb, commandcenter-flash-foreman, commandcenter-hermes-fx99,
commandcenter-jev-scheduler, commandcenter-local-work, hearth-execution-control-plane (commandcenter);
gallery-stage-baseline-20260915 (baseline); gallery-stage-quest-20260915 (comfy-quest);
gallery-stage-steward-20260915 (ComfyStewardView); irc-hearth-adapter (irc). `conductor-mirror.git` is bare.

C: nested repos: am4-harvest/{ember 36, gad 53, manifest 32}; Diana/oddlittlebird 2 (steppe-integrations),
Diana/showcase-site 292 (third-party); _extract/comfy-quest-incomplete 111; _extract/comfy-quest-identity-wrong-tested 0;
_retired/comfy 237 (djcdevelopment/comfy); _retired/Lumberjacks 215 (djcdevelopment/Lumberjacks);
orchestration/local-operator-workspace-20260917 38; orchestration/truth-alignment-20260908 3;
research/cnc-generals 1 (third-party); deepagents-poc/target, overview/episodes 0.

### 1b. E:\work (`/mnt/omen-e-read/work`), top-level repos (38)

| Dir | Remote | First → last | Commits | Refs |
|---|---|---|---|---|
| ai-dev-system | djcdevelopment/ai-dev-system (private) | 2026-03-06 → 04-08 | 5 | 5 |
| ai-systems-research | djcdevelopment/ai-systems-research | 2026-03-07 → 09-23 | 22 | 7 |
| azure-event-grid-viewer | Azure-Samples fork (third-party + dciula) | 2018 → 2025-07 | 47 | 19 |
| b70tools | djcdevelopment/b70tools | 2026-05-28 → 09-02 | 11 | 4 |
| bring-your-own-ollama | steppe-integrations/bring-your-own-ollama | 2026-05-09 | 11 | 3 |
| campfire | djcdevelopment/campfire (private) | 2026-05-13 → 05-17 | 40 | 5 |
| chatGPT_parser | djcdevelopment/chatGPT_parse (private) | 2026-03-12 → 09-23 | 12 | 3 |
| denning | djcdevelopment/denning | 2026-06-19 → 06-22 | 61 | 5 |
| discoverlay | djcdevelopment/discoverlay (private) | 2026-05-31 → 06-09 | 8 | 3 |
| ember | djcdevelopment/ember | 2026-05-15 → 09-22 | 37 | 3 |
| event-viewer | Azure-Samples (third-party) | 2018 → 2025-07 | 46 | 19 |
| gad | djcdevelopment/gad (private) | 2026-05-17 → 09-23 | 56 | 2 |
| gad-bot | djcdevelopment/gad-bot (private) | 2026-05-15 → 06-22 | 2 | 2 |
| game | djcdevelopment/Lumberjacks | 2026-03-24 → 05-07 | 57 | 2 |
| GasperCards | steppe-integrations/threat-trace | 2026-04-29 | 2 | 4 |
| Guild | djcdevelopment/goatsafterdark (private) | 2026-04-25 → 05-15 | 136 | 23 |
| hearth | djcdevelopment/hearth (private) | 2026-05-15 → 05-16 | 8 | 5 |
| img | djcdevelopment/tempo-imagegen (private) | 2026-05-17 → 09-03 | 10 | 2 |
| lantern | djcdevelopment/Lantern | 2026-05-17 → 05-22 | 5 | 2 |
| leopard | djcdevelopment/leopard | 2026-06-03 → 06-16 | 54 | 5 |
| liveView | djcdevelopment/liveView (private) | 2026-03-06 → 04-11 | 10 | 4 |
| llamacpp-knee | ggml-org/llama.cpp (third-party) | 2026-08-20 → 09-18 | 517 | 27 |
| llamacpp-qwen38 | unslothai/llama.cpp (third-party) | 2023-03 → 2026-08 | 11272 | 228 |
| llama.cpp-src | ggml-org/llama.cpp (third-party) | 2026-06-20 | 1 | 4 |
| manifest | djcdevelopment/manifest (private) | 2026-05-28 → 09-23 | 36 | 2 |
| planning | djcdevelopment/planning | 2026-04-06 → 09-23 | 82 | 10 |
| RaidUI | djcdevelopment/RaidUI | 2026-04-21 → 05-16 | 344 | 85 |
| reader | djcdevelopment/indexcard | 2026-06-08 → 06-17 | 9 | 3 |
| resonantOS | ResonantOS/2.0.0-alpha (third-party) | 2026-05-26 → 09-25 | 1073 | 77 |
| stars-app | djcdevelopment/stars-app (private) | **2026-01-17** → 01-26 | 27 | 10 |
| temp | djcdevelopment/ComfyStewardView | 2026-03-19 → 05-26 | 11 | 2 |
| vllama | djcdevelopment/vllama (private) | 2026-06-04 → 06-17 | 6 | 3 |
| workbench | djcdevelopment/workbench (private) | 2026-06-03 → 06-05 | 4 | 2 |
| work-visuals | djcdevelopment/work-visuals (private) | 2026-04-08 | 2 | 2 |
| writing | djcdevelopment/desire-trace (private) | 2026-04-09 → 06-16 | 35 | 14 |
| www | djcdevelopment/steppeintegrations-site (private) | 2026-04-09 → 06-17 | 27 | 7 |
| xpu-train | djcdevelopment/xpu-train (private) | 2026-06-22 | 1 | 2 |

"(private)" above = not in the public API list of 50; confirm with `gh repo list` once authenticated.

E: nested repos: liveView/ingest 6, liveView/ui 13; start/planner **1660** (2026-03-17 → 04-08, likely automated),
start/precheck 42, start/precheckv2 1, start/contextforge 5, start/farmer 29, start/ashley 20 (has a `Claude` author),
start/portmap 3, start/scarecrow 6, start/langfuse 8359 (third-party); comfy/seer 1; battlemage/tempo-workbench 1;
repos/multi-agent-build-blueprint 2 (steppe-integrations); vllm-xpu-win/kernels 514 (third-party),
vllm-xpu-win/vllm-src 6 (third-party). `llamacpp-knee-pr` is a worktree with an unresolvable `E:/` gitdir.

Known duplicate lineages (same root commit): game = _retired/Lumberjacks = baseline (root 2026-03-24T06:10:06) and
lumberjacks-platform overlaps; www = steppeintegrations-site; temp = ComfyStewardView; am4-harvest/* = E: ember, gad,
manifest; memsplice on C:, E:? and Linux and GitHub.

### 1c. Linux (`omen-linux`)

| Repo | Remote | First → last | Commits | Refs |
|---|---|---|---|---|
| ~/work/commandcenter-linux-flash | djcdevelopment/commandcenter | 2026-07-02 → 10-07 | 1319 | 138 |
| ~/private-migration-20260923/commandcenter | same | 2026-07-02 → 09-23 | 927 | 257 |
| ~/git/commandcenter-flash-base | the migration copy | 2026-07-02 → 09-23 | 807 | 73 |
| ~/.continuity/ledger | none (bookkeeping commits by `ct`) | 2026-09-27 → 10-02 | 518 | 1 |
| ~/work/lab-rnd | none | 2026-09-30 → 10-05 | 143 | 18 |
| ~/work/continuity | ssh://192.168.12.220/…/continuity.git | 2026-09-27 → 10-02 | 80 | 14 |
| ~/work/jepa-add-protocol | none | 2026-10-07 → 10-08 | 52 | 1 |
| ~/work/game-jepa | none | 2026-10-07 → 10-08 | 33 | 1 |
| ~/work/discengine | none | 2026-10-08 → 10-09 | 32 | 1 |
| ~/work/lab | none | 2026-10-02 → 10-04 | 30 | 2 |
| ~/work/trial/notebook (+ -cold, -cold2, and worktrees -devstral, -gemma, -32b, -27b) | continuity-host notebook.git | 2026-07-20 → 09-27 | 26 | 15 |
| ~/work/memsplice | djcdevelopment/memsplice | 2026-09-17 → 09-27 | 25 | 6 |
| ~/work/resume-linux.git (bare) | none | 2026-09-03 → 10-07 | 24 | 2 |
| ~/work/lever-ledger | none | 2026-10-01 → 10-05 | 22 | 3 |
| ~/work/deepagents-linux | none | 2026-09-17 → 10-03 | 18 | 6 |
| ~/work/liveView-ui-run | djcdevelopment/liveview-ui (private) | 2026-03-06 → 04-08 | 13 | 8 |
| ~/work/founderOS | none | 2026-10-09 | 5 | 1 |
| ~/work/clm-pilot (+ upstream, third-party) | none / facebookresearch | 2026-10-02 | 3 | 2 |
| ~/continuity-triage/entire-probe | none | 2026-09-27 | 4 | 2 |
| ~/private-migration-20260923/{deepagents-shot-director 3, deepagents-poc 1} | none | 2026-09 | | |
| ~/work/amux, ~/work/commandcenter-linux-private | none | 2026-10 | 1 each | |

Zero-commit repos (skip, never write): ~/work/hybrid-context-trial, jepa-evidence-units-20260925 (+utility-smoke),
jepa-confirmation-20260924, jepa-project-holdout-20260925 (+utility-smoke), jepa-recorded-actions-20260925,
jepa-same-role-actions-20260925, jepa-operation-representations-20260925, ~/git-local-probe.

`~/work/worktrees` (94): commandcenter-linux-flash 57, lab-rnd 16, continuity 11, deepagents-linux 4, lever-ledger 2,
resume-linux.git 2, plus two plain dirs. Worktree branches share the parent's object store: read from the parent with
`--all`. `~/work/commandcenter-public` is an unpacked tarball snapshot (not a repo).

### 1d. AM4 (`ssh 10.44.0.2`, hostname am4)

Repos: ~/quest-build-20260915, ~/bench, ~/o1/level-zero-tests, ~/o1/libpng, ~/continuity, ~/chatgpt_parser_run,
~/am4bot, ~/ComfyUI (third-party), ~/sovereign-shards, ~/.continuity/ledger, ~/baseline/llama.cpp (third-party).
Non-git: ~/work/am4-dual-nvidia-poc, ~/work/vllm-e3-20260923. No Claude Code or Codex transcripts.

### 1e. FX99 (`ssh 100.122.130.124`, hostname ai-1)

Repos: ~/fleet (+ ~/fleet.git bare), ~/continuity, ~/.continuity/ledger. Non-git dirs of interest: ~/dmos, ~/menu,
~/liferaft, ~/ai-bench, ~/apps, ~/cookbook. No ~/work. No Claude Code or Codex transcripts.

### 1f. GitHub (`djcdevelopment`, public view; private repos pending `gh` auth)

50 public repos: 1 fork from 2011 (personal_website), POEscripter and PoE-Item-Filter-Creator (2015),
klaviyoDataformatter (2017), Comfy-ExaltedContracts and ComfyMerchant (2023-10/11), then ~44 from 2026-03-08 on
(ai-systems-research first; ComfyStewardView, plinko, waypoints, ContextForge, Lumberjacks, portmap, farm, planning,
RaidUI, threat-trace, ember, Lantern, battlemage, chest-seer, b70tools, leopard, indexcard, llmquest, denning, comfy,
commandcenter, windtunnel, articleblitz, open-notebook (fork), baseline, contextlandscape, irc, networksense,
lumberjacks-platform, comfy-quest, sovereign-shards, TotemSentinel, vulkancliff, llama.cpp (fork), clippy,
djcdevelopment, deepnorthtesting, ComfyMods (fork), ismodded, Unfaded, SelfieStick, valheim-profile-engine, memsplice).
Forks: personal_website, open-notebook, llama.cpp, ComfyMods. Zero-size: POEscripter, Comfy-ExaltedContracts, plinko,
waypoints, farm, threat-trace, battlemage. `created_at` is the GitHub creation date, often later than local history.
Unauthenticated budget 60/h; authenticated 5000/h.

## 2. Non-git directories (file births)

C:\work: omen-perception 50,762 files (2026-06 → 10), _retired 42,987, orchestration 33,659 (2026-09), tools 18,722
(2026-06 → 07), worktrees 10,776, research 6,076, valheim-capture 4,728, comfy-quest-test-artifacts-20260812 1,906,
github-runner-deepnorthtesting 939, _extract 635, am4-harvest 615, JEPA 357, Diana 287, am4 191, writing 109,
creator-dm-restart-20260906 88, _archive 75, kart 74, iso 46; small: handoffs, overview, m11-transport-*-bundle,
conductor-mirror.git, valheim-terrain, am4-game-art-deploy, imagegen, benchmark, buzz, where-to-point-it. Skip:
dotnet9, jdk17, godot-4.6.1, fieldlab-postgres-data, model, venvs.

E:\work: comfy 29,366 (2023-09 → 2026-05), vllm-xpu-win 20,402, start 14,769, battlemage 7,210, 8350 4,690, dump 2,481
(the ChatGPT export, 2026-03-12), Antigravity 1,441, mfa 166 (2021 → 2024-08), claude-fleet-control 122, ConsoleApp1 83,
hermes 64, drawing 52 (2024-12 → 2025-02), ISO 39, planning-runtime 38, archStandards 18; many small dirs 2026-03 → 06.
Loose files back to 2024-12-12. Skip: models.

C: root: hearth-var (HEARTH runtime state; `ledger/events.ndjson` 90,784 events 2026-07-04 → 08-19;
`execution/events.ndjson` 573 events; contains `*.secret` and `callers.json`: exclude), dirty-diffs (one 2026-08-19
snapshot of 8 repos' patches), omen-perception-authored (`cycle.log` timestamps from 2026-06-28), tuning (git, 1 commit),
assessment (git, 6 commits; run-dated transcripts: counts only), AM4-provision (2026-08-22 staging), OMEN_prep (1 xlsx).

## 3. Chat and chatter sources

| Source | Path | Span | Size | Schema notes |
|---|---|---|---|---|
| ChatGPT export, normalized | `/mnt/omen-e-read/work/chatGPT_parser/data/normalized/{messages,conversations,source_files}.ndjson` (raw export in `/mnt/omen-e-read/work/dump`) | 2023-04-17 → 2026-03-12 | 380 conversations, 19,045 messages (37 MB) | conversation: `conversation_id title create_time update_time message_count user_message_count assistant_message_count has_branches model_slug is_archived voice`; message: `message_id conversation_id parent_message_id role author_name content_type text create_time …`. Projections `data/projections/{timeline,activity_calendar}.ndjson` are already aggregated. Read `docs/RETROSPECTIVE_2026-09-23.md` first. |
| Claude Code, Windows, archived | `/mnt/omen-e-read/work/claude-20260623T084942Z-3-001.zip` (212 MB) | transcripts 2026-05-09 → 06-22 | 413 jsonl under `.claude/projects/` (50 project dirs, 410 MB uncompressed) | A zipped `~/.claude` (also `file-history`, `tasks`, `plans`, `history.jsonl`, and `.credentials.json`: never extract; `unzip -p` allowlisted members only). Project dirs use `D--…`. |
| Claude Code, Windows, live | `/mnt/omen-c-read/Users/derek/.claude/projects` | 2026-07-10 → 2026-10-08 | 55 project dirs, 1,042 jsonl, 1.2 GB | line `type` ∈ user/assistant/attachment/queue-operation/last-prompt/custom-title; keys `parentUuid isSidechain promptId type message{role,content} uuid timestamp permissionMode origin promptSource userType entrypoint cwd sessionId version gitBranch`; assistant adds `message.model message.usage requestId effort`. Also `history.jsonl` 454 lines (`display pastedContents timestamp project sessionId`). |
| Codex, Windows | `/mnt/omen-c-read/Users/derek/.codex/sessions` | 2026-06-29 → 2026-10-06 | 432 jsonl, **10.6 GB** | line keys `timestamp type payload`; first line payload `session_id id timestamp cwd originator cli_version source thread_source model_provider base_instructions`. Stream; metadata only. `auth.json` alongside: exclude. |
| Claude Code, Linux | `~/.claude/projects` | 2026-09-27 → now | 12 project dirs, 481 jsonl (341 are `<session>/subagents/*.jsonl`), 411 MB | same shape; line 0 is `queue-operation`; types also `cost-state`, `atis-latch`; `isSidechain` marks subagents; `~/.claude/history.jsonl` 213 lines. |
| Codex, Linux | `~/.codex/sessions` | 2026-09-27 → now | 50 jsonl, 296 MB | keys `timestamp ordinal type payload`; types `session_meta event_msg response_item turn_context world_state token_usage_record`; `session_index.jsonl` (`id thread_name updated_at`); `history.jsonl` 209 lines. `auth.json`: exclude. |
| OpenCode | `~/.local/share/opencode/opencode.db` | recent | 24 sessions, 953 messages, 2,203 parts, 7,716 events (22 MB) | sqlite; open `mode=ro&immutable=1`; explicit columns only. |
| HEARTH ledger, Linux | `~/hearth-production/var/ledger/events.ndjson` (375 MB, 472,077 lines) + `index.sqlite` (table `events`: `event_id ts caller_id runner_class tool ok duration_ms offset length task_class model backend routed_by …`) | 2026-07-04 → now, 92 days | runner_class: local 246,602 / frontier 144,222 / human 81,250; tools mostly polling (`kernel_status` 75k, `get_execution` 58k, `local_generate` 24k) | record keys `schema event_id ts caller{id,runner_class,node} tool args_digest args_preview result_digest ok error duration_ms cost{tokens_in,tokens_out,watt_s} task_id` + newer `task_class model backend routed_by occupancy error_code outcome profile`. `args_preview` may hold prompt text: never emit. `callers.json*` nearby: exclude. |
| HEARTH ledger, Windows copy | `/mnt/omen-c-read/hearth-var/ledger/events.ndjson` | 2026-07-04 → 08-19 | 90,784 events | same schema; dedupe on `event_id` against the Linux copy. |
| Continuity (`ct`) | `~/.continuity/ledger/events/*.json` (327 events; keys `id recorded_at recorded_by runner schema type body`), `receipts/`, `transcripts/` (imported claude-code and opencode copies, 4.5 MB) | 2026-09-27 → 10-02 | types: receipt.recorded 229, link.asserted 30, work_item.opened 20, launch.recorded 17, session.observed 17, commit.observed 6, … | `ct stats`, `ct recall`. AM4 and FX99 have their own `~/.continuity/ledger`. |
| deepagents runs | `~/work/deepagents-linux/runs/` (133 run dirs, 2,986 files, 50 MB), `~/hearth-production/runs/` (227 MB; `artifacts/<date>/obs-offload-*.json` per-call observations from 2026-07-30) | 2026-09-07 → 10-03; 2026-07-30 → | | run dirs `authored-<date>-<slug>-<ts>`. |
| assessment transcripts | `/mnt/omen-c-read/assessment/transcripts/run-2026-08-18, run-2026-08-19-s1-1, -s1-1b` | 2026-08-18/19 | 3 runs | counts only. |
| Downloads session exports | `/mnt/omen-c-read/Users/derek/Downloads/session-export-<epoch>.zip` ×6 (2026-07-09, 07-10, 07-15, 08-27 ×3; 1–22 MB) | | | unopened; list names/dates only unless Scope decides they add span. |

Chat coverage is continuous 2023-04 → today: ChatGPT (2023-04 → 2026-03), Claude zip (2026-05 → 06), Windows live
Claude + Codex (2026-06-29 → 10-08), Linux Claude + Codex + OpenCode (2026-09-27 → now).

## 4. Existing assets and tooling on omen-linux

- `~/work/fleet-topography-interactive.html`: 963 lines, self-contained, raw Canvas 2D, the lab's dark palette
  (`--bg-base #07090e`, cyan/crimson/emerald/amber/purple, JetBrains Mono). The renderer should feel like it.
- `~/work/liveView-ui-run`: Vite + React 18 + TS + recharts "Projection Workbench" over chatGPT_parser projections.
- Python 3.14.4 + `uv` 0.12.17; project venv `.venv` has numpy 2.5.3 and imageio-ffmpeg (static ffmpeg 7.0.2 with
  libx264 and aac). Node 24.21; Playwright 1.64 + Chromium under `~/work/founderOS/node_modules`
  (`~/.cache/ms-playwright/chromium-1248`). Firefox present. No gource, ImageMagick, sox, d3, three, pixi anywhere.
  Display: Wayland session on seat0; headless jobs must not assume `DISPLAY`. GPUs: two Intel B70 held by vLLM;
  render on CPU.
- `gh` 2.102.0 at `~/.local/bin/gh` (installed 2026-10-09; **not yet authenticated**). `credential.helper store`
  already serves https clones of private repos (verified with `git ls-remote` on 404-isolate; credential never read).

## 5. Secrets near the data (exclude by path, never open)

`~/.claude/.credentials.json` (and inside the E: zip), `~/.codex/auth.json` (both hosts),
`~/hearth-production/var/callers.json*`, `bf6-dispatcher.key`, `/mnt/omen-c-read/hearth-var/*.secret`,
`caddy-funnel-secret.caddy`, `/mnt/omen-e-read/work/dev2.pfx`, `.env*` in repos, `~/.git-credentials`.

## 4b. RaidUI: Derek's prior animation-over-time player (surveyed 2026-10-09)

`E:\work\RaidUI` (`/mnt/omen-e-read/work/RaidUI`, 333 commits 2026-04-21 → 05-16, Node ≥20 ESM, DuckDB; three UI
generations: `src/viewer`+`src/shell` v1 "raid replay" (React 18 UMD, globals), `app/` analysis app, `NewUI/app`
Vite 8 + React 19 + TS 6; on disk the directory is `NewUI/`, git tracks `newui/`). Contract-first: JSON Schemas in
`contracts/session/` (session, encounter, pull, entity, event, frame); the replay file is dense fixed-step frames
(`frameStepMs`, flat normalized positions index-aligned to `entities[]`) plus a sparse `events[]`. Rule: "the contract
absorbs optionality; the surface rejects it"; unknown enum values are dropped, wrong `schemaVersion` is refused.

**The playback core (lift as-is; copies in `render/vendor/raidui/`, see PROVENANCE.md):**

| Module | Lines | What it gives Known World |
|---|---|---|
| `src/overlay/render-state.js` | 128 | `buildRenderState({data, currentTimeMs, …}, out?)`: pure (data, t) → state with preallocated `Float32Array` scratch; O(1) frame lookup `fi = floor(t / step)` with lerp alpha from real frame times; runs under Node |
| `src/compare/playback-controller.js` | 179 | shared clock `{timeMs, playing, speed, subscribe, setTime, togglePlay, setSpeed, _tick(dtMs)}`; rAF loop starts lazily and stops with the last subscriber; `_tick` is the deterministic frame-stepper for headless export |
| `src/shape/density.js` | 53 | 200×200 point-density grid (a fog or heat mask) |
| `src/shape/palette.js` | 80 | OKLCH palette by role with djb2 hue jitter ±10° per id: stable colour per entity |
| `src/overlay/registry.js` + `builtins/trails-2s.overlay.jsx` | 82 + 113 | overlay descriptors `{id, zIndex, render(ctx, state)}` composited in z order with save/restore and per-overlay try/catch; the trail overlay is the decay template (resample `frameLookup(t − k·step)`, alpha by age) |
| `useRafPlayback` (.js 142 / .ts 147), `Transport.tsx` | 166 | the single-rAF clock (`t += dt·speed`, draws every tick even when paused so scrubbing is free; React sees time only through a ~100 ms throttle, ADR-016); scrubber, play/pause, ±5 s, 0.5/1/2×, keyboard; the clock readout written with `textContent` straight from the rAF loop |

**Adapt:** drop React from the clock; add a fixed-step export mode and a speed list far beyond 2×; keep the
compositor loop (clear, base layer, overlays by zIndex) and replace the arena with fog; keep the direct-DOM readout
and replace `m:ss` with the date ticker and rate; turn the 2-second trail into day-scale decay keyed by event age;
reuse the `shape-raster.js` offscreen-layer-plus-cache-key pattern for a persistent fog mask.

**Missing (the strategists design these):** a sparse timestamped event index (sorted array with upper-bound search
or per-frame buckets; RaidUI only has dense frames), cumulative monotonic state for fog (per-frame reveal snapshots
or an incremental accumulator rebuilt on scrub), running tallies, a calendar ticker, legend, tooltips, camera
(zoom/pan), audio (no Web Audio anywhere), seeded RNG, any frame export or headless tooling, and burst handling (no
aggregation design exists; sparse events are only timeline pips).

**Ideas to keep:** stateless renderer and a separate ref-based clock; allocation-free hot path; loud schema-version
check with unknown enums dropped; interpolation in the renderer, not at parse time; alpha from real frame times so
irregular spacing is tolerated. Tests are Node's built-in runner on `*.test.cjs` (no browser tests).

## 4c. manifest: Derek's relationship graph between projects (surveyed 2026-10-09)

`E:\work\manifest` (`/mnt/omen-e-read/work/manifest`, 36 commits 2026-05-28 → 09-23, newest copy; the C:
`am4-harvest/manifest` copy is stale at 2026-06-05) is the constellation-manifest framework (Python 3.11+, pydantic 2,
PyYAML; `framework load --json <constellation.yaml>` validates and dumps; needs pydantic, which this host lacks, so a
PyYAML `safe_load` is the pragmatic read, skipping validation and defaults against ADR-011's advice). The manifest
repo holds no constellation files: the **12 live `constellation.yaml` files sit in the member repos' roots** and
`fleet.yaml` (generated 2026-09-23) only indexes them with Windows paths.

| Constellation | File | Repos | depends_on | contracts |
|---|---|---|---|---|
| GAD | `E:\work\gad` | 20 | 21 | 1 |
| ai-systems-research | `E:\work\ai-systems-research` (mtime 2026-09-26, post-commit edits) | 8 | 5 (+2 parent) | 6 |
| planning-spine | `E:\work\planning` | 10 | 3 | 3 |
| creator-os | `C:\work\baseline` | 20 | 23 | 5 |
| omen-core | `C:\work\commandcenter` | 12 | 8 | 4 |
| steppe | `C:\work\steppeintegrations-site` | 11 | 3 | 1 |
| p2p-inference, lumberjacks | `C:\work\irc`, `C:\work\lumberjacks-platform` | 2 each | 1 each | 1 each |
| career-proof, 404-mesh, open-notebook, contextlandscape | `E:\resume`, `C:\work\404`, `C:\work\notebook`, `C:\work\contextlandscape` | 1 each | 0 | intra-repo only |

Schema (`framework/src/constellation_manifest/models.py`, 645 lines): a `RepoEntry` node has `name`, `kind`
(git | filesystem | monorepo-package), `github` (`org/repo` slug, not a URL), `local_path` (Windows), `aliases`, `role`,
`producer_type`, `lifecycle`, `primary`, `surfaces`, and the edges `depends_on` (untyped, directed, by name) and
`parent`; `Contract` is producer → consumers (`scope` cross-repo | intra-repo); `DataSource` → `consumed_by`;
`PipelineTool` is constellation-wide. **No dates in the YAML.** 87 unique repo names, 74 github slugs (`sealcompanion`
and `deepnorthtesting` share one); ~13 filesystem-only repos join by directory name. Name differences from remotes:
old-goat-new-tricks = llmquest, guild = goatsafterdark, img = tempo-imagegen, reader = indexcard, planner = start-planner.

The typed graph: `exports/jepa-graph.v1.json` (181 KB, plain JSON; a 2026-06-01 snapshot beside it): 88 nodes, 134
directed edges typed consumes 78, produces_data_for 36, verifies 7, leases_hardware_to 3, describes_topology_for 3,
extracted_from 2, replaces 2, hosts_awareness_for, control_plane_for, bridges_traffic_to 1 each; `valid_from` dates are
compiler-inferred (hard-coded or latest-commit fallbacks: rough ordering only, never truth); 8 self-edges to filter;
names lower-cased (`selfiestick`, `chatgpt_parser`). 358 `important_artifacts` (ADRs, handoffs, benchmarks) carry a
real `created_at`. `/home/derek/work/jepa-temporal-lineage-20260925/` (immutable; read only) already resolved these
edges: `relationships-resolved.json`, `entity-resolution.json`, `git-history.json`.

Reuse: constellation = hex cluster with its `primary` repo at the centre; `depends_on`, `parent`, `consumes`,
`extracted_from`, `replaces` = adjacency; cross-constellation edges and `bridges_traffic_to`, `leases_hardware_to`,
`control_plane_for`, `describes_topology_for` = bridges; integrations per repo = cross-repo contracts produced or
consumed + data_sources + depends_on in and out (intra-repo contracts excluded). Join to lineages by github slug, then
directory basename and aliases. Relationship dates come from our own corpus (an edge cannot predate either endpoint's
first commit); only GAD and ai-systems-research have a real YAML history (first commit 2026-05-24), the other ten were
batch-committed 2026-09-23.

## 3b. ChatGPT-era links and liveView (surveyed 2026-10-09)

**liveView is not an inventory source.** `E:\work\liveView/ingest/out` holds three snapshots of 12 to 75 UUID-named run
folders scanned on 2026-03-11 (no drive letters, every `modified` is scan time, `edges.json` empty); `artifacts/sessions`
holds 7 research-handoff packages (2026-03-07 ×2, 2026-04-10 ×5; `request_log.json`, some with a UTF-8 BOM) that record
repos and files touched by the AI-assisted work on liveView itself. Use only as minor markers for that project.

**chatGPT_parser projections link conversations to projects** (`E:\work/chatGPT_parser/data/projections`, built
2026-09-23; conversations per year 2023: 6, 2024: 6, 2025: 211, 2026: 157):

| File | Records | Metadata fields to use (never `title`, `title_hint`, `text*`, `*_preview`, `intent_terms`) |
|---|---|---|
| `timeline.ndjson` | 380 | `conversation_id create_time update_time duration_seconds message_count artifact_count commands_used[] key_file_paths[] has_code has_errors phase_label phase_confidence` |
| `session_classification.ndjson` | 380 | `commands_used[] code_languages[] has_* assistant_user_ratio phase_label` |
| `decision_trace.ndjson`, `session_strategy_summary.ndjson` | 380 | `key_file_paths[] strategy_label turning_points[] recovery_after_error artifact_driven` |
| `artifact_workflow_paths.ndjson` | 1,314 | `file_path conversation_id workflow_label phase_label message_ids[] artifact_ids[] command_names[]` |
| `artifact_index.ndjson` | 3,879 | `artifact_id artifact_type (code 3,512 / execution_output 367) conversation_id source_message_id file_references[] approx_lines language` |
| `activity_calendar.ndjson` | 189 | `date conversation_count message_count artifact_count command_invocation_count error_conversation_count` (2023-04-17 → 2026-03-11) |
| `entity_usage_map.ndjson` | 1,667 | `entity_type (repository 920, file_path 643, tool 64, …) entity_label conversation_ids[]` |
| graph `nodes.ndjson` (69 MB, stream) | 32,523 | Message nodes: `create_time file_references[] shell_commands_detected[] role`; 1,103 messages in 92 conversations carry file references |

Labels: `phase_label` implementation 172, mixed 134, problem_framing 53, verification 18, investigation 3;
`strategy_label` debugging 91, debug_build_loop 86, exploration 84, mixed 36, visual_inspection 34,
artifact_implementation 32, implementation 17. 158 conversations have a code or output artifact; 74 name a file path.
Drive-letter paths start 2025-08-23 and name about 8 projects: `D:/work/liveView` (108 mentions, 8 conversations),
`D:/work/ai-dev-system` (35, 6), `D:/work/stars-app` (20, 5), `D:/work/ai-systems-research` (11, 3), `D:/work/writing`,
`D:/valhiem`, plus `C:/Users/derek`, `C:/Python312`. Drop relative paths and `/mnt/data` sandbox paths (85). Paths are
model-written text: intent, not proof. Nothing from 2023–24 carries a path; those years attribute by time only.

## 1g. Repositories outside the work trees (found 2026-10-09 after task 1b)

The `work` trees were not the whole territory. Bounded finds (maxdepth 3, excluding ComfyUI, SteamLibrary, node_modules)
found on **E: root**: `omen/{CC, clippy, DMos, DMos-actor-controls, DMos-chronicle, DMos-chronicle-salience,
DMos-command-freshness, DMos-rc1, DMos-rehearsal, DMos-secrets, imagegen, menu, tensor, bf6-highlights-retired-20260828}`
(the omen-core constellation's clippy, img/imagegen, menu and tensor live here), `World of Warcraft/{code, Tempo,
tempo-viewer, Tempo-wt-A, Tempo-wt-A-1b9, Tempo-wt-B..F}` (GAD's tempo, tempo-viewer, wow-code; the Claude archive's
`D--World-of-Warcraft-tempo` project dir, 186 entries, points here), `gemini`, `helloworld/old-goat-new-tricks`
(= llmquest), `resume`, `resume-wt/{claude-seat-receipts, gemini-proof-snapshot, linux-proof-review-20261006}`. Non-git
E: root dirs to walk for births and updates: `linux, wool, writing, wt, cold-storage, continuity-evidence, repo-audit,
_migration, hiking, HANDOFF, gemini, wsl, tmp, IndexCard, BF6-Highlights, wtviewer-skin-previewshots`. On **C: root**:
`assessment` and `tuning` are git repos (births were walked; commits were not). `C:\Users\derek` holds no repos at depth 3.
A maxdepth-4 pass over E: root (excluding `work`) is part of task 1c.
