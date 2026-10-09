# github-list: GitHub repository list, authenticated

## Source

`gh repo list` for djcdevelopment (89 repositories: 50 public, 39 private, 4 forks) and steppe-integrations (4 public). Fields kept: name, url, private flag, fork flag, size, created, pushed, primary language. Descriptions are not stored.

## Output

93 `repo_born` events (host github), one per listed repository; `github_repos.json` (git-ignored) carries the private flag. Manifest `complete`, no warnings.
