# CONTRACT.md: the corpus data contract (v1, 2026-10-09)

This file is the one agreement between the collection layer, the compile layer and the renderer. Extractors emit
exactly this; everything downstream reads exactly this. Change it by revision, with a note in `
## 8. Derived at compile time: launches (`compile/launches.json`)

Not collected; computed deterministically by `compile/launches.py` from `corpus/merged/events.ndjson` and
`sessions.json` under the payload model in DIRECTION.md. One record per intentional work episode:

```
{"launch_id": sha1(lineage + ts_start)[:12], "lineage": <repo id>, "ts_start", "ts_end",
 "nation": <actor class that conducted it: the dominant class of the episode's commits, else the session class, else human>,
 "sessions": [<session ids whose cwd maps to the lineage and overlap the window ± session_overlap_min>],
 "commits": n, "hosts": [...], "seats": [<offload backends called during the window>],
 "yield": {"lines": ins + del, "files": distinct files, "integrations": distinct lineages + hosts + seats touched,
           "moving_pieces": distinct depth-2 dirs + branches/worktrees created + distinct agent classes, "class": <band>},
 "shape": "single" | "mirv" | "unified", "warheads": n, "targets": [<lineage or worktree ids the commits landed on>],
 "unifies": [<launch_ids of the warheads this episode consolidated>] | [],
 "first_test": bool, "first_of_nation": <nation or model generation whose first appearance this launch is> | null}
```

Also derived: `compile/nations.json`, one record per nation (actor class) and per model generation inside it:
`{"nation", "generation", "first_ts", "first_launch_id", "tests", "yield_total", "last_ts"}`, ordered by first
appearance; the border's growing legend reads it. Sources for first appearance: `actor.name` on commits (trailers) and
`models` on sessions; offload_call `backend`/`model` for local seats.

Parameters (`compile/params.json`, lap variables): `episode_gap_h` (default 2), `session_overlap_min` (30),
`min_yield` (`lines` 50 or `files` 3; smaller episodes stay infrastructure), `yield_bands` (log10 of lines, tuned),
`mirv_min_targets` (2), `unify_window_h` (24), `generation_shades` (true).
Commits below the threshold and every chat_msg, file_birth, branch and worktree event remain infrastructure and are
rendered as fields, never as flashes. Two runs over the same corpus and parameters give byte-identical output.

## Revisions`.

## 1. Event records: `corpus/raw/<item>/events.ndjson`, one JSON object per line

| Field | Type | Rule |
|---|---|---|
| `ts` | string or null | UTC ISO-8601 (`2026-07-04T00:20:11Z`). Null when the source gives none, or the value is before 2005-01-01, after now, or a placeholder (1970-01-01, 1980-01-01). Merge drops null-ts events and counts them in the report. |
| `ts_author`, `ts_commit` | string | Commits only; `ts` = `ts_author`. |
| `kind` | enum | `commit` `repo_born` `branch` `worktree` `file_birth` `chat_msg` `chat_session` `offload_call` `receipt` `run` |
| `actor` | object | `{"class": <class>, "name": <string>}`; class ∈ `human` `chatgpt` `claude` `codex` `opencode` `local_model` `automation` `third_party`. `name` is a model name, a builder id, or `derek`; never an email; unknown humans get `sha1(name)[:12]`. |
| `role` | enum or absent | Chat only: `user` `assistant` `tool`. `actor.class` is the agent for every role; `role` says who spoke. |
| `host` | enum | `omen-c` `omen-e` `omen-linux` `am4` `fx99` `github` `cloud` |
| `repo` | string or null | Lineage id: the smallest root-commit sha in the lineage component (Merge assigns; extractors emit `repo_local`, see §3). Non-git: `dir:<host>:<top-level path>`. Chat and ledger events: null; Merge joins by `path`. |
| `path` | string or null | A directory to depth 2 relative to the repo (or surface) root, e.g. `src/hearth`. Drive-normalised: Claude project dirs `C--work-foo` → host `omen-c`, path `work/foo`; `E--…` and the older `D--…` → `omen-e`. |
| `files` | string[] | Commits only: the deduped depth-2 directories the commit touched. |
| `magnitude` | object | `{"n": int, …}` plus per kind: commit `files ins del`; chat `tokens_in tokens_out` (nullable); file_birth `bytes`; offload_call `tokens_in tokens_out duration_ms`. `n` is how many source events this record folds. |
| `ref` | string | Dedupe key: commit sha, session/message uuid, ledger `event_id`, GitHub `node_id`, or `sha1` of the folded key. |
| `src` | string | Extractor id (`git_repo`, `fs_births`, `claude_jsonl`, `codex_jsonl`, `chatgpt_export`, `opencode_db`, `hearth_ledger`, `continuity`, `github_api`, `deepagents_runs`). |

