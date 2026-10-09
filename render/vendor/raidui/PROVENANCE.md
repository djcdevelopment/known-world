# Vendored from RaidUI (Derek's own WoW raid-replay project)

Source: E:\work\RaidUI (/mnt/omen-e-read/work/RaidUI), master at c3933d3 (2026-05-16T17:18:33-07:00), remote djcdevelopment/RaidUI.
Copied 2026-10-09 for reuse in Known World; see SURVEY.md section 4b for the reuse assessment. Files are unmodified
copies; adapt them in render/, never edit these copies.

| File | Origin | Why |
|---|---|---|
| render-state.js | src/overlay/render-state.js | pure (data, t) -> state with scratch buffers; works under Node |
| playback-controller.js | src/compare/playback-controller.js | shared clock with deterministic _tick(dtMs); rAF starts/stops on demand |
| density.js | src/shape/density.js | 200x200 Float32Array point-density grid (fog / heat mask) |
| palette.js | src/shape/palette.js | OKLCH role palette with djb2 hash hue jitter: stable colour per id |
| registry.js | src/overlay/registry.js | overlay descriptor {id, name, enabled, zIndex, render(ctx, state)} |
| trails-2s.overlay.jsx | src/overlay/builtins/ | fading trail = the decay template (resample by frameLookup(t - k*step), alpha by age) |
| useRafPlayback.js / .ts | src/replay/hooks/, NewUI/app/src/hooks/ | the single-rAF clock with speed, pause, scrub (ADR-016) |
| Transport.tsx | NewUI/app/src/ | scrubber + play/pause/speed; writes the clock readout with textContent from the rAF loop |
