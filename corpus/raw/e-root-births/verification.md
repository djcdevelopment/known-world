# Verification (task 1c manager)

Recount by a different path: plain `find -type f` over the same trees with the same prunes and name exclusions, plus a loose-file listing for the 5 container levels.

- Fleet total 491,667 files (births); recount 491,657 tree files + 16 loose = 491,673. Difference 6 (0.001%), not isolated; recount side is higher.
- First run found 6 records with an empty repo key for E: root loose files (`dir:omen-e:`); fixed to `dir:omen-e:.` in fs_births.py and re-run with --fresh.
- `*.pcm` and `msdownld.tmp` added to the exclusions and the item re-run with --fresh.
- Privacy scan: exit 0, violations=0.