Folding rules (so the corpus stays tractable and private):

- `chat_msg`: one record per `(session, role, minute bucket)` with `n` = messages in that minute. Never one per message.
- `chat_session`: one record per session: `ts` = first message, `magnitude.n` = messages, `magnitude.duration_s`, `meta.sidechain` (Claude subagent transcripts), `meta.model` (assistant model names seen, list).
- `file_birth`: one record per `(depth-2 directory, day)` with `n` files and `bytes`. Birth time from `stat %w` (ntfs3 exposes it); mtime when birth is missing. Directories whose files share one birth second with their siblings (bulk copies) emit `meta.bulk_copy: true`.
- `commit`: one record per `(sha, host)`. Merge keeps the earliest `ts` and records the host set. Binary numstat (`-`) and merge commits emit 0.
- `branch`: `ts` = earliest commit unique to that branch; null if none.
- `worktree`: one record per linked worktree, `ts` = the worktree's first commit on its branch or the directory birth; Windows worktrees whose gitdir cannot be followed emit `meta.unresolved: true`.
- `repo_born`: local: the root commit's `ts_author`; GitHub: `created_at` with host `github`.
- `offload_call`: HEARTH ledger rows with `tool` in `{local_generate, submit_task, submit_local_work, submit_execution, submit_batch, submit_delegated_execution}` only (polling tools are dropped and counted); `actor.class` from `runner_class` (`frontier` → `claude` unless `caller.id` names codex; `local` → `local_model` with `model`; `human` → `human`).

## 2. Per-source allowlists (privacy is enforced by `privacy_scan.py`, not promised)

Every extractor declares the exact set of output keys it may emit and a validator per key. The scanner rejects any record with a key outside the allowlist or a value failing its validator (timestamp regex, 40-hex sha, uuid, enum, path depth ≤ 2 and ≤ 120 chars, integers). Common keys: `ts ts_author ts_commit kind actor role host repo repo_local path files magnitude ref src meta`. `meta` is itself allowlisted per source.

Fields that are **never read**, by source (they carry text or secrets):

| Source | Never read |
|---|---|
| Claude Code jsonl | `message.content` (except to count `tool_use` items and read `name`), `slug`, `customTitle`, `aiTitle`, `summary` records, `gitBranch`, `toolUseResult`, tool_use `input`, `attachment` records, `pastedContents`, `display`, `last-prompt` records |
| Codex jsonl | `thread_name`, `instructions`, `base_instructions`, `arguments`, `output`, `content`, `text`, `git.repository_url`, `payload.message` bodies |
| ChatGPT normalized | `title`, `title_hint`, `text`, `key_file_paths`, `parts`, `asset_refs`, anything under `search_index`, `decision_trace` |
| HEARTH ledger | `args_preview`, `result_digest`, `intent`, `reason`, `note`, `error` text (keep `error_code` only) |
| OpenCode sqlite | `parts`, `title`, `summary`, `diff`, any blob; read only `json_extract` of explicit keys |
| git | author emails, commit messages, diffs (numstat counts only), file names below depth 2 |
| continuity / deepagents | event `body` text; read `type`, `recorded_at`, `runner`, ids only |

