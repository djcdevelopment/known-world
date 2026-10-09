// palette.js — role-bucket oklch palette for Shape's long-exposure view.
//
// Exports (onto window.RaidUIShape per amendments-phase-4 §3):
//   - paletteFor({ role, participantId, classSpec? }) -> oklch string
//   - normalizeRole(rawRole) -> 'Tank' | 'Healer' | 'Melee' | 'Ranged'
//
// Role normalization lives here per amendments §8:
//   MeleeDps  -> Melee
//   RangedDps -> Ranged
//   canonical -> passthrough
//   unknown   -> Ranged (defensive, amendments §9) with NODE_ENV!=='production'
//                console.warn to surface frequent firing.
//
// Palette stability: (role, participantId [, classSpec]) -> same oklch string.
// Hue jittered ±10° within bucket via djb2 hash on participantId (folded with
// classSpec when present, for intra-role differentiation).

(function (root) {
  const ROLE_BASE = {
    Tank:   { L: 0.65, C: 0.15, H: 40  },
    Healer: { L: 0.70, C: 0.12, H: 150 },
    Melee:  { L: 0.60, C: 0.18, H: 25  },
    Ranged: { L: 0.60, C: 0.18, H: 300 },
  };
  const JITTER_DEG = 10;

  const CANONICAL_ROLES = new Set(["Tank", "Healer", "Melee", "Ranged"]);

  function normalizeRole(rawRole) {
    if (rawRole === "MeleeDps") return "Melee";
    if (rawRole === "RangedDps") return "Ranged";
    if (typeof rawRole === "string" && CANONICAL_ROLES.has(rawRole)) return rawRole;
    // Defensive fallback — amendments §9.
    if (typeof process !== "undefined" &&
        process.env &&
        process.env.NODE_ENV !== "production" &&
        typeof console !== "undefined" && console.warn) {
      console.warn("[RaidUIShape] normalizeRole: unknown role", rawRole, "-> Ranged");
    }
    return "Ranged";
  }

  // djb2 (Bernstein) over UTF-16 code units; folded unsigned 32-bit.
  function hashDjb2(str) {
    let h = 5381;
    for (let i = 0; i < str.length; i++) {
      h = (((h << 5) + h) + str.charCodeAt(i)) | 0;
    }
    return h >>> 0;
  }

  function paletteFor(args) {
    const role = (args && args.role) || "Ranged";
    const participantId = (args && args.participantId) || "";
    const classSpec = args && args.classSpec ? args.classSpec : null;

    const base = ROLE_BASE[role] || ROLE_BASE.Ranged;

    const key = classSpec ? (participantId + "|" + classSpec) : participantId;
    const bits = hashDjb2(key);
    const unit = (bits % 10000) / 10000;       // [0, 1)
    const hOffset = (unit * 2 - 1) * JITTER_DEG; // [-10, +10]
    const H = base.H + hOffset;
    const Lpct = Math.round(base.L * 1000) / 10; // 1 decimal, e.g. 65.0
    // C to 3 decimals for determinism across runs.
    const Cstr = base.C.toFixed(3);
    // H to 3 decimals.
    const Hstr = H.toFixed(3);
    return "oklch(" + Lpct + "% " + Cstr + " " + Hstr + ")";
  }

  const api = { paletteFor, normalizeRole };

  if (root && typeof root === "object") {
    root.RaidUIShape = Object.assign(root.RaidUIShape || {}, api);
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : (typeof globalThis !== "undefined" ? globalThis : null));
