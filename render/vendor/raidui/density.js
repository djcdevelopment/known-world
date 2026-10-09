// density.js — accumulate a 200x200 density grid from trajectory point clouds.
//
// Exports (onto window.RaidUIShape per amendments-phase-4 §3):
//   - buildDensityGrid(pointArrays) ->
//       { cells: Float32Array, width: 200, height: 200, max: number }
//
// Row-major: `cells[row * 200 + col]` where
//   col = floor(x * 200), row = floor(y * 200) for x,y in [0, 1).
// Strict `< 1` gate drops points at exactly (1,1) (off-by-one safety) and
// silently drops out-of-arena (x<0, x>=1, y<0, y>=1) and NaN points.
// Gaussian smoothing deferred per kickoff (add 3x3 box blur if L reports
// blocky raster).

(function (root) {
  const W = 200;
  const H = 200;
  const CELL_COUNT = W * H;

  function buildDensityGrid(pointArrays) {
    const cells = new Float32Array(CELL_COUNT);
    let max = 0;
    if (!pointArrays) {
      return { cells: cells, width: W, height: H, max: 0 };
    }
    // `pointArrays` is an iterable of Float32Arrays (paired floats).
    for (const points of pointArrays) {
      if (!points || points.length < 2) continue;
      const n = points.length;
      for (let i = 0; i + 1 < n; i += 2) {
        const x = points[i];
        const y = points[i + 1];
        // Strict [0, 1) range; NaN fails both comparisons.
        if (!(x >= 0 && x < 1 && y >= 0 && y < 1)) continue;
        const col = Math.floor(x * W);
        const row = Math.floor(y * H);
        const idx = row * W + col;
        const v = cells[idx] + 1;
        cells[idx] = v;
        if (v > max) max = v;
      }
    }
    return { cells: cells, width: W, height: H, max: max };
  }

  const api = { buildDensityGrid };

  if (root && typeof root === "object") {
    root.RaidUIShape = Object.assign(root.RaidUIShape || {}, api);
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : (typeof globalThis !== "undefined" ? globalThis : null));
