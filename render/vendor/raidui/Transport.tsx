import { useEffect, useRef, type MutableRefObject } from 'react';
import { Ico } from './Icons';
import { fmtTime } from './spatial';

export interface TransportEvent {
  t: number;
  kind: 'death' | 'spike' | 'info';
  label: string;
}

export interface Inflection {
  start: number;
  end: number;
}

interface Props {
  /** Throttled React-state time. Used as the initial render value and as
   *  a fallback when the RAF subscription isn't wired. */
  time: number;
  duration: number;
  paused: boolean;
  onTogglePlay: () => void;
  onSeek: (t: number) => void;
  onStep: (delta: number) => void;
  speed: number;
  setSpeed: (s: number) => void;
  events?: TransportEvent[];
  inflection?: Inflection | null;
  /** Live timeRef from useRafPlayback. When provided alongside addDraw, the
   *  playhead position + time-display text update at canvas frequency
   *  (60Hz) via direct DOM mutation, bypassing React rerenders for the
   *  high-frequency surfaces. */
  timeRef?: MutableRefObject<number>;
  /** Subscribe a draw callback to the parent's RAF loop. Called every
   *  frame with the current timeRef value. */
  addDraw?: (fn: (timeSec: number) => void) => () => void;
}

const SPEEDS = [0.5, 1, 2] as const;

export function Transport({
  time, duration, paused, onTogglePlay, onSeek, onStep,
  speed, setSpeed, events = [], inflection = null,
  timeRef, addDraw,
}: Props) {
  const barRef = useRef<HTMLDivElement>(null);
  const playheadRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const timeTextRef = useRef<HTMLDivElement>(null);

  function handleBarClick(e: React.MouseEvent<HTMLDivElement>) {
    const rect = barRef.current?.getBoundingClientRect();
    if (!rect) return;
    const t = ((e.clientX - rect.left) / rect.width) * duration;
    onSeek(t);
  }

  // RAF subscription — when the parent passes addDraw + timeRef, mutate
  // playhead + progress + time text directly from inside the loop. Bypasses
  // React state for the 60Hz surfaces; the speed selector, paused state,
  // events list etc. stay reactive because they only change on user action.
  useEffect(() => {
    if (!addDraw || !timeRef) return;
    const unsub = addDraw((t) => {
      const pct = duration > 0 ? Math.max(0, Math.min(100, (t / duration) * 100)) : 0;
      if (playheadRef.current) playheadRef.current.style.left = `calc(${pct}% - 6px)`;
      if (progressRef.current) progressRef.current.style.width = `${pct}%`;
      if (timeTextRef.current) {
        // Avoid React's sanitizer overhead — just write the string.
        timeTextRef.current.textContent = `${fmtTime(t)} / ${fmtTime(duration)}`;
      }
    });
    return unsub;
  }, [addDraw, timeRef, duration]);

  const initialPct = duration > 0 ? (time / duration) * 100 : 0;

  return (
    <div
      style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '10px 12px', background: 'var(--panel)',
        border: '1px solid var(--line)', borderRadius: 8,
      }}
    >
      <button className="btn ghost btn-icon" onClick={() => onStep(-5)} title="-5s"><Ico.rewind /></button>
      <button className="btn primary btn-icon" onClick={onTogglePlay} title="Space">
        {paused ? <Ico.play /> : <Ico.pause />}
      </button>
      <button className="btn ghost btn-icon" onClick={() => onStep(5)} title="+5s"><Ico.fwd /></button>

      <div
        ref={timeTextRef}
        className="mono tabular"
        style={{ fontSize: 12, minWidth: 74, color: 'var(--ink-2)' }}
      >
        {fmtTime(time)} / {fmtTime(duration)}
      </div>

      <div ref={barRef} onClick={handleBarClick} style={{ flex: 1, height: 30, position: 'relative', cursor: 'pointer' }}>
        {/* base bar */}
        <div style={{ position: 'absolute', top: 14, left: 0, right: 0, height: 2, background: 'var(--line)', borderRadius: 1 }} />
        {/* inflection band */}
        {inflection && (
          <div
            style={{
              position: 'absolute', top: 10,
              left: `${(inflection.start / duration) * 100}%`,
              width: `${((inflection.end - inflection.start) / duration) * 100}%`,
              height: 10, background: 'rgba(245,180,97,0.18)', borderRadius: 2,
            }}
          />
        )}
        {/* events */}
        {events.map((ev, i) => (
          <div
            key={i}
            title={ev.label}
            style={{
              position: 'absolute',
              top: ev.kind === 'death' ? 6 : 18,
              left: `calc(${(ev.t / duration) * 100}% - 3px)`,
              width: 6, height: 6, borderRadius: '50%',
              background:
                ev.kind === 'death' ? 'var(--wipe)' :
                ev.kind === 'spike' ? 'var(--warn)' : 'var(--info)',
            }}
          />
        ))}
        {/* progress — initial width from React state, then mutated each
            RAF frame when subscribed. */}
        <div
          ref={progressRef}
          style={{
            position: 'absolute', top: 14, left: 0,
            width: `${initialPct}%`,
            height: 2, background: 'var(--accent)', borderRadius: 1,
          }}
        />
        {/* playhead — initial position from React state, then mutated each
            RAF frame when subscribed. */}
        <div
          ref={playheadRef}
          style={{
            position: 'absolute', top: 8,
            left: `calc(${initialPct}% - 6px)`,
            width: 12, height: 14, background: 'var(--accent)',
            borderRadius: 2, boxShadow: '0 0 8px var(--accent-glow)',
          }}
        />
      </div>

      <div className="segmented">
        {SPEEDS.map((s) => (
          <button key={s} className={speed === s ? 'on' : ''} onClick={() => setSpeed(s)}>
            {s}×
          </button>
        ))}
      </div>

      <span className="chip" style={{ fontSize: 10 }}>
        <Ico.kbd /> Space · ← → · Esc
      </span>
    </div>
  );
}
