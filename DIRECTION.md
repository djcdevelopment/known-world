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

## The payload model (Derek's call, 2026-10-09; this is the event model)

Derek's correction, taken as the design: commit volume is not the detonations. In the correlation to the original,
the commit spam is the investment in and prioritization of the nation's scientific and industrial infrastructure,
the capacity that makes a test possible. The payloads are the focused, intentional developer/creator/operator
interactions that generate a project of a particular size; yield is what that interaction produced: lines of code,
number of files, number of integrations, amount of moving pieces.

So the piece has two layers with different physics:

- **Infrastructure** (continuous, cumulative, rendered as fields): commits, files, directories, branches, worktrees
  and routine chatter. They reveal and grow the territory (fog, tile brightness, region size) and hum on the radio
  band. They never flash and never beep. Their rate is the industrial tempo; the border carries them as capacity
  (commits, files), in a smaller second line under the test tallies.
- **Launches** (discrete, rendered as detonations): an intentional work episode on one lineage. The operator engages
  (a Claude Code, Codex or OpenCode session whose cwd maps to the lineage, or a human-only burst) and a cluster of
  commits follows within a gap window. One episode = one test. Flash radius, bloom duration and tone length scale with
  yield; pitch by nation (the actor class that conducted it); the border tallies **tests and cumulative yield per
  nation**, like the original's per-country counters.
- **Yield** (per episode, from metadata only): lines = insertions + deletions; files = distinct files touched;
  integrations = distinct lineages, hosts and seats touched (a commit that lands on two surfaces, an offload to a local
  seat, a push to GitHub each count); moving pieces = distinct depth-2 directories plus branches and worktrees created
  plus distinct agent classes involved. A yield class on a log scale (bands tuned in a lap) sets the visual size, as
  kiloton to megaton did.
- **Before git** (Derek, 2026-10-09): he was historically terrible about even making repos or committing in early
  tests, so file creation and update volume, frequency and density stand in for commits there. A burst of file births
  and updates in a directory is an episode like any other, with yield in files, bytes and moving pieces; the ChatGPT
  conversations active around it give the nation (inferred, and marked so). The early tests are real tests.
- A new lineage's first episode is its first test (the bloom and the bell stay). ChatGPT sessions (no cwd, 2023-04 to
  2026-03) are the research program before any test: radio only.
- **Episode detection** (compile layer; lap variables): a gap over 2 h between commits on one lineage closes an
  episode; a session joins an episode when its cwd maps to the lineage and overlaps the window by 30 min either side;
  the minimum yield to count as a test is 50 lines or 3 files (below that it is infrastructure maintenance); an episode
  with no session is a human-only test (nation human).
- **Shape** (Derek, 2026-10-09): tests change shape over the piece. Early tests are single blips (a PoC), then bigger
  and bigger single blips for larger tests. Later, projects start as **MIRVs** (cluster bombs): one operator
  engagement whose commits land across several lineages, worktrees or hosts inside the same window, drawn as one beam
  from HQ that splits into N smaller warheads scattered over their targets, "scatter-bomb effective". Some of those
  later consolidate into **one large unified blip** when the worktree branches merge back or the migration copies
  unify on the parent lineage. Detection, from metadata: an episode whose commits touch ≥ 2 lineages or linked
  worktrees within the gap window is a MIRV with that many warheads (the 94 Linux worktrees, 57 of them on
  commandcenter, are the fleet era); a unification is a large-yield episode on a parent lineage within a day of ≥ 2
  warheads on its worktrees or components (signals available: worktree and branch events, lineage components with
  several records, commits present on several hosts). Thresholds are lap variables.

## Two evolutions at once (Derek, 2026-10-09)

The viewer is watching Derek's evolution and the industry's evolution at the same time, and the piece must read as
both without narration:

- **The operator's curve** is the shape and yield of the tests: blip, larger blips, MIRVs, unified blips; the
  cadence of launches against the industrial base underneath them; the move from one surface to several.
- **The industry's curve** is who is conducting the tests. Each agent class, and each model generation inside a
  class, enters the corpus at a date: the first ChatGPT conversation (2023-04), the first Claude Code session, the first
  Codex session, the first builder automation, the first offload to a local seat, the first Opus 5, Fable 5, Sonnet 5.5
  trailer. Each first appearance is **a new nation's first test**: a new colour and a new tone enter, and the nation's
  name appears in the border from that moment. The original's legend was fixed; ours grows as the club grows. Model
  generations within a class are shades of the class hue (lap variable: shade per generation vs one hue per class).
- The two curves are read against each other: the industrial base and the chatter (research) rise first; nations
  enter; tests grow and change shape; the mix of nations shifts from ChatGPT alone to Claude, Codex, fleets and local
  seats. The honesty rule holds: nothing is annotated; the data carries it or it is not there.

## Visual grammar

| Element | Rule |
|---|---|
| World | Hex tiles. Continents = physical surfaces (C:, E:, omen-linux, AM4, FX99). Regions = repos and large non-git directories. Tiles = directories to depth 2, area by log(file count). Laid out once (final state), revealed progressively. |
| Lineage | The same repo on two surfaces is one lineage; its regions are linked by a bridge that lights when both exist (clone, migration). |
| GitHub | An archipelago at sea. Remote-only repos are islands; a pushed lineage gets a harbour mark on its home region. |
| Third-party clones | Another civilisation's land: grey, hatched, never counted as built. Lap variable: hidden vs shown. |
| Camera | Fits the bounding box of explored tiles with padding and slow easing; the world grows, early tiles shrink. |
| Hue = who | human warm white · ChatGPT green · Claude coral · Codex cyan · OpenCode violet · local models ember red · automation/builders amber · third-party grey. Surfaces carry only a subtle terrain tint. Lap variable: actor vs surface. |
| Commit | Infrastructure: reveals and brightens the touched tiles, grows the region; no flash, no tone. |
| Launch | The detonation: a flash whose radius, bloom duration and tone length scale with yield; pitch by nation (actor class). |
| Repo born | A slow bloom and a low bell (the lineage's first test). |
| Branch / worktree | A short spur off the region (infrastructure). |
| Chat message | A tick on the radio band (density). A session whose cwd maps to a region draws a faint comms beam from the operator's HQ to it: the countdown before a launch. ChatGPT (no cwd) broadcasts rings into the dark. |
| HEARTH offload | A spark between HQ and a seat marker (frontier → local chatter); counts as an integration in the episode's yield. |
| Border | Right: per nation (actor class), tests and cumulative yield, with capacity (commits, files) as a smaller second line. Left: tallies per surface. Bottom: the radio band, a scrolling density trace coloured by class. Top: the date ticker with the current rate shown. |
| Ending | Camera pulls back to the whole known world. The unknown stays dark. Tallies settle. Silence. A final tally card. |

## Sound

One tone per launch, pitch by nation (human A3, Claude E4, Codex G4, OpenCode B4, local models C3, automation D4,
third-party muted), length and gain by yield class. Infrastructure is a hum whose level follows the commit rate;
chatter is band-passed static whose amplitude follows message rate, with a class colour on the band. Repo births are
bells. Above about 8 launches per second (unlikely after episode detection; the collapse rule stays as a safety)
launches collapse into a roll or chord. The ChatGPT years are static with no tones: radio before territory.

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
episode_gap_h: 2              session_overlap_min: 30
min_yield: {lines: 50, files: 3}                      yield_bands: log10 (tuned in a lap)
```

Records use laboratory language (Workflow, Run, Lap, Candidate, Receipt, Verdict); steppe lore only at render time.