Allowed from Claude Code jsonl: `type timestamp sessionId uuid parentUuid isSidechain cwd version message.role message.model message.usage.* stop_reason` and the `name` of each `tool_use` item. Allowed from Codex: `timestamp ordinal type payload.type payload.session_id payload.cwd payload.model_provider payload.cli_version` and token-count fields. Allowed from ChatGPT normalized: `conversation_id create_time update_time message_count user_message_count assistant_message_count model_slug role message_id parent_message_id` (ids only, no titles). Allowed from HEARTH: `event_id ts caller.id caller.runner_class caller.node tool ok duration_ms cost.* task_class model backend routed_by error_code outcome`.

Mechanics: JSON decode errors log the byte offset only. Zip members are allowlisted by glob (`.claude/projects/**/*.jsonl`) before `unzip -p`; the archive is never extracted. Credential-bearing paths are excluded before any walk: `.credentials.json`, `auth.json`, `callers.json*`, `*.pfx`, `*.secret`, `*.key`, `.env*`, `~/.git-credentials`, `*.caddy`. Agents receive counts and scan verdicts; they never print corpus lines (paths alone name private repos).

## 3. Per-repo lineage record: `corpus/raw/<item>/repos.ndjson`

One line per repository the item walked:

```
{"repo_local": "<host>:<path>", "host": ..., "path": ..., "remotes": [normalised URLs, userinfo stripped],
 "roots": [sha...], "root_tree": sha|null, "tip_tree": sha|null, "shallow": bool, "shallow_boundary": [sha...],
 "is_bare": bool, "is_worktree": bool, "common_dir": path|"unresolved"|null, "empty": bool,
 "first_ts": ..., "last_ts": ..., "commits": int, "refs": int, "authors": {"<class>": count},
 "third_party": bool, "derek_share": float}
```

`third_party` is true when `derek_share` (commits by `human` or AI-co-authored commits over all commits) is under 0.05, or the remote org is neither `djcdevelopment` nor `steppe-integrations` and no Derek identity appears. Merge builds lineage components by union-find over shared `roots`; shallow clones fall back to commit-sha overlap plus remote URL; squash-imported mirrors (`private-migration-*`) link by remote URL or `root_tree`; name-only matches are recorded as `{"link": "candidate"}` and never auto-merged. The lineage id is the smallest root sha in the component.

## 4. Identity map: `collect/knownworld/identity.json` (committed; Scope writes it, Merge applies it)

- Human: `derek`, `dciula`, `Derek Ciula`, `DjcDevelopment`, `djcdevelopment`, `Derek` → `{"class": "human", "name": "derek"}`.
- `Co-Authored-By:` trailers (case-insensitive, name part only): `Claude <family> <version>` → `claude` with the model name; `Codex` → `codex`; `cc-builder-*`, `am4-worker-*`, `omen-worker-*`, `builder-*` → `automation` with the id.
- Direct authors `Codex` → `codex`; `Claude Sonnet 5.5` etc. → `claude`; `ct (omen-linux)` → `automation`.
- Everyone else → `third_party`, name = `sha1(name)[:12]`.
- A commit with a human author and an AI trailer emits the AI class as `actor` and `meta.human_authored: true` (the map colours by who did the work; the tally board counts both).

## 5. Work items and manifests

Work item (input to a collector): `{"id", "source_type", "host", "roots": [paths], "shard": {"k", "n", "rule": "sha1(path) % n"}, "since", "until", "out_dir", "timeout_s", "mount": "c"|"e"|null}`. Shards are deterministic and disjoint.

`corpus/raw/<item>/manifest.json` (output): `{"item", "src", "started", "finished", "status": "complete"|"partial"|"failed", "events": int, "events_sha256", "repos": int, "dropped": {"null_ts": n, "polling": n, "decode_errors": n}, "coverage": {"sources_seen": n, "sources_skipped": [...]}, "warnings": [...]}`.

