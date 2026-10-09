// player.js: the interactive player (DIRECTION 'The player'). Loads only outside ?export=1; the export never touches this file, and nothing here
// changes what renderFrame(f) draws for a given frame, layout and overlay state.
//
// Transport (HUD plate, merged into the radio band in landscape, its own plate under the band in portrait): play/pause, speed steps
// -- - + ++ over 1, 1.5, 2, 3, 4 (-- to 1, ++ to 4), the current speed shown; keys: space, Left/Right seek 5 film seconds, [ ] speed,
// Home/End. The status bar is a scrubber: era segments shaded, hashmarks from marks.json (hover shows the label, click seeks).
// Audio: the compiled WAV through one AudioBufferSourceNode with playbackRate = speed (no pitch correction: speed 2 sounds an octave up).
// While audio plays the film position is read from the audio clock, pos = (offset + (ctx.currentTime - t0 - outputLatency) * speed) * fps,
// so picture and sound cannot drift apart by construction; the bound is one displayed frame (33.3 ms) plus the uncertainty of the
// reported output latency. Seek and speed change re-anchor the source (a new node at the new offset and rate).
(function () {
  const KW = window.KW, D = KW.D;
  if (new URLSearchParams(location.search).get('export') === '1') return;
  const Q = new URLSearchParams(location.search);
  const LY = KW.LAY, FPS = KW.fps, F = KW.F, SPEEDS = [1, 1.5, 2, 3, 4];
  const FONT = '"JetBrains Mono", monospace';
  const css = `
  html,body{margin:0;padding:0;background:#07090e;overflow:hidden;height:100%;font-family:${FONT}}
  #stage{position:absolute;overflow:hidden}
  #ui{position:absolute;left:0;top:0;transform-origin:0 0;pointer-events:none;color:${KW.C.fg};font:12px ${FONT}}
  #ui *{box-sizing:border-box}
  .tp{position:absolute;display:flex;align-items:center;gap:6px;pointer-events:auto;user-select:none;transition:opacity .3s}
  .tp.ia{background:rgba(11,14,20,.92);border-bottom:1px solid rgba(74,86,112,.55)} .tp.hide{opacity:0;pointer-events:none}
  .tp.plate{background:rgba(11,14,20,.6);border:1px solid rgba(74,86,112,.55)}
  .b{height:22px;min-width:26px;padding:0 6px;border:1px solid rgba(74,86,112,.7);background:rgba(20,26,38,.7);color:${KW.C.fg};font:13px ${FONT};cursor:pointer;display:flex;align-items:center;justify-content:center;border-radius:2px}
  .b:hover{background:rgba(60,72,98,.8)} .b.on{border-color:${KW.C.fg}}
  .lbl{color:${KW.C.fg2};font-size:12px;white-space:nowrap}
  .bar{position:relative;flex:1;height:22px;background:rgba(7,9,14,.55);border:1px solid rgba(74,86,112,.6);cursor:pointer;min-width:60px}
  .seg{position:absolute;top:0;bottom:0} .fill{position:absolute;left:0;top:0;bottom:0;background:rgba(${KW.C.fgRgb},.16)}
  .head{position:absolute;top:-2px;bottom:-2px;width:2px;background:${KW.C.fg}}
  .mk{position:absolute;top:0;bottom:0;width:7px;margin-left:-3px}
  .mk i{position:absolute;left:3px;top:0;bottom:0;width:1px}
  #tip{position:absolute;pointer-events:none;background:rgba(11,14,20,.92);border:1px solid rgba(74,86,112,.8);padding:3px 6px;color:${KW.C.fg};font:12px ${FONT};white-space:nowrap;display:none;z-index:9}
  #aud{display:none}`;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
  const cv = document.getElementById('c');
  const stage = document.createElement('div'); stage.id = 'stage'; document.body.appendChild(stage);
  stage.appendChild(cv);
  const ui = document.createElement('div'); ui.id = 'ui'; stage.appendChild(ui);
  const tip = document.createElement('div'); tip.id = 'tip'; ui.appendChild(tip);
  function place() {
    const w = Math.round(LY.W * LY.css), h = Math.round(LY.H * LY.css);
    stage.style.width = w + 'px'; stage.style.height = h + 'px';
    stage.style.left = Math.max(0, Math.round((window.innerWidth - w) / 2)) + 'px'; stage.style.top = Math.max(0, Math.round((window.innerHeight - h) / 2)) + 'px';
    ui.style.width = LY.W + 'px'; ui.style.height = LY.H + 'px'; ui.style.transform = 'scale(' + LY.css + ')';
  }
  place();
  const el = (cls, parent, txt, tag) => { const e = document.createElement(tag || 'div'); if (cls) e.className = cls; if (txt !== undefined) e.textContent = txt; if (parent) parent.appendChild(e); return e; };

  // ---- state ------------------------------------------------------------------------------------------------------------------
  const H = new URLSearchParams(location.hash.slice(1));
  const S = { pos: Math.max(0, Math.min(F - 1, parseFloat(H.get('f') || Q.get('f') || '0'))), playing: false, si: Math.max(0, Math.min(4, parseInt(H.get('s') || Q.get('s') || '0', 10))), last: null, shown: -1 };
  const tau = KW.tau;
  const dateOf = f => { const [y, m, d] = KW.civil(D.epoch0_days + Math.floor(tau[f] + 1e-9)); return y + '-' + (m < 10 ? '0' : '') + m + '-' + (d < 10 ? '0' : '') + d; };
  KW.dateOf = dateOf;

  // ---- audio ------------------------------------------------------------------------------------------------------------------
  const A = { ctx: null, buf: null, src: null, t0: 0, off: 0, state: 'off', lat: 0, muted: false };
  function audioUrl() {
    if (Q.get('audio') === 'none') return null;
    if (Q.get('audio')) return Q.get('audio');
    return (Q.get('data') || 'kw-data.js').replace(/kw-data\.js$/, 'audio.wav');
  }
  async function loadAudio(arrayBuffer) {
    try {
      A.ctx = A.ctx || new (window.AudioContext || window.webkitAudioContext)();
      A.state = 'decoding'; setAudioLbl();
      A.buf = await A.ctx.decodeAudioData(arrayBuffer);
      A.state = 'ready'; setAudioLbl();
      if (S.playing) audioStart();
    } catch (e) { A.state = 'error'; setAudioLbl(); }
  }
  async function fetchAudio() {
    const u = audioUrl(); if (!u) return;
    A.state = 'loading'; setAudioLbl();
    try { const r = await fetch(u); if (!r.ok) throw new Error(r.status); await loadAudio(await r.arrayBuffer()); }
    catch (e) { A.state = 'pick'; setAudioLbl(); }   // file:// pages cannot fetch: pick audio.wav by hand
  }
  function audioStop() { if (A.src) { try { A.src.onended = null; A.src.stop(); } catch (e) { } A.src.disconnect(); A.src = null; } }
  function audioStart() {
    audioStop();
    if (!A.buf || !A.ctx || A.muted) return;
    const src = A.ctx.createBufferSource(); src.buffer = A.buf; src.playbackRate.value = SPEEDS[S.si];
    src.connect(A.ctx.destination);
    A.off = S.pos / FPS; A.t0 = A.ctx.currentTime; A.lat = (A.ctx.outputLatency || 0) + (A.ctx.baseLatency || 0);
    src.start(0, Math.min(A.off, A.buf.duration - 0.01)); A.src = src;
  }
  const audioClockPos = () => (A.off + (A.ctx.currentTime - A.t0 - A.lat) * SPEEDS[S.si]) * FPS;

  // ---- transport DOM ----------------------------------------------------------------------------------------------------------
  const por = LY.mode === 'portrait';
  const tpWrap = el('tp' + (por ? ' plate' : ''), ui);
  if (LY.ia) {   // information architecture: the transport and the scrubber overlay the timeline's ruler and hide after 3 s without input
    tpWrap.classList.add('ia');
    const R = LY.ia.ruler;
    if (!por) Object.assign(tpWrap.style, { left: '0px', top: R[1] + 'px', width: LY.W + 'px', height: R[3] + 'px', padding: '0 8px' });
    else Object.assign(tpWrap.style, { left: '0px', top: R[1] + 'px', width: LY.W + 'px', height: (R[3] + LY.ia.band[3]) + 'px', flexWrap: 'wrap', padding: '4px 6px', alignContent: 'flex-start', gap: '4px 5px' });
  }
  else if (!por) { Object.assign(tpWrap.style, { left: (LY.left + 8) + 'px', top: (LY.bandY + 5) + 'px', width: (LY.W - LY.left - LY.right - 16) + 'px', height: '24px' }); }
  else { Object.assign(tpWrap.style, { left: '0px', top: (LY.H - LY.tpH) + 'px', width: LY.W + 'px', height: LY.tpH + 'px', flexWrap: 'wrap', padding: '5px 8px', alignContent: 'flex-start', gap: '5px 6px' }); }
  if (LY.ia && !por) st.textContent += '.tp.ia .b{height:20px}.tp.ia .bar{height:18px}';
  const bt = (txt, title, fn) => { const b = el('b', tpWrap, txt, 'button'); b.title = title; b.onclick = e => { fn(); b.blur(); }; return b; };
  const bSlow = bt('--', 'speed 1x', () => setSpeed(0)), bDn = bt('-', 'slower', () => setSpeed(S.si - 1));
  const bPlay = bt('▶', 'play / pause (space)', () => toggle()), bUp = bt('+', 'faster', () => setSpeed(S.si + 1)), bFast = bt('++', 'speed 4x', () => setSpeed(4));
  if (LY.ia && por) bt('\u2261', 'lineage lanes', () => { KW.ui.lanes = !KW.ui.lanes; S.shown = -1; });
  const lSpeed = el('lbl', tpWrap, '1×'); lSpeed.style.minWidth = '34px'; lSpeed.style.textAlign = 'center'; lSpeed.title = 'current speed';
  const lTime = el('lbl', tpWrap, ''); lTime.style.minWidth = '84px';
  const bMute = bt('♪', 'audio', () => { if (A.state === 'pick') pick.click(); else { A.muted = !A.muted; if (A.muted) audioStop(); else if (S.playing) audioStart(); setAudioLbl(); } });
  const pick = el('', tpWrap, undefined, 'input'); pick.type = 'file'; pick.accept = 'audio/*,.wav'; pick.id = 'aud';
  pick.onchange = async () => { if (pick.files[0]) { A.ctx = A.ctx || new (window.AudioContext || window.webkitAudioContext)(); await loadAudio(await pick.files[0].arrayBuffer()); } };
  function setAudioLbl() { bMute.title = 'audio: ' + (A.muted ? 'muted' : A.state) + (A.state === 'pick' ? ' (click to load audio.wav)' : ''); bMute.classList.toggle('on', A.state === 'ready' && !A.muted); bMute.style.opacity = A.state === 'ready' || A.state === 'pick' ? 1 : 0.5; }
  setAudioLbl();
  const bar = el('bar', tpWrap); if (por) { bar.style.flexBasis = '100%'; bar.style.flexGrow = '0'; }
  // era segments
  const sw = D.era_switch_f, edges = [0, sw[0], sw[1], F - 1];
  [0.05, 0.11, 0.19].forEach((a, i) => { const s = el('seg', bar); s.style.left = (100 * edges[i] / (F - 1)) + '%'; s.style.width = (100 * (edges[i + 1] - edges[i]) / (F - 1)) + '%'; s.style.background = 'rgba(160,170,196,' + a + ')'; s.style.borderRight = i < 2 ? '1px solid rgba(' + KW.C.fgRgb + ',.35)' : 'none'; });
  const fill = el('fill', bar), head = el('head', bar);
  const marks = (D.marks || []).slice();
  const mkEls = marks.map(m => { const d = el('mk', bar); d.style.left = (100 * m.frame / (F - 1)) + '%'; const i = el('', d, undefined, 'i'); i.style.background = KW.markColor(m.kind, 0.9); d._m = m; return d; });

  // ---- tooltips -----------------------------------------------------------------------------------------------------------------
  function showTip(text, x, y) {   // logical coordinates of the stage
    tip.textContent = text; tip.style.display = 'block';
    const w = tip.offsetWidth, h = tip.offsetHeight;
    tip.style.left = Math.max(2, Math.min(LY.W - w - 2, x + 10)) + 'px'; tip.style.top = Math.max(2, Math.min(LY.H - h - 2, y - h - 8)) + 'px';
  }
  const hideTip = () => { tip.style.display = 'none'; };
  const logical = e => { const r = stage.getBoundingClientRect(); return { x: (e.clientX - r.left) / LY.css, y: (e.clientY - r.top) / LY.css }; };
  const barFrame = e => { const r = bar.getBoundingClientRect(); return Math.max(0, Math.min(F - 1, Math.round((e.clientX - r.left) / r.width * (F - 1)))); };
  bar.addEventListener('pointermove', e => {
    const r = bar.getBoundingClientRect(), px = e.clientX - r.left;
    let best = null, bd = 6 * LY.css;
    for (const d of mkEls) { const dx = Math.abs(d._m.frame / (F - 1) * r.width - px); if (dx < bd) { bd = dx; best = d._m; } }
    const p = logical(e);
    showTip(best ? dateOf(best.frame) + '  ' + best.label : dateOf(barFrame(e)), p.x, p.y);
  });
  bar.addEventListener('pointerleave', hideTip);
  let dragging = false;
  bar.addEventListener('pointerdown', e => {
    const r = bar.getBoundingClientRect(), px = e.clientX - r.left;
    let best = null, bd = 5 * LY.css;
    for (const d of mkEls) { const dx = Math.abs(d._m.frame / (F - 1) * r.width - px); if (dx < bd) { bd = dx; best = d._m; } }
    seek(best ? best.frame : barFrame(e)); dragging = !best; bar.setPointerCapture(e.pointerId);
  });
  bar.addEventListener('pointermove', e => { if (dragging) seek(barFrame(e)); });
  bar.addEventListener('pointerup', () => { dragging = false; });

  // canvas hover and taps
  function hoverAt(p) {
    const f = Math.floor(S.pos);
    if (KW.streamLaneAt) { const l = KW.streamLaneAt(f, p.x, p.y); if (l) return l.name; }
    for (const r of (KW.nationRows || [])) if (p.x >= r.x && p.x < r.x + r.w && p.y >= r.y && p.y < r.y + r.h) {
      const e = KW.util.i32(D.nat_entry_f)[r.i]; return D.nat_names[r.i] + '  entered ' + dateOf(Math.min(F - 1, e));
    }
    if ((KW.LAY.mode === 'landscape' && !KW.LAY.ia) || KW.ui.surfaces) for (const r of (KW.tallyRows || [])) if (p.x >= 0 && p.x < 240 && p.y >= r.y && p.y < r.y + r.h) return r.name + '  first appeared ' + dateOf(Math.min(F - 1, D.surfaces.entry[r.i]));
    return null;
  }
  cv.addEventListener('pointermove', e => { const p = logical(e), t = hoverAt(p); if (t) showTip(t, p.x, p.y); else hideTip(); });
  cv.addEventListener('pointerleave', hideTip);
  cv.addEventListener('pointerdown', e => {
    const p = logical(e);
    if (LY.mode === 'portrait') {
      const hit = (KW.nationRows || []).find(r => p.x >= r.x && p.x < r.x + r.w && p.y >= r.y && p.y < r.y + r.h && r.y < LY.top);
      const sb = KW.surfBtn;
      if (sb && p.x >= sb.x && p.x < sb.x + sb.w && p.y >= sb.y && p.y < sb.y + sb.h) { KW.ui.surfaces = !KW.ui.surfaces; KW.ui.nations = false; }
      else if (hit) { KW.ui.nations = !KW.ui.nations; KW.ui.surfaces = false; }
      else if (LY.ia && KW.timelineRects && p.y >= KW.timelineRects.band[1] && p.y < KW.timelineRects.band[1] + KW.timelineRects.band[3]) { KW.ui.lanes = !KW.ui.lanes; }   // tap the band: open or fold the lanes
      else if (p.y > LY.top) { KW.ui.nations = false; KW.ui.surfaces = false; }
      S.shown = -1; return;
    }
    const t = hoverAt(p); if (t) showTip(t, p.x, p.y);
  });

  // ---- control ---------------------------------------------------------------------------------------------------------------------
  function paintSpeed() { lSpeed.textContent = SPEEDS[S.si] + '×'; bPlay.textContent = S.playing ? '❚❚' : '▶'; [bSlow, bDn, bUp, bFast].forEach(b => b.classList.remove('on')); }
  function setSpeed(i) {
    i = Math.max(0, Math.min(SPEEDS.length - 1, i));
    if (S.playing && A.src) { S.pos = Math.min(F - 1, A.ctx ? audioClockPos() : S.pos); }
    S.si = i; paintSpeed(); if (S.playing) { S.last = null; audioStart(); }
  }
  function play() {
    if (S.playing) return;
    if (S.pos >= F - 1) S.pos = 0;
    S.playing = true; S.last = null;
    if (A.ctx && A.ctx.state === 'suspended') A.ctx.resume();
    audioStart(); paintSpeed();
  }
  function pause() { if (!S.playing) return; if (A.src && A.ctx) S.pos = Math.max(0, Math.min(F - 1, audioClockPos())); S.playing = false; audioStop(); paintSpeed(); }
  function toggle() { S.playing ? pause() : play(); }
  function seek(f) { S.pos = Math.max(0, Math.min(F - 1, f)); S.last = null; if (S.playing) audioStart(); }
  window.addEventListener('keydown', e => {
    if (e.target && e.target.tagName === 'INPUT') return;
    const k = e.key;
    if (k === ' ') { toggle(); e.preventDefault(); }
    else if (k === 'ArrowLeft') { seek(S.pos - 5 * FPS); e.preventDefault(); }
    else if (k === 'ArrowRight') { seek(S.pos + 5 * FPS); e.preventDefault(); }
    else if (k === '[') setSpeed(S.si - 1);
    else if (k === ']') setSpeed(S.si + 1);
    else if (k === 's' || k === 'S') { KW.ui.surfaces = !KW.ui.surfaces; if (KW.ui.surfaces) KW.ui.nations = false; S.shown = -1; }
    else if (k === 'Home') { seek(0); e.preventDefault(); }
    else if (k === 'End') { seek(F - 1); e.preventDefault(); }
  });
  // chrome auto-hide (ia): visible while the pointer or a key moved within 3 s, or the pointer is over it; fades over 0.3 s (css transition)
  let lastInput = performance.now(), overChrome = false;
  const wake = () => { lastInput = performance.now(); tpWrap.classList.remove('hide'); };
  ['pointermove', 'pointerdown', 'keydown', 'wheel', 'touchstart'].forEach(ev => window.addEventListener(ev, wake, { passive: true }));
  tpWrap.addEventListener('pointerenter', () => { overChrome = true; wake(); }); tpWrap.addEventListener('pointerleave', () => { overChrome = false; lastInput = performance.now(); });
  window.kwChrome = () => ({ hidden: tpWrap.classList.contains('hide'), idle_ms: performance.now() - lastInput });
  // a changed viewport changes the layout: keep the place and reload
  let rt = null;
  window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { const f = Math.floor(S.pos); location.hash = 'f=' + f + '&s=' + S.si; location.reload(); }, 300); });

  // ---- the loop (wall clock only here; the export has its own) -----------------------------------------------------------------------
  let drift = { max: 0, n: 0 };
  function tick(ts) {
    if (S.playing) {
      if (A.src && A.ctx) S.pos = audioClockPos();
      else { if (S.last === null) S.last = ts; S.pos += (ts - S.last) * SPEEDS[S.si] * FPS / 1000; S.last = ts; }
      if (S.pos >= F - 1) { S.pos = F - 1; pause(); }
      if (S.pos < 0) S.pos = 0;
    }
    if (LY.ia && !overChrome && ts - lastInput > 3000 && !tpWrap.classList.contains('hide')) tpWrap.classList.add('hide');
    const f = Math.max(0, Math.min(F - 1, Math.floor(S.pos)));
    if (f !== S.shown) {
      S.shown = f; window.renderFrame(f);
      const pc = 100 * f / (F - 1); head.style.left = pc + '%'; fill.style.width = pc + '%';
      lTime.textContent = dateOf(f);
    }
    requestAnimationFrame(tick);
  }
  KW.startPlayer = function () {
    paintSpeed(); S.shown = -1; fetchAudio(); requestAnimationFrame(tick);
    if (Q.get('play') === '1') play();
  };
  if (window.__ready) KW.startPlayer();   // main.js reached ready before this script ran
  // test and debugging hooks
  window.kwPlayer = {
    play, pause, toggle, seek, setSpeed, state: () => ({ pos: S.pos, playing: S.playing, speed: SPEEDS[S.si], audio: A.state, lat: A.lat, frame: S.shown }),
    audioClockPos: () => (A.ctx && A.src ? audioClockPos() : null), SPEEDS,
  };
})();
