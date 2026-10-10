#!/usr/bin/env python3
"""Inspect explicitly listed source schemas; emit no source data values.

SQLite: table/column types and row counts, never blobs or message columns.
JSON/JSONL: bounded structural keys/types only; never string values.
Only task-authored paths under approved source roots are accepted.
"""
import argparse
import collections
import json
from pathlib import Path
import re
import sqlite3
import time
from urllib.parse import quote

from discover import excluded, validate_output

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")
NO_DESCEND = {"content", "text", "prompt", "messages", "message", "arguments", "args_preview", "output",
              "input", "response", "reasoning", "error", "note", "notes", "body", "title", "instructions"}
SECRET_KEYS = {"api_key", "access_token", "refresh_token", "password", "secret", "credentials", "authorization", "auth"}


def shape(obj, depth=0):
    if depth >= 3:
        return type(obj).__name__
    if isinstance(obj, dict):
        return {k: (type(v).__name__ if k.lower() in NO_DESCEND else shape(v, depth + 1))
                for k, v in list(obj.items())[:100] if IDENT.fullmatch(k) and k.lower() not in SECRET_KEYS}
    if isinstance(obj, list):
        return {"type": "list", "sample_shape": shape(obj[0], depth + 1) if obj else None}
    return type(obj).__name__


def probe(spec, approved_roots):
    path = Path(spec["path"]).expanduser()
    result = {"id": spec["id"], "path": str(path), "status": "complete", "limitations": []}
    if path.is_symlink() or path.resolve() != path.absolute() or excluded(str(path)):
        return dict(result, status="refused", limitations=["excluded_or_symlink_path"])
    if not any(path.is_relative_to(r) for r in approved_roots):
        return dict(result, status="refused", limitations=["outside_source_roots"])
    try:
        if path.suffix in (".db", ".sqlite", ".sqlite3"):
            stop = time.monotonic() + 3
            con = sqlite3.connect("file:" + quote(str(path)) + "?mode=ro&immutable=1", uri=True, timeout=1)
            try:
                con.execute("PRAGMA query_only=ON")
                con.set_progress_handler(lambda: int(time.monotonic() > stop), 10000)
                tables = []
                for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name LIMIT 100").fetchall():
                    if not IDENT.fullmatch(name):
                        continue
                    cols = [{"name": row[1], "type": row[2]} for row in con.execute('PRAGMA table_info("' + name + '")')
                            if IDENT.fullmatch(row[1]) and IDENT.fullmatch(row[2] or "unknown")]
                    tables.append({"name": name, "columns": cols,
                                   "rows": con.execute('SELECT COUNT(*) FROM "' + name + '"').fetchone()[0]})
                result["tables"] = tables
                result["wal_present"] = Path(str(path) + "-wal").exists()
                result["limitations"].append("Immutable read: WAL rows may be omitted; no data values or BLOBs selected")
            finally:
                con.close()
        elif path.suffix in (".json", ".jsonl", ".ndjson"):
            # The parser sees bytes, but no scalar source value is selected/emitted.
            with path.open("rb") as f:
                raw = f.readline(262145) if path.suffix != ".json" else f.read(262145)
            if len(raw) > 262144:
                return dict(result, status="partial", limitations=["structural_probe_size_cap"])
            result["shape"] = shape(json.loads(raw))
            result["limitations"].append("Shape of first JSONL record or one bounded JSON file only; no scalar values emitted")
        else:
            return dict(result, status="refused", limitations=["unsupported_format"])
    except (OSError, ValueError, sqlite3.Error) as exc:
        result.update(status="failed", error_type=type(exc).__name__)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sources", type=Path, required=True)
    ap.add_argument("--roots", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    validate_output(args.out)
    roots = [Path(s["path"]).expanduser() for s in json.loads(args.roots.read_text())["sources"] if not s.get("ssh")]
    results = [probe(s, roots) for s in json.loads(args.sources.read_text())["probes"]]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"version": 1, "probes": results}, indent=2) + "\n")
    print(json.dumps({"probes": len(results), "status": dict(collections.Counter(r["status"] for r in results))}))


if __name__ == "__main__":
    main()