`corpus/raw/<item>/card.md` (output, written by the collecting agent): what the source is, its span, what was folded, quirks hit, what a future run should change. Never a corpus line.

## 6. Operating rules for every collector (in the toolkit, not left to agents)

- Environment: `PYTHONDONTWRITEBYTECODE=1`, `GIT_OPTIONAL_LOCKS=0`, `GIT_TERMINAL_PROMPT=0`, and `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0=*`.
- Git subcommands allowed: `log`, `rev-list`, `for-each-ref`, `rev-parse`, `ls-remote`, `cat-file`, `clone --mirror` (into `cache/clones/` only). Never `status`, `fetch`, `gc`, `worktree`, or anything that writes.
- Mounts `/mnt/omen-c-read` and `/mnt/omen-e-read` are read-only; at most 3 concurrent items per mount; every subprocess has a timeout; a timed-out item is `partial`, never silent.
- SQLite opens as `file:<path>?mode=ro&immutable=1`; the manifest notes that WAL contents may be missed.
- Never walk: `models`, `checkpoints`, `venvs`, `.venv`, `node_modules`, `.cache`, `ComfyUI/models`, `*.safetensors`, `*.gguf`, `~/hearth-production/var` except `var/ledger`, `~/work/amux/scratch`.
- Never write into `jepa-*`, `hybrid-context-trial`, `runs/`, or the mounts. All output goes under `~/work/known-world/`.
- ssh hosts (`am4` = 10.44.0.2, `fx99` = 100.122.130.124): `BatchMode=yes`, read-only commands, the git toolkit shipped as a single script via stdin.

## 7. Merged outputs: `corpus/merged/`

`events.ndjson` (same record shape, `repo` resolved, `(sha,host)` folded with `meta.hosts`), `repos.json` (lineage → names and paths per host, remotes, first/last, counts, third_party, region), `actors.json`, `hosts.json`, `sessions.json`, and `CORPUS-REPORT.md` (per source: covered / partial / absent with reason; reconciliation against SURVEY.md counts; dropped counts; candidate links).

## Revisions

- v1 2026-10-09: initial, from the approved plan `~/.claude/plans/moonlit-wandering-sunbeam.md` and the executability review.
- v1.1 2026-10-09 (toolkit, Sonnet manager): additions made while building `collect/knownworld/`, none loosening §2.
  Claude jsonl: `requestId` is read as an in-memory dedupe key only (a streamed reply is logged as several lines that repeat
  one `usage`), never emitted; content item `type` is read to tell tool results from prompts. Codex: `payload.model` of a
  `turn_context` is read as the model name and `payload.id` as a session-id fallback. `chat_msg.magnitude` may carry
  `tokens_cache` (cache reads) and `tool_calls`; `meta.session` links a record to its session. Git events carry
  `repo_local` (`<host>:<path>`, `~/`-relative on Linux hosts, drive-relative on the mounts); mirror clones set host
  `github` and `repo_local` `github:<owner>/<name>`. Birth times come from GNU `stat %W` through `find -exec` (GNU find has no
  birth directive). `github_repos.json` is a plain list. Manifest adds `sources` (`label`, `kind`, `raw`: commits, lines or
  rows) and `slices`; `coverage` adds `not_repos`, `excluded`, `null_ts_emitted`, `out_of_range`, `deduped`; `dropped` may add
  `other_role`. `dropped.null_ts` counts records the extractor could not bucket (no usable timestamp); events with a null
  `ts` that are still emitted (a commit with a bad date) are counted in `coverage.null_ts_emitted`. `third_party` counts only
  third_party-class authors against `derek_share` (agents and automation in Derek's repos are Derek's).
- v1.2 2026-10-09: section 8, derived launches under the payload model (Derek: commits are infrastructure; payloads are intentional interactions with a yield).
- v1.3 2026-10-09: launches carry shape (single, MIRV, unified), warheads and targets; derived nations.json for first appearances (Derek: watch the operator and the industry evolve at once).
