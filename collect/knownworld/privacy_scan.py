#!/usr/bin/env python3
"""privacy_scan.py <dir|file>: exit 0 clean, 1 violations, 2 usage. Prints counts only, never a value.

events.ndjson and repos.ndjson are validated against allowlists.py; manifest.json against the manifest key set;
every JSON value additionally goes through the generic scan (forbidden keys at any depth, strings over 120
characters, e-mail shapes, secret shapes). run.log and card.md are text-scanned. Anything else is counted as
'unscanned'.
"""
import json
import os
import re
import sys
from collections import Counter

sys.dont_write_bytecode = True  # -I ignores PYTHONDONTWRITEBYTECODE
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from knownworld import allowlists as A  # noqa: E402

TEXT_LINE_MAX = 400


def scan_text(path, viol, stats):
    with open(path, "rb") as f:
        for i, raw in enumerate(f):
            line = raw.decode("utf-8", "replace").rstrip("\n")
            stats["lines"] += 1
            if len(line) > TEXT_LINE_MAX:
                viol[("text", "long_line")] += 1
            if A.EMAIL_RE.search(line):
                viol[("text", "email")] += 1
            if any(rx.search(line) for rx in A.SECRET_RES):
                viol[("text", "secret_shape")] += 1
            if re.match(r'^\s*\{\s*"', line):
                viol[("text", "json_object_line")] += 1


def scan_ndjson(path, kind, viol, stats):
    with open(path, "rb") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            stats["records"] += 1
            try:
                rec = json.loads(raw)
            except ValueError:
                viol[(kind, "json_decode")] += 1
                continue
            if kind == "events":
                errs = A.validate_event(rec)
                src = rec.get("src", "?") if isinstance(rec, dict) else "?"
            elif kind == "repos":
                errs = A.validate_repo(rec)
                src = "repos"
            else:
                errs, src = [], kind
            errs = errs + A.scan_value(rec)
            for e in errs:
                viol[(str(src)[:24], e)] += 1


def scan_file(path, viol, stats):
    base = os.path.basename(path)
    if base.endswith(".ndjson"):
        kind = "events" if base.startswith("events") else "repos" if base.startswith("repos") else "other"
        scan_ndjson(path, kind, viol, stats)
        stats["files"] += 1
    elif base.endswith(".json"):
        try:
            with open(path, "rb") as f:
                data = json.load(f)
        except ValueError:
            viol[(base[:24], "json_decode")] += 1
            return
        errs = A.scan_value(data)
        if base == "manifest.json":
            errs += A.validate_manifest(data)
        for e in errs:
            viol[(base[:24], e)] += 1
        stats["files"] += 1
        stats["records"] += 1
    elif base.endswith(".log") or base.endswith(".md"):
        scan_text(path, viol, stats)
        stats["files"] += 1
    else:
        stats["unscanned"] += 1


def main(argv):
    if len(argv) != 2:
        print("usage: privacy_scan.py <dir|file>")
        return 2
    target = argv[1]
    viol, stats = Counter(), Counter()
    if os.path.isdir(target):
        for dp, dn, fn in os.walk(target):
            dn.sort()
            for n in sorted(fn):
                if n.startswith(".") or n.endswith(".lock"):
                    continue
                scan_file(os.path.join(dp, n), viol, stats)
    elif os.path.isfile(target):
        scan_file(target, viol, stats)
    else:
        print("no such target")
        return 2
    print("scanned_files=%d records=%d text_lines=%d unscanned=%d violations=%d" % (
        stats["files"], stats["records"], stats["lines"], stats["unscanned"], sum(viol.values())))
    for (src, code), n in sorted(viol.items(), key=lambda kv: -kv[1])[:40]:
        print("violation src=%s code=%s count=%d" % (src, code, n))
    return 0 if not viol else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
