# knownworld collectors

One entry point: `run_item.py <item.json> [--budget-s N] [--retry-skipped] [--fresh] [--list]`.
Run it with the project venv and the safe environment:

```
cd /home/derek/work/known-world
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 GIT_TERMINAL_PROMPT=0
.venv/bin/python -I collect/knownworld/run_item.py corpus/worklist/<id>.json --budget-s 540
```

- Exit 0: complete (manifest `complete`, or `partial` with every gap listed in `coverage.sources_skipped`).
- Exit 3: budget exhausted or mount slots busy; run the same command again (it resumes from `checkpoint.json`).
- Exit 1: failed (nothing usable, enumeration error, no sources found, or another run holds the item lock).
- A Bash call may run 600 s at most: use `--budget-s 540` and `timeout 600000`.
- `--retry-skipped` re-queues sources recorded as skipped (timeouts); `--fresh` discards the item's output and starts over;
  `--list` prints source and shard counts and processes nothing.
- Output: `corpus/raw/<id>/{events.ndjson, repos.ndjson, manifest.json, checkpoint.json, run.log}` (+ `github_repos.json`
  for github-list). `run.log` holds counts and byte offsets only. Never print or open a corpus line; report manifest fields
  and `privacy_scan.py` verdicts.
- `privacy_scan.py <dir|file>`: exit 0 clean, prints counts only. `missing_repos.py`: GitHub repos no local remote names.
  `clone_mirrors.py [--dry-run]`: mirror clones into `cache/clones` plus `corpus/worklist/mirror-*.json` items.
- Mount items hold one of 3 flock slots per mount (`cache/locks`); a full mount makes the run wait up to 240 s, then exit 3.
- Common warnings: `numstat_failed:*` / `numstat_skipped` (commit counts kept, line counts 0: partial clone or timeout),
  `commit_count_mismatch` (parsed log differs from `rev-list --count --all`), `pending auth: private repos not listed`,
  `sqlite_immutable_wal_may_be_missed`.
- Source types: git_repo, fs_births, claude_jsonl, codex_jsonl, chatgpt_export, opencode_db, hearth_ledger, continuity
  (+ deepagents_runs parts), github_api. Item `options` per type are documented at the top of each module and in
  `make_worklist.py`, which regenerates `corpus/worklist/`.
