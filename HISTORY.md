# HISTORY.md: the historical-state contract (iteration 2, 2026-10-10)

Geometry may be retrospective; visibility never is. The final layout (where a constellation's disc sits, where a
region's tiles go, which slot a nation gets) is computed from the whole corpus so the world is stable and nothing
jumps. What is drawn at frame *f* is only what has evidence at or before the story time of *f*. The compile emits an
evidence frame for every drawn element and `export/verify.mjs` checks the drawn set against it (acceptance 3).

## What is known, when it becomes known, which evidence supports it

| Thing | Becomes visible when | Evidence (corpus field) | Uncertainty handling | Retrospective use allowed |
|---|---|---|---|---|
| Lineage (region) | its first commit, or its first non-git burst at or above `nongit_min_files` | `commit.ts_author`; `file_birth` / `file_update` per day | third-party clones never appear as Derek's land (default hidden) | tile placement inside the region (tree rings) |
| Constellation (continent) | its first member lineage becomes visible | `relations.json` membership; the member's first evidence | a lineage with no manifest entry joins the loose archipelago; the disc outline is never drawn, only revealed tiles | the disc's position and size |
| Coast label (constellation name) | from the second visible member (one region is a place, not yet a land) | as above | none | none |
| Tile | its first touch (a commit touching the directory, or a births/updates day) | `commit.files[]`, `file_birth`, `file_update` | bulk-copied directories (flagged) reveal at their copy day and never flash | tile shape and ring order |
| Cross-constellation bridge | both endpoints visible AND the relationship has dated evidence | the first commit of the `constellation.yaml` that names it (GAD and ai-systems-research 2026-05-24; the other ten 2026-09-23, a batch); `relations.json edges[].since` = later of the endpoints' first evidence | an edge dated only by the batch renders in the candidate (dashed) style until a MIRV or a session touches both ends; JEPA `valid_from` is never used | the arc's geometry |
| MIRV connector | at the launch | `launches.json` (shape, targets) | none (observed) | none |
| Harbour mark | the GitHub repository's `created_at` | `repo_born` on host `github` | the push date is unknown: the mark means "existed on GitHub from here"; mirrored-only repositories get no land, only a mark at their constellation's sea edge | none |
| Host badge and tint | the first evidence that the lineage's bytes or sessions were on that host | a Claude/Codex session with a cwd on that host naming the lineage (`sessions.json host, path, repo, first_ts`, or the chat buckets' host and path); a `file_birth` of the lineage's files on that host (a copy's arrival counts: that is when the bytes got there) | where no evidence exists, no tint: the region stays neutral with a "?" badge; a drive is tinted as a drive (E:, C:) because its machine is not evidenced; `commit.meta.hosts` (where a sha exists today) is never used for timing | none |
| Migration (tint change) | per region, when Linux evidence arrives | as above | no global migration event is drawn; the HQ ring moves with session evidence only | none |
| Nation row | the nation's first event | `events.actor.class` | zero-test rows show participations; nothing shows before the first event | the slot (reserved from the final count) |
| Generation chip | the generation's first test | `launches.json nation, generation` | unversioned trailers get no chip | none |
| Mark (ruler letter) | at its frame | `marks.json` | regime marks are causal: a breakpoint is drawn only once the data up to `bp + marks_min_days` reproduces it; the storm threshold is a trailing peak | none |
| HQ ring | from the first session with a cwd | `sessions.json` | before 2026-05-08 no Claude transcript survives: the HQ sits on the drive the commits came from, badge "inferred" | none |
| Seat beacon | the seat's first offload | `offload_call backend` | none | none |
| Camera | reacts after land appears (causal smoother, no look-ahead) | the revealed tiles and launch targets | the look-ahead camera is an arm, never the default | the fill ramp's normalisation by the final span (layout, not content) |

## What remains uncertain (stated once in the tally card's footer)

- No chat source covers 2026-04.
- No Claude Code transcript before 2026-05-08 survives; Claude's presence from 2026-01 to 2026-04 is known from commit
  trailers only.
- Relationship dates for ten of twelve constellations come from one batch commit (2026-09-23).
- Drive-to-machine assignment before the Linux era is not evidenced; those regions carry a drive tint, never a machine.
- Commits carry no host of origin.
- Playback starts 2026-01-01; the prologue card carries what came before (ChatGPT conversations from 2023-04, a handful
  of commits, no repository of Derek's own). Long-lived lineages first-touch in 2026 for that reason.

## Glossary of marks

nation (a colour enters) · constellation (a new land) · migration (a region gains its first Linux evidence) · storm (the
offload rate's trailing peak) · regime (a confirmed change in the growth of commits, launches or files) · host (a
region's tint changes).

Rules are parameters under `reveal.*` in `compile/params.json`, one key per row above, so a lap can tighten or loosen
one rule at a time.
