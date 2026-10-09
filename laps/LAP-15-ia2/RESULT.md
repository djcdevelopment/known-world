# LAP-15 information architecture 2: result (builder Sonnet 5.5, work item w-26069fe96149)

Spec: the approved plan (sections 1 to 5, 8, 10 with the gaps list, 12). Runner `laps/LAP-15-ia2/lap.py`. Notes are appended step by step.

## Step A: start date 2026-01-01, single era, prologue card
- `compile/params.json`: `eras: single`, `start_date`, `prologue_s` 3 (cut: `prologue_cut_s` 2), `prologue_text`, `uncertainty_footer` (the tally-card footer lines are now params).
- `compile/clock.py`: single-era path (one rate, no boundaries, no glides, `intro_s` = prologue). Every frame carries era index 2 so the day-grain ticker, week unit, 30-day regime minimum and `camera_memory_days` C read one era with no further change; `era_switch_f` is empty, `rate_labels` has the one label at index 2, `summary` reports `eras: single`.
- `compile/corpus.py:load`: events before `start_date` are tallied into `c.prologue` (ChatGPT conversations, own commits, repositories, first and last month; third-party events counted apart) and never indexed; a GitHub `repo_born` earlier than the start is kept at the start frame (it existed from frame 0); lineage `first_ts` clamped. `series.class_series` applies the same filter (it re-streams the corpus).
- Consumers made single-era: `build_data` (`era_count`, empty switch list), `build.py` (no era marks, `intro_f`, `prologue` block, footer from params), `stream._ruler` (day ticks from the start), `camera.py` (`hq_join` = first launch), `player.js` (scrubber segments from the clock's era list), `card.js` (prologue card: dark card, one wrapped line, fade in 0.3 s and out 0.5 s; footer wrapped to 1600 px).
- Receipt (`check-a`, `ct receipt://1f7fe41504e2813b0beaccbd`): cut compiled twice byte-identical; `tau` from 0.0 to 281.65 days; one era; prologue counts 223 conversations, 5 commits, 3 repositories.
