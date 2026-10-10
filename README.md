# Known World

A fog-of-war time-lapse of everything built on the lab's surfaces (C:, E:, omen-linux, AM4, FX99, GitHub) and
everything said to agents along the way, in the manner of Isao Hashimoto's "1945-1998". The world is laid out once
from the final corpus and revealed as it is touched; conversations are the radio traffic.

Goal `G-known-world` in `~/work/lab/intent.yaml`. Plan: `~/.claude/plans/moonlit-wandering-sunbeam.md` (approved
2026-10-09). Handoff briefs: `~/work/known-world-plan/0-index.md`. Living plan: `plan.html`.

## Read first

1. `DIRECTION.md`: the creative direction and the initial parameters.
2. `CONTRACT.md`: the data contract, allowlists, lineage rules, operating rules. Everything flows through it.
3. `SURVEY.md`: what exists, where, how big; the Scope agent turns it into the work-list.
4. `EVIDENCE-HUNT.md`: repeatable local-scout discovery workflow, measurement recipes and the 2026-10-10 coverage hunt.

## Layout

```
collect/knownworld/   extractors (one per source type), identity.json, privacy_scan.py, run_item.py
corpus/raw/<item>/    fleet output per work item: events.ndjson, repos.ndjson, manifest.json, card.md
corpus/merged/        merge.py output: events.ndjson, repos.json, actors.json, hosts.json, sessions.json
corpus/CORPUS-REPORT.md
compile/              layout.py (hex world), timeline.py (touches, decay, camera, rates), audio.py (wav)
render/               index.html + kw.js (Canvas 2D, deterministic render(t)), styles.css
export/               frames.mjs (Playwright headless Chromium), encode.sh (ffmpeg)
laps/LAP-NN-<var>/    RESULT.md, preview, frame grid
cache/clones/         --mirror clones of GitHub repos missing locally (gitignored)
```

## Environment

```
uv venv .venv && uv pip install --python .venv/bin/python numpy imageio-ffmpeg
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 GIT_TERMINAL_PROMPT=0
```

Windows mounts are read-only; nothing is ever written there or into `jepa-*`, `hybrid-context-trial`, `runs/`.
Chat sources are metadata only; see CONTRACT.md §2.

## Status

- 2026-10-10 public release: https://fx99.tail8e749c.ts.net/known-world/ — 98 seconds,
  including a five-second animated key, slower burst/tone tails, five-to-seven story-day
  connection memory, improved burst contrast and three extra seconds fading before closing totals.
  Both the original stable media URL and the current hashed video serve this release.
  The older `/chronicles/known-world/` remains an alias of the same content.
  See [current handoff](HANDOFF-20261010.md) for release hashes, regeneration and deployment details.

- 2026-10-10: [LAP-23](laps/LAP-23-experimental-shapes/RESULT.md) discovers evidence by schema across
  known roots, including ignored outputs and removed Git artifacts. Reconciles 436 configurations and 1,487
  measured trials, folds 3,356 copied rows, recovers 60 dated Memsplice experiments from source hashes,
  and adds undated image evidence to the ending card. Updated FX99 film published and checked.
- 2026-10-10: [LAP-22](laps/LAP-22-windows-research/RESULT.md) recovers 11,388 direct Windows research
  attempts, 41 finished B70tools/Vllama runners and 210 dated Battlemage benchmark measurements.
  Adds visible counters, timeline rows and source coverage; published on FX99 with verified playback and asset hashes.
- 2026-10-10: [LAP-21](laps/LAP-21-count-audit/RESULT.md) independently audits raw records, compiled counters,
  rendered sidebar text and the public release. Corrects mirrored-session counts, unlabelled bursts, inconsistent
  local-call counts and omitted ending-summary activity. Corrected FX99 film is published.
- 2026-10-10: [LAP-20](laps/LAP-20-publication/RESULT.md) publishes the recovered film, poster and categorized
  evidence summary on [FX99](https://fx99.tail8e749c.ts.net/chronicles/known-world/). Live media hashes, playback,
  seeking and desktop/mobile layouts verified. Snapshot cutoff: October 9, 15:41 UTC.
- 2026-10-10: [LAP-19](laps/LAP-19-benchmark-history/RESULT.md) recovers 257 benchmark runs, expands dated
  invocation coverage to 629, and adds 23 fleet-result observations. Includes the reusable recovery workflow
  and explicit AM4/Conductor archive gaps. Local preview only.
- 2026-10-10: [LAP-18](laps/LAP-18-activity/RESULT.md) adds execution, Antigravity and research activity,
  uncapped numeric totals, landscape/portrait stills and an eight-second audio excerpt. Local preview only.
- 2026-10-09: scaffolded; contract v1; surveys in; gh installed (auth pending Derek's token); corpus run next.
