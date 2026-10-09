# NationStrip

The portrait nation zone. It is one 44px row of swatch-and-count chips under the ticker, and a tap opens the full nation rows beneath it.

- Markup: a `<details class="kw-strip">` whose `<summary>` holds a `.kw-chip` per nation (with a hue modifier such as `kw-nation--claude`) and a trailing `.kw-strip__more` label. `.kw-strip__rows` holds the `NationRow`s.
- Chips are in entry order. A chip appears at the nation's first event, fades in once and never moves.
- With more nations than fit, the strip scrolls sideways inside itself and the page never scrolls.
- The open rows overlay the map and do not push it. The camera does not re-centre.
- The rows sit one per line on phones and two-up from `bp-sm`.
- The export renders the strip closed.
- The consumer provides counts already abbreviated.
