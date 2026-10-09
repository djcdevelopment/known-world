# linux-births: Non-git directories on omen-linux

## Source

Source type: fs_births (v1.4: file_birth and file_update). Non-git directories under the Linux work tree plus the zero-commit jepa and hybrid-context-trial directories (read only) and the research directory.

## Span

Birth and update days as folded per depth-2 directory and day; the merged report (section 12) carries the year-month counts.

## Folded

49 sources walked, none skipped. Records: 600 file_birth (28769 files), 146 file_update (5474 files), 183 bulk-copy flagged. Updates are a lower bound: the filesystem keeps only the last modification.

## Quirks

Worktrees, amux and the corpus's own directory are excluded; loose top-level files are one source; the zero-commit repositories are walked as plain files (their .git is pruned).

## Next run

Re-run with --fresh after any change to fs_find.py; the walk is fast (seconds to minutes). Nested git repositories inside non-git directories are walked as plain files.
