# DataTable

The board's tables: hairline rows with no zebra striping, mono uppercase heads and sans cells.

- Use `.kw-table`. Heads use `kw-label` (`muted`) and cells use `kw-table` (`fg`).
- A numbered first column takes `.kw-n` (mono, `accent`) to trace the eye path.
- In a decision table, the recommended option goes in `.kw-rec` (mono 12px, `accent`), followed by the reason in plain text.
- **Mobile first.** On phones, each row stacks as a block: the numbered cell on top, then each cell as a label/value pair. Give every non-numbered `<td>` a `data-label` matching its column head. From `bp-sm` it renders as a normal table.
