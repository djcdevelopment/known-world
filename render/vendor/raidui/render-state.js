// RenderState builder — pure function from (PullReplay + playback state) to
// the RenderState object overlays consume. Invoked by Track B's host each frame.
// Shape locked by ADR-002 §2.
//
// The host SHOULD reuse the returned object (or at least its scratch buffers)
// across frames to avoid allocation in the RAF hot path. This builder accepts
// an optional `out` parameter for that reuse pattern.

(function (root) {
  // Reusable scratch object returned by frameLookup; caller MUST read
  // immediately and MUST NOT retain across frames (ADR-002 §2).
  function makeFrameLookup(frames, frameStepMs) {
    const scratch = { a: null, b: null, alpha: 0, fi: 0 };
    const last = frames.length - 1;
    return function frameLookup(t) {
      let fi = Math.floor(t / frameStepMs);
      if (fi < 0) fi = 0;
      if (fi > last) fi = last;
      const a = frames[fi];
      const b = frames[fi + 1 < frames.length ? fi + 1 : last];
      // Alpha uses actual frame timestamps so irregular spacing still interpolates.
      const span = (b.t - a.t) || frameStepMs || 1;
      let alpha = (t - a.t) / span;
      if (alpha < 0) alpha = 0; else if (alpha > 1) alpha = 1;
      scratch.a = a;
      scratch.b = b;
      scratch.alpha = alpha;
      scratch.fi = fi;
      return scratch;
    };
  }

  // Per-pull cached interpolation buffers so the host doesn't re-allocate.
  // Keyed by pullReplay identity via WeakMap.
  const bufferCache = new WeakMap();

  function buffersFor(pullReplay) {
    let buf = bufferCache.get(pullReplay);
    if (buf) return buf;
    const n = pullReplay.entities.length;
    buf = {
      positions: new Float32Array(n * 2),
      // hp allocated lazily only when a frame carries entityHp
      hp: null,
      hasHp: false,
      frameLookup: makeFrameLookup(pullReplay.frames, pullReplay.frameStepMs),
    };
    bufferCache.set(pullReplay, buf);
    return buf;
  }

  function computeInterpolated(pullReplay, currentTimeMs, buf) {
    const lookup = buf.frameLookup(currentTimeMs);
    const { a, b, alpha } = lookup;
    const n = pullReplay.entities.length;
    const positions = buf.positions;
    const ap = a.entityPositions;
    const bp = b.entityPositions;
    for (let i = 0; i < n; i++) {
      const k = i * 2;
      const ax = ap[k];
      const ay = ap[k + 1];
      positions[k] = ax + (bp[k] - ax) * alpha;
      positions[k + 1] = ay + (bp[k + 1] - ay) * alpha;
    }

    // HP is optional per contract.
    const ahp = a.entityHp;
    const bhp = b.entityHp;
    if (ahp && bhp) {
      if (!buf.hp || buf.hp.length !== n) buf.hp = new Float32Array(n);
      for (let i = 0; i < n; i++) {
        buf.hp[i] = ahp[i] + (bhp[i] - ahp[i]) * alpha;
      }
      buf.hasHp = true;
    } else {
      buf.hasHp = false;
    }

    return lookup;
  }

  /**
   * Build RenderState for the current frame.
   *
   * @param {Object} args
   * @param {Object} args.pullReplay          PullReplay (frame.schema.json)
   * @param {number} args.currentTimeMs       playback cursor in ms
   * @param {string|null} args.selectedEntityId
   * @param {{w:number,h:number}} args.canvasSize
   * @param {{x0:number,y0:number,size:number}} args.arenaRect
   * @param {Object} [out]                     optional reusable RenderState object
   * @returns {Object} RenderState
   */
  function buildRenderState(args, out) {
    const {
      pullReplay,
      currentTimeMs,
      selectedEntityId,
      canvasSize,
      arenaRect,
    } = args;

    const buf = buffersFor(pullReplay);
    computeInterpolated(pullReplay, currentTimeMs, buf);

    const state = out || {};
    state.pullReplay = pullReplay;
    state.currentTimeMs = currentTimeMs;
    state.selectedEntityId = selectedEntityId == null ? null : selectedEntityId;
    state.canvasSize = canvasSize;
    state.arenaRect = arenaRect;
    state.entities = pullReplay.entities;
    state.interpolatedPositions = buf.positions;
    state.interpolatedHp = buf.hasHp ? buf.hp : null;
    state.frameLookup = buf.frameLookup;
    return state;
  }

  const api = { buildRenderState };

  if (root && typeof root === "object") {
    root.RaidUIOverlay = Object.assign(root.RaidUIOverlay || {}, api);
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : (typeof globalThis !== "undefined" ? globalThis : null));
