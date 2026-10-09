/**
 * RAF-driven playback timing — TS port of src/replay/hooks/useRafPlayback.js.
 *
 * Architecture is intentionally identical to the legacy engine:
 *   • one requestAnimationFrame loop is the sole timing source
 *   • dt comes from real RAF timestamps; time advances by dt × speed
 *   • timeRef / playingRef / speedRef hold the live values; React state
 *     is the throttled (~10Hz) view used to drive UI
 *   • registered canvas draws fan out from the RAF tick — they redraw on
 *     every frame regardless of pause state so scrub stays smooth
 *   • the hot path allocates nothing
 */
import { useCallback, useEffect, useRef, useState } from 'react';

type DrawFn = (timeSec: number) => void;

interface Args {
  /** Total pull duration in seconds. */
  durationSec: number;
  /** Initial time in seconds (default 0). */
  initialTimeSec?: number;
}

interface Return {
  /** Mutable, written by the RAF loop. Canvases read this for paint. */
  timeRef: React.MutableRefObject<number>;
  /** Throttled React-state copy of timeRef. UI source-of-truth. */
  time: number;

  playing: boolean;
  togglePlay: () => void;
  setPlaying: React.Dispatch<React.SetStateAction<boolean>>;

  speed: number;
  setSpeed: React.Dispatch<React.SetStateAction<number>>;

  /** Set absolute time (clamped). Pauses playback to match legacy semantics. */
  seek: (t: number) => void;
  /** Relative seek; does not pause. */
  step: (delta: number) => void;
  /** Set time without pausing — used by the playback loop end-of-pull check. */
  setTimeImmediate: (t: number) => void;

  /** Register a draw callback to fire every RAF tick. Returns unsubscribe. */
  addDraw: (fn: DrawFn) => () => void;
}

export function useRafPlayback({ durationSec, initialTimeSec = 0 }: Args): Return {
  const [playing, setPlaying] = useState(false);
  const [time, setTimeState] = useState(initialTimeSec);
  const [speed, setSpeed] = useState(1);

  const timeRef = useRef(initialTimeSec);
  const playingRef = useRef(false);
  const speedRef = useRef(1);
  const durationRef = useRef(durationSec);

  // Single shared draw set. The RAF tick iterates this every frame; subscribers
  // come and go via addDraw without remounting the loop.
  const drawsRef = useRef<Set<DrawFn>>(new Set());

  const rafRef = useRef(0);
  const lastTsRef = useRef(0);
  const lastSyncRef = useRef(0);

  // Mirror reactive state into refs so the RAF loop reads current values
  // without rebuilding its closure.
  useEffect(() => { playingRef.current = playing; }, [playing]);
  useEffect(() => { speedRef.current = speed; }, [speed]);
  useEffect(() => { durationRef.current = durationSec; }, [durationSec]);

  const togglePlay = useCallback(() => setPlaying((p) => !p), []);

  const setTimeImmediate = useCallback((t: number) => {
    const c = Math.max(0, Math.min(durationRef.current, t));
    timeRef.current = c;
    setTimeState(c);
  }, []);

  const seek = useCallback((t: number) => {
    const c = Math.max(0, Math.min(durationRef.current, t));
    timeRef.current = c;
    playingRef.current = false;
    setPlaying(false);
    setTimeState(c);
  }, []);

  const step = useCallback((delta: number) => {
    const c = Math.max(0, Math.min(durationRef.current, timeRef.current + delta));
    timeRef.current = c;
    setTimeState(c);
  }, []);

  const addDraw = useCallback((fn: DrawFn) => {
    drawsRef.current.add(fn);
    return () => {
      drawsRef.current.delete(fn);
    };
  }, []);

  // RAF loop — single source of playback timing. Drives time advancement
  // (when playing), throttled state sync (~10Hz), and draw fan-out (every tick).
  useEffect(() => {
    function tick(ts: number) {
      if (!lastTsRef.current) lastTsRef.current = ts;
      const dt = (ts - lastTsRef.current) / 1000;
      lastTsRef.current = ts;

      if (playingRef.current) {
        let next = timeRef.current + dt * speedRef.current;
        if (next >= durationRef.current) {
          next = durationRef.current;
          playingRef.current = false;
          setPlaying(false);
        }
        timeRef.current = next;

        // Throttle React state sync to ~10Hz so UI components (Transport
        // playhead, classifier text) don't trigger 60Hz rerender storms.
        if (ts - lastSyncRef.current > 100) {
          lastSyncRef.current = ts;
          setTimeState(next);
        }
      }

      // Draw fan-out — every frame, even paused. Uses Set.forEach which is
      // allocation-free for our small subscriber count (1–2 canvases).
      const t = timeRef.current;
      drawsRef.current.forEach((fn) => fn(t));

      rafRef.current = requestAnimationFrame(tick);
    }
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(rafRef.current);
      lastTsRef.current = 0;
    };
  }, []);

  return {
    timeRef, time,
    playing, togglePlay, setPlaying,
    speed, setSpeed,
    seek, step, setTimeImmediate,
    addDraw,
  };
}
