// system.js: the ONE constants module. Values copied from design/known-world-design-system/tokens.json (Known World design system, artifact 1791572259-1d3e).
// Colours, layout sizes, type sizes and opacities the render code reads under layout ia live here and nowhere else; accent (amber) is board-only
// and is deliberately absent: it never appears inside the frame.
window.KW_SYS = {
  color: { canvas: '#07090e', sea: '#0c111b', line: '#263044', frameLine: '#2b3650', fg: '#e8edf6', fg2: '#9aa7bb', muted: '#66748c', frameMuted: '#7d8aa3',
           dim: '#2a3346', land: '#3b4a66', landDim: '#1f2838' },
  nation: { human: '#e3d3b4', chatgpt: '#26bf7c', claude: '#ff7a59', codex: '#3b8cf5', automation: '#e062c4', local_model: '#e2ef6a', opencode: '#c4b0ff' },
  surface: { 'omen-c': '#8d96a6', 'omen-e': '#5f7fb5', 'omen-linux': '#86915a', am4: '#a5809e', fx99: '#a8876a', github: '#6f9585' },
  layout: { tickerH: 64, tickerHTotals: 84, nationsW: 320, nationRow: 136, nationRowDense: 96, timelineH: 200, rulerH: 24, bandH: 60, laneH: 11,
            pTickerH: 64, pStripH: 44, pTimelineH: 84, pTimelineOpen: 200, pMapMin: 448, pFrameW: 1080, pFrameH: 1920 },
  type: { ticker: 44, tickerP: 32, count: 30, countP: 28, label: 11, chip: 12 },
  opacity: { bloomHalo: 0.18, bloomCore: 0.6, beam: 0.5 },
};
