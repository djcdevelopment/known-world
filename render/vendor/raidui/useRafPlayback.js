// useRafPlayback — requestAnimationFrame loop using refs for playback state.
// Draws every tick (even when paused, so scrub is live). Calls draw(timeMs)
// each frame and throttles React state sync to ~100ms while playing.

(function () {
  const { useEffect, useRef, useState, useCallback } = React;

  function useRafPlayback({ durationMs, onTimeChange, controller }) {
    const [playing, setPlaying] = useState(false);
    const [timeMs, setTimeMsState] = useState(0);
    const [speed, setSpeed] = useState(1);

    const playingRef = useRef(false);
    const timeRef = useRef(0);
    const speedRef = useRef(1);
    const rafRef = useRef(0);
    const lastTsRef = useRef(0);
    const drawRef = useRef(null);
    const lastSyncRef = useRef(0);
    const onTimeChangeRef = useRef(onTimeChange);

    useEffect(() => { playingRef.current = playing; }, [playing]);
    useEffect(() => { speedRef.current = speed; }, [speed]);
    useEffect(() => { onTimeChangeRef.current = onTimeChange; }, [onTimeChange]);

    // Follower-mode setters: when a controller is present, all state mutations
    // route through the shared clock so both <Replay> instances stay in sync.
    // Without a controller, behavior is byte-identical to Phase 1.
    const setTimeMs = useCallback((t) => {
      if (controller) {
        controller.setTime(t);
        return;
      }
      const clamped = Math.max(0, Math.min(durationMs, t));
      timeRef.current = clamped;
      setTimeMsState(clamped);
      if (onTimeChangeRef.current) onTimeChangeRef.current(clamped);
    }, [durationMs, controller]);

    const seek = useCallback((t) => {
      if (controller) {
        // Seek = pause + setTime, matching Phase-1 semantics. togglePlay()
        // is idempotent-ish; we only force-pause if currently playing.
        if (controller.playing.current) controller.togglePlay();
        controller.setTime(t);
        return;
      }
      playingRef.current = false;
      setPlaying(false);
      setTimeMs(t);
    }, [setTimeMs, controller]);

    const togglePlay = useCallback(() => {
      if (controller) {
        controller.togglePlay();
        return;
      }
      setPlaying((p) => !p);
    }, [controller]);

    const setDraw = useCallback((fn) => {
      drawRef.current = fn;
    }, []);

    // Proxy setSpeed: route through controller when present so both instances
    // receive the speed change.
    const setSpeedProxy = useCallback((s) => {
      if (controller) { controller.setSpeed(s); return; }
      setSpeed(s);
    }, [controller]);

    // Subscribe to the controller once per controller identity. Mirrors
    // controller state into local refs + React state (throttled).
    useEffect(() => {
      if (!controller) return;
      let lastSync = 0;
      const unsub = controller.subscribe((snap) => {
        timeRef.current = snap.timeMs;
        playingRef.current = snap.playing;
        speedRef.current = snap.speed;
        const now = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
        if (now - lastSync > 100 || snap.playing === false) {
          lastSync = now;
          setTimeMsState(snap.timeMs);
          setPlaying(snap.playing);
          setSpeed(snap.speed);
          if (onTimeChangeRef.current) onTimeChangeRef.current(snap.timeMs);
        }
      });
      return unsub;
    }, [controller]);

    useEffect(() => {
      function tick(ts) {
        if (!lastTsRef.current) lastTsRef.current = ts;
        const dt = ts - lastTsRef.current;
        lastTsRef.current = ts;

        if (controller) {
          // Follower mode: do NOT advance timeRef locally. The controller's
          // own RAF mutates the shared refs; we just draw from whatever
          // timeRef currently reads.
          timeRef.current = controller.timeMs.current;
        } else if (playingRef.current) {
          let next = timeRef.current + dt * speedRef.current;
          if (next >= durationMs) {
            next = durationMs;
            playingRef.current = false;
            setPlaying(false);
          }
          timeRef.current = next;

          // Throttle React sync to ~100ms
          if (ts - lastSyncRef.current > 100) {
            lastSyncRef.current = ts;
            setTimeMsState(next);
            if (onTimeChangeRef.current) onTimeChangeRef.current(next);
          }
        }

        if (drawRef.current) drawRef.current(timeRef.current);
        rafRef.current = requestAnimationFrame(tick);
      }
      rafRef.current = requestAnimationFrame(tick);
      return () => {
        cancelAnimationFrame(rafRef.current);
        lastTsRef.current = 0;
      };
    }, [durationMs, controller]);

    return {
      playing, setPlaying, togglePlay,
      timeMs, setTimeMs, seek,
      speed, setSpeed: setSpeedProxy,
      setDraw,
      timeRef, speedRef, playingRef,
    };
  }

  window.RaidUIReplay = window.RaidUIReplay || {};
  window.RaidUIReplay.useRafPlayback = useRafPlayback;
})();
