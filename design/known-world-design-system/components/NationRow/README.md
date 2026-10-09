# NationRow

One collaborator in the frame's nation panel. It is the film's border counter: a swatch, the name, and the test count as the big number.

- Below the head: model chips in the nation's hue (named for three seconds at their first test), then a yield sub-line (`1.6M lines · 445c 3.8kf`), then base counters (`commits`, `files`, `lines`, `commits/wk`) with log bars on a shared scale. The bars carry quarter tick marks, as in the WiP render.
- Set the hue with a modifier: `.kw-nation--claude`, `--chatgpt`, `--codex`, `--auto`, `--local` or `--oc`. Human is the default.
- The row is fluid. It fills its column up to `nations-w` (320px), the landscape panel width. In portrait it lives inside `NationStrip`'s open rows at full width. Name and count step up from 20/28px to 22/30px at `bp-sm`.
- In landscape a row is 136px tall at seven nations or fewer and 96px (counters hidden) from the eighth. It appears at the nation's first event, fades in once and never slides.
- The consumer provides the numbers already abbreviated (`1.1k`, `3.2M`).
