# MERGE-READY (task 1d, 2026-10-09)

Built from corpus/raw (incl. github-list authenticated, mirror-2) into corpus/.merge-tmp; corpus/merged untouched. privacy_scan on .merge-tmp: exit 0.

| Total | corpus/merged (before) | .merge-tmp (after) |
|---|---|---|
| events (events_out) | 216,753 | 216,796 (+43) |
| lineages git / dir / github_only | 130 / 177 / 2 | 132 / 177 / 2 |
| lineage records in repos.json | 309 | 311 |
| repo records (stats.repo_records) | 213 | 217 |
| relations nodes / joined / edges | 88 / 88 / 223 | 88 / 88 / 223 |
| chatgpt_links with_lineages / matched | 14 / 5 | 14 / 5 |

Newly mirrored repos (private, djcdevelopment): continuity 5 commits, conductor 36, contextforge-contracts 2, claudefarm 0 (empty repository). continuity and conductor joined existing lineages (root commit) as extra names; contextforge-contracts and claudefarm are new lineages (2 commits, 0 commits).

Relations join delta: none. All 88 manifest repos were already joined; edge counts unchanged (223), by type and basis identical. The new lineages are not named by any constellation.yaml.

Swap (atomic per file; run only when the builder is not reading, events.ndjson last in the list is the large one):
```
cd /home/derek/work/known-world && python3 -c "import os; [os.replace('corpus/.merge-tmp/'+f, 'corpus/merged/'+f) for f in ('actors.json','chatgpt_links.json','hosts.json','relations.json','repos.json','sessions.json','stats.json','events.ndjson')]" 
```
