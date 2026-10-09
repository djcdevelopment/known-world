# github-list (Source Card)

## Source Description

GitHub API list of repositories from the `djcdevelopment` user account (Derek's public GitHub presence, created 2011-08-25). Source type: `github_api`. The item collects public repository metadata using `gh api` without authentication, enumerating 50 public repos spanning from 2011 (personal_website fork) through 2026.

## Span and Coverage

- **Time span**: Repository creation dates from 2011-08-25 (personal_website) through 2026-10-08 (various recent projects)
- **Events collected**: 54 (each public repo's metadata)
- **Repos in scan phase**: 0 (the list phase enumerates repos; the scan phase would examine their contents, not applicable here)
- **Sources seen**: 1 (github-list)
- **Sources skipped**: 0

## Folded and Dropped

- **No dropped records**: null_ts=0, polling=0, decode_errors=0
- **Warning**: Pending auth for private repos (unauthenticated mode lists only public; private repos suppressed)
- The unauthenticated budget is 60 req/h; authenticated budget is 5000 req/h. No rate-limiting encountered.

## Slices and Execution

- **Slices used**: 1 of 1
- **Execution time**: 1 second (2026-10-09T12:45:09Z → 12:45:10Z)
- **Budget consumed**: <1 s of 540 s allocated
- **Status**: complete

## Quirks and Future Runs

- Private repos not listed (authentication pending; `gh auth status` would confirm available credentials)
- GitHub metadata includes `created_at` which may be later than local repository history
- No client-side errors or decode failures; clean run
- Future run should attempt authentication if private repo enumeration is needed

## Manifest Summary

- **events_sha256**: cd345abab9dcb1cb9e8a696ab71315db780539c7f6fbb32dc09b6210cf6fe01b
- **Status**: complete
- **Not-repos field**: 0 (no entries skipped as non-repository records)
- **Null timestamp emitted**: 0
