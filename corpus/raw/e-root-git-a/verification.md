# Verification (task 1c manager)

Recount by a different path: `git rev-list --count --all` on each root through the safe-directory git wrapper (GIT_OPTIONAL_LOCKS=0), compared with `repos.ndjson` commits.

- Non-worktree repositories: all counts equal.
- Linked worktrees: the `.git` file points to a Windows path, so `rev-list` fails on the Linux side; the toolkit resolves them through the parent `.git/worktrees` and records 0 commits with a `common_dir`. Resolved: all of them.
- Submodule `omen/CC/GeneralsReplays` (relative `gitdir: ../.git/modules/...`) was first recorded as an unresolved worktree with 0 commits; `git_repo.py` now reads it as a full repository (4 commits, equals rev-list).
- Privacy scan: exit 0, violations=0.
