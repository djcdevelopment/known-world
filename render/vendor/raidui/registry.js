// Overlay registry — pure JS, no React, no DOM.
// Consumed by the RAF host (Track B) and the context-panel (Track B/C) via
// listOverlays() + subscribe(). Overlays self-register on module load.
//
// Descriptor shape (ADR-002 §1): { id, name, enabled, zIndex?, render }
//
// Exposed:
//   - registerOverlay(desc)
//   - unregisterOverlay(id)
//   - listOverlays()
//   - setEnabled(id, bool)
//   - subscribe(cb) -> unsubscribe
//
// Dual-loadable: attaches to window.RaidUIOverlay when window exists,
// and exports via module.exports for Node-based unit tests.

(function (root) {
  const overlays = new Map(); // id -> descriptor
  const subscribers = new Set();

  function notify() {
    for (const cb of subscribers) {
      try { cb(); } catch (e) { /* subscriber must not break others */ console.error("[overlay subscriber]", e); }
    }
  }

  function registerOverlay(desc) {
    if (!desc || typeof desc.id !== "string") throw new Error("registerOverlay: id required");
    if (typeof desc.render !== "function") throw new Error("registerOverlay: render() required");
    if (overlays.has(desc.id)) {
      // Idempotent re-register (e.g. HMR / accidental double-include): replace.
      overlays.set(desc.id, normalize(desc));
    } else {
      overlays.set(desc.id, normalize(desc));
    }
    notify();
  }

  function normalize(desc) {
    return {
      id: desc.id,
      name: typeof desc.name === "string" ? desc.name : desc.id,
      enabled: desc.enabled !== false,
      zIndex: typeof desc.zIndex === "number" ? desc.zIndex : 0,
      render: desc.render,
    };
  }

  function unregisterOverlay(id) {
    if (overlays.delete(id)) notify();
  }

  function listOverlays() {
    // Host iterates every frame; return a plain array snapshot in insertion order.
    // Host is responsible for filtering by enabled + sorting by zIndex.
    return Array.from(overlays.values());
  }

  function setEnabled(id, enabled) {
    const o = overlays.get(id);
    if (!o) return;
    const want = !!enabled;
    if (o.enabled === want) return;
    o.enabled = want;
    notify();
  }

  function subscribe(cb) {
    if (typeof cb !== "function") throw new Error("subscribe: cb must be a function");
    subscribers.add(cb);
    return function unsubscribe() { subscribers.delete(cb); };
  }

  const api = { registerOverlay, unregisterOverlay, listOverlays, setEnabled, subscribe };

  if (root && typeof root === "object") {
    root.RaidUIOverlay = Object.assign(root.RaidUIOverlay || {}, api);
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : (typeof globalThis !== "undefined" ? globalThis : null));
