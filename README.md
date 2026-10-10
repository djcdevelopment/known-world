# Known World

A time-lapse of a year of software development and AI experimentation, inspired by Isao Hashimoto’s *1945–1998*. Projects become land; recorded work lights it up. Human and AI activity forms a musical score beneath the map.

**[Watch the film on FX99](https://fx99.tail8e749c.ts.net/known-world/)** · 98 seconds · Best with headphones. The FX99 address requires access to its Tailscale network.

## Reading the world

A five-second animated key opens the film:

- **Land:** clusters represent projects and repositories; tiles represent folders.
- **Color and brightness:** color identifies the collaborator; brightness reflects weighted recent activity and fades over time.
- **Bursts:** larger flashes represent larger recorded output. Bright centers and expanding rings with dark edges keep them visible against matching terrain.
- **Connections:** moving trails show work reaching projects or local calls reaching machines. Recorded paths remain for five story days, fade through day seven, and renew with relevant activity. Pale project links and worktree spokes use the same fade window.
- **Circle and dot:** an inferred coordination hub, following the machine with the most recent recorded agent chat.
- **Score and totals:** activity over time appears below; recorded counts appear at right. The final map fades for three extra seconds before the closing totals.

The current story covers January 1 through October 9, 2026. Its evidence spans Windows C: and E:, Linux, AM4, FX99, GitHub, agent sessions, HEARTH dispatches and archived experiment results. Collaborators include human, ChatGPT, Claude, Codex, Gemini, local models, OpenCode and automation; Antigravity activity is tracked separately.

## Recorded scale

| Measure | Current evidence |
| --- | ---: |
| Commits | 9,784 |
| File touches | 209,848 |
| Line additions + removals | 18,447,909 |
| Local HEARTH calls | 22,672 |
| Gemini calls | 1,057 |
| Antigravity conversations | 160 |
| Completed invocations | 629 |
| Recorded benchmark runners | 298 |
| Native benchmark configurations | 436 |
| Measured experiment trials | 1,487 |
| Direct research attempts | 11,388 |
| Undated image results, outside the timeline | 4,533 |

These are overlapping views, not numbers to add into one grand total. File touches are observations rather than unique files; line changes are not current code size; runner, configuration and trial counts use different units. Copies and mirrored sessions are folded where native identities permit. Undated evidence remains visible without invented dates. Coverage is partial and does not measure total operator hours or hardware utilization.

[Evidence discovery and reconciliation](EVIDENCE-HUNT.md) documents the reusable search workflow, source shapes, historical recovery and remaining gaps. [The data contract](CONTRACT.md) describes collection boundaries and identity rules. Chat collection uses metadata rather than message bodies.

## Project layout

| Directory | Purpose |
| --- | --- |
| `collect/knownworld/` | Source adapters, schema discovery, recovery and metadata validation |
| `corpus/activity/` | Structured activity sidecars and coverage records |
| `corpus/discovery/` | Evidence inventories and schema/source reports |
| `compile/` | Deterministic geometry, counters, event timing and synthesized audio |
| `render/` | Canvas map, bursts, connections, score, opening key and closing card |
| `export/` | Browser frame capture, video encoding and static-site packaging |
| `laps/` | Iteration records, source audits and validation receipts |

Generated video, audio, PNGs, frame exports and build directories are excluded from Git. Historical evidence adapters rely on the lab’s source archives; the repository alone does not include every original source needed for a complete rebuild.

## Development and rendering

Python dependencies are NumPy and imageio-ffmpeg; frame capture uses Node.js, Playwright and Chromium. The current export scripts resolve Playwright from the local lab installation, so update that path when using a different environment.

```bash
uv venv .venv
uv pip install --python .venv/bin/python numpy imageio-ffmpeg
.venv/bin/python compile/build_cli.py --cut 90 --out <new-lap>/build
```

With the required source corpus available, export 2,790 story frames using `export/frames.mjs --query closingFade=3` and 150 opening frames using `--query intro=1`. Set `FFMPEG` to the executable supplied by imageio-ffmpeg. The five-second opener plus the 93-second story/coda produces the 98-second release.

[LAP-29’s assembly recipe](laps/LAP-29-burst-contrast/assemble.py) shows the reviewed audio/video assembly. For a new compile, use its matching WAV. Package with `export/publication.py --opening-seconds 5 --closing-fade-seconds 3`; its assets include both hashed filenames and stable compatibility aliases.

[The current handoff](HANDOFF-20261010.md) records release hashes, deployment, rebuild details and limitations. [Creative direction](DIRECTION.md) explains the visual approach.

## License

[MIT](LICENSE).
