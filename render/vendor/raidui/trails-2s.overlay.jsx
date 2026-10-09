// trails-2s.overlay — last 2 seconds of entity positions as a fading polyline.
// ADR-002 §4: MUST use frameLookup(t) exclusively. MUST NOT read
// interpolatedPositions (that's only the current moment).
//
// zIndex 10 — below player-dots (20).

(function () {
  const TRAIL_MS = 2000;
  const STEP_MS = 100; // resample every 100ms regardless of frameStepMs

  function render(ctx, state) {
    const { pullReplay, entities, currentTimeMs, frameLookup, arenaRect, selectedEntityId } = state;
    const { x0, y0, size } = arenaRect;
    const n = entities.length;
    if (n === 0) return;

    // Walk back in time; each step resolves frameLookup into a position via
    // the two bracketing frames' entityPositions. frameLookup returns a shared
    // scratch object, so we MUST consume a/b/alpha immediately before the next call.
    // Pull coordinates into a local buffer per entity.
    const steps = Math.floor(TRAIL_MS / STEP_MS);
    if (steps < 2) return;

    // Build position series: series[pi] = [x_pix, y_pix, ...] for each step.
    // Allocation-light: one Float32Array per render. For 20 entities * 20 steps * 2
    // that's 800 floats — negligible.
    const series = new Float32Array(n * steps * 2);
    for (let s = 0; s < steps; s++) {
      const t = currentTimeMs - s * STEP_MS;
      if (t < 0) {
        // mark as NaN so the draw loop breaks the polyline.
        for (let i = 0; i < n; i++) {
          series[(s * n + i) * 2] = NaN;
          series[(s * n + i) * 2 + 1] = NaN;
        }
        continue;
      }
      const look = frameLookup(t);
      const a = look.a;
      const b = look.b;
      const alpha = look.alpha;
      const ap = a.entityPositions;
      const bp = b.entityPositions;
      for (let i = 0; i < n; i++) {
        const k = i * 2;
        const nx = ap[k] + (bp[k] - ap[k]) * alpha;
        const ny = ap[k + 1] + (bp[k + 1] - ap[k + 1]) * alpha;
        series[(s * n + i) * 2] = x0 + nx * size;
        series[(s * n + i) * 2 + 1] = y0 + ny * size;
      }
    }

    ctx.save();
    ctx.lineJoin = "round";
    ctx.lineCap = "round";

    for (let i = 0; i < n; i++) {
      const e = entities[i];
      if (e.kind === "Boss") continue; // boss has its own diamond; trails would clutter

      const isFocus = selectedEntityId === e.entityId;
      const dimmed = selectedEntityId && !isFocus;

      // Color: reuse class palette via RaidUIOverlay.colorFor if exposed.
      const color = (typeof window !== "undefined" && window.RaidUIOverlay && window.RaidUIOverlay.colorFor)
        ? window.RaidUIOverlay.colorFor(e)
        : "oklch(60% 0.08 250)";
      ctx.strokeStyle = color;
      ctx.lineWidth = isFocus ? 1.8 : 1.1;

      // Draw segments with per-segment alpha fade. Segment s connects series[s+1] -> series[s].
      for (let s = 0; s < steps - 1; s++) {
        const headIdx = (s * n + i) * 2;
        const tailIdx = ((s + 1) * n + i) * 2;
        const hx = series[headIdx];
        const hy = series[headIdx + 1];
        const tx = series[tailIdx];
        const ty = series[tailIdx + 1];
        if (!Number.isFinite(hx) || !Number.isFinite(tx)) continue;

        const age = s / steps; // 0 at head, →1 at tail
        let alpha = (1 - age) * 0.6;
        if (dimmed) alpha *= 0.1;
        if (alpha <= 0.01) continue;
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.moveTo(hx, hy);
        ctx.lineTo(tx, ty);
        ctx.stroke();
      }
    }
    ctx.globalAlpha = 1;
    ctx.restore();

    // Touch pullReplay to satisfy linter/guard that we inspected identity.
    void pullReplay;
  }

  const descriptor = {
    id: "trails-2s",
    name: "Trails (2s)",
    enabled: true,
    zIndex: 10,
    render,
  };

  if (typeof window !== "undefined" && window.RaidUIOverlay) {
    window.RaidUIOverlay.registerOverlay(descriptor);
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { descriptor };
  }
})();
