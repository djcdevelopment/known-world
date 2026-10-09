// playback-controller.js — shared playback clock for dual <Replay>.
//
// Contract (per track-i-design §3, amendments-phase3 §I):
//   createPlaybackController() -> {
//     timeMs, playing, speed        : { current } mutable refs
//     subscribe(cb) -> unsubscribe  : lazy-start; last-unsub stops RAF
//     setTime(ms)                   : clamped to [0, maxDurationMs]
//     togglePlay()                  : auto-stops at end; restart-from-start if at end
//     setSpeed(multiplier)
//     registerDuration(id, ms)      : tracks min across ids (shared clock cap)
//     unregisterDuration(id)
//     _tick(dtMs)                   : deterministic step for tests
//   }
//
// Back-compat: absent from <Replay> props => hook owns clock (Phase 1 path).
//
// Dual-mode: window.RaidUICompare.createPlaybackController + module.exports.

(function (root) {
  function createPlaybackController() {
    const timeMs = { current: 0 };
    const playing = { current: false };
    const speed = { current: 1 };

    const subscribers = new Set();
    const durations = new Map(); // id -> ms

    let rafId = 0;
    let lastTs = 0;
    let running = false;

    function maxDurationMs() {
      if (durations.size === 0) return Infinity;
      let min = Infinity;
      for (const v of durations.values()) if (v < min) min = v;
      return min;
    }

    function snapshot() {
      return { timeMs: timeMs.current, playing: playing.current, speed: speed.current };
    }

    function notify() {
      const snap = snapshot();
      for (const cb of subscribers) {
        try { cb(snap); } catch (_) { /* swallow — subscriber bug shouldn't kill clock */ }
      }
    }

    function clamp(t) {
      const max = maxDurationMs();
      if (t < 0) return 0;
      if (t > max && max !== Infinity) return max;
      return t;
    }

    function advance(dtMs) {
      if (!playing.current) { notify(); return; }
      let next = timeMs.current + dtMs * speed.current;
      const max = maxDurationMs();
      if (max !== Infinity && next >= max) {
        next = max;
        playing.current = false; // auto-stop at end
      }
      timeMs.current = next;
      notify();
    }

    // Internal RAF loop — canonical clock. Uses browser's rAF when available;
    // otherwise _tick() is the only mover (tests).
    function rafTick(ts) {
      if (!running) return;
      if (!lastTs) lastTs = ts;
      const dt = ts - lastTs;
      lastTs = ts;
      advance(dt);
      if (typeof requestAnimationFrame === 'function') {
        rafId = requestAnimationFrame(rafTick);
      }
    }

    function start() {
      if (running) return;
      running = true;
      lastTs = 0;
      if (typeof requestAnimationFrame === 'function') {
        rafId = requestAnimationFrame(rafTick);
      }
    }

    function stop() {
      running = false;
      lastTs = 0;
      if (rafId && typeof cancelAnimationFrame === 'function') {
        cancelAnimationFrame(rafId);
      }
      rafId = 0;
    }

    function subscribe(cb) {
      if (typeof cb !== 'function') return () => {};
      subscribers.add(cb);
      if (subscribers.size === 1) start();
      // Fire once with current snapshot so the subscriber can initialize.
      try { cb(snapshot()); } catch (_) {}
      let active = true;
      return function unsubscribe() {
        if (!active) return;
        active = false;
        subscribers.delete(cb);
        if (subscribers.size === 0) stop();
      };
    }

    function setTime(ms) {
      const t = clamp(Number(ms) || 0);
      timeMs.current = t;
      notify();
    }

    function togglePlay() {
      const max = maxDurationMs();
      if (!playing.current && max !== Infinity && timeMs.current >= max) {
        // Restart from beginning when toggling play at end-of-clip.
        timeMs.current = 0;
      }
      playing.current = !playing.current;
      notify();
    }

    function setSpeed(multiplier) {
      const m = Number(multiplier);
      if (!isFinite(m) || m <= 0) return;
      speed.current = m;
      notify();
    }

    function registerDuration(id, durationMs) {
      if (!id) return;
      durations.set(String(id), Math.max(0, Number(durationMs) || 0));
      // Re-clamp timeMs under possibly-tighter cap.
      const t = clamp(timeMs.current);
      if (t !== timeMs.current) {
        timeMs.current = t;
        notify();
      }
    }

    function unregisterDuration(id) {
      if (!id) return;
      durations.delete(String(id));
    }

    function _tick(dtMs) {
      advance(Number(dtMs) || 0);
    }

    return {
      timeMs, playing, speed,
      subscribe,
      setTime, togglePlay, setSpeed,
      registerDuration, unregisterDuration,
      _tick,
      // Test-only introspection:
      _subscriberCount: () => subscribers.size,
      _isRunning: () => running,
      _maxDurationMs: maxDurationMs,
    };
  }

  const api = { createPlaybackController };
  if (root && typeof root === 'object') {
    root.RaidUICompare = root.RaidUICompare || {};
    root.RaidUICompare.createPlaybackController = createPlaybackController;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));
