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

- 2026-10-09: scaffolded; contract v1; surveys in; gh installed (auth pending Derek's token); corpus run next.
