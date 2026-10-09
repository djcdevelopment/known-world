# DIRECTION.md: creative direction (Fable, 2026-10-09)

## The reference

Isao Hashimoto, "1945-1998" (youtube.com/watch?v=cjAqR1zICA0). A still, dark world map. One second per month; a date
ticker; nothing else narrates. Each detonation is one flash and one short tone, pitch by nation; each nation keeps a
running tally in the border. The emotional arc is carried entirely by density: lonely early flashes, a cold-war
cascade, then quiet. Negative space is the medium. Identity is colour and pitch. The tallies count so the map never
has to.

## The transposition

Everything Derek built (repos, directories, files, commits, branches, worktrees on C:, E:, omen-linux, AM4, FX99 and
GitHub) and everything he said to agents (ChatGPT, Claude Code, Codex, OpenCode, and the frontier-to-local chatter
through HEARTH), as one time-lapse with two substitutions:

1. **Fog of war instead of a given map.** The world is laid out once from the final corpus and revealed as it is
   touched. Civilization's three states: *unknown* (void), *explored* (touched once; dim, desaturated, remembered),
   *active* (touched recently; lit). Activity decays with a half-life. The camera fits the known world, so the map
   scales and expands with understanding.
2. **Radio chatter as a signal layer.** Conversations are comms traffic rendered against the volume, size, scope and
   frequency of the territory, over time, via size, scale, colour, intensity and opacity.

## Visual grammar

| Element | Rule |
|---|---|
| World | Hex tiles. Continents = physical surfaces (C:, E:, omen-linux, AM4, FX99). Regions = repos and large non-git directories. Tiles = directories to depth 2, area by log(file count). Laid out once (final state), revealed progressively. |
| Lineage | The same repo on two surfaces is one lineage; its regions are linked by a bridge that lights when both exist (clone, migration). |
| GitHub | An archipelago at sea. Remote-only repos are islands; a pushed lineage gets a harbour mark on its home region. |
| Third-party clones | Another civilisation's land: grey, hatched, never counted as built. Lap variable: hidden vs shown. |
| Camera | Fits the bounding box of explored tiles with padding and slow easing; the world grows, early tiles shrink. |
| Hue = who | human warm white · ChatGPT green · Claude coral · Codex cyan · OpenCode violet · local models ember red · automation/builders amber · third-party grey. Surfaces carry only a subtle terrain tint. Lap variable: actor vs surface. |
| Commit | A flash on the touched tiles, intensity by log(lines), one tone. |
| Repo born | A slow bloom and a low bell. |
| Branch / worktree | A short spur off the region. |
| Chat message | A tick on the radio band. Sessions with a cwd draw a faint comms beam from the operator's HQ to the region. ChatGPT (no cwd) broadcasts rings into the dark. |
| HEARTH offload | A spark between HQ and a seat marker (frontier → local chatter). |
| Border | Right: tallies per actor class (commits, files, messages). Left: tallies per surface. Bottom: the radio band, a scrolling density trace coloured by class. Top: the date ticker with the current rate shown. |
| Ending | Camera pulls back to the whole known world. The unknown stays dark. Tallies settle. Silence. A final tally card. |

## Sound

One tone per commit, pitch by actor class (human A3, Claude E4, Codex G4, OpenCode B4, local models C3, automation D4,
third-party muted), gain by log(lines). Above about 8 events per second, events collapse into a roll or chord so the
ear is not flooded (lap variable). Chatter is band-passed static whose amplitude follows message rate, with a class
colour on the band. Repo births are bells. The ChatGPT years are static with no tones: radio before territory.

## Pacing (initial; lap 3 varies it)

| Era | Span | Rate | Length |
|---|---|---|---|
| A | 2011-08 → 2023-03 | 1 year = 4 s | ~46 s |
| B | 2023-04 → 2026-02 | 1 month = 2.5 s | ~88 s |
| C | 2026-03 → present | 1 day = 2.4 s | ~8.8 min |

About 11 minutes, in the reference's range. A 90-second cut uses the same timeline at a uniform multiple; the ticker
always shows the rate, because the reference never changed rate and we do.

## The story the corpus already tells

Chat coverage is continuous from 2023-04; built code starts 2026-01 and explodes 2026-03. The first act is two and a
half years of radio into the dark before any territory appears. Then the Windows continents fill (March to September
2026), then the Linux continent appears and the old one dims (the migration), then the local seats start answering
(HEARTH sparks). Honesty rule: we show what was touched, not a finished map; quiet years stay visibly quiet.

## Initial parameters (the compile layer reads these; laps change them one at a time)

```
fog_half_life_days: 30        hue_axis: actor        geography: surfaces
collapse_events_per_s: 8      camera: fit_known      third_party: ruins
era_rates: {A: 4/yr, B: 2.5/mo, C: 2.4/day}          cut_90s_multiple: auto
```

Records use laboratory language (Workflow, Run, Lap, Candidate, Receipt, Verdict); steppe lore only at render time.
