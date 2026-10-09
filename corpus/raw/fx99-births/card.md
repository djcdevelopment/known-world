# fx99-births: Non-git directories on FX99

## Source

Source type: fs_births (v1.4: file_birth and file_update). Six non-git directories on FX99, walked over ssh with fs_find.py shipped on stdin and folded locally.

## Span

Birth and update days as folded per depth-2 directory and day; the merged report (section 12) carries the year-month counts.

## Folded

6 sources walked, none skipped. Records: 52 file_birth (3873 files), 197 file_update (3475 files), 45 bulk-copy flagged. Updates are a lower bound: the filesystem keeps only the last modification.

## Quirks

Birth time comes from GNU stat through find; fs_find falls back to mtime only if find is missing.

## Next run

Re-run with --fresh after any change to fs_find.py; the walk is fast (seconds to minutes). Nested git repositories inside non-git directories are walked as plain files.
