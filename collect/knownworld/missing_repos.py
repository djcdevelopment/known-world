#!/usr/bin/env python3
"""missing_repos.py: GitHub repositories that no local remote names.

Reads every corpus/raw/*/repos.ndjson (normalising remotes: userinfo stripped, scp form to https, .git removed,
lower-cased) and corpus/raw/github-list/github_repos.json, and prints a JSON list of {name, url, fork, size_kb} for
the GitHub repos with no matching local remote. Counts go to stderr. Private repos are included once the list was
fetched authenticated.
"""
import glob
import json
import os
import re
import sys

sys.dont_write_bytecode = True  # -I ignores PYTHONDONTWRITEBYTECODE
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from knownworld import core  # noqa: E402


def key(url):
    u = core.norm_remote(url or "")
    if not u:
        return None
    m = re.match(r"^https?://(?:www\.)?github\.com/([^/]+)/([^/]+)", u, re.I)
    return ("%s/%s" % (m.group(1), m.group(2))).lower() if m else None


def compute(raw, gh):
    """(missing list, local record count, github repo count)."""
    with open(gh) as f:
        listing = json.load(f)
    if isinstance(listing, dict):
        listing = listing.get("repos", [])
    local, nrepos = set(), 0
    for p in sorted(glob.glob(os.path.join(raw, "*", "repos.ndjson"))):
        with open(p, "rb") as f:
            for ln in f:
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                nrepos += 1
                for u in r.get("remotes", []):
                    k = key(u)
                    if k:
                        local.add(k)
    out = []
    for r in listing:
        k = key(r.get("url"))
        if k and k not in local:
            out.append({"name": r["name"], "url": r["url"], "fork": r.get("fork"), "size_kb": r.get("size_kb")})
    return out, nrepos, len(listing)


def main(argv):
    raw = os.path.join(core.KW_ROOT, "corpus", "raw")
    gh = os.path.join(raw, "github-list", "github_repos.json")
    if len(argv) >= 3 and argv[1] == "--github-json":
        gh = argv[2]
        raw = argv[3] if len(argv) > 3 else raw
    if not os.path.isfile(gh):
        print("github_repos.json not found; run the github-list item first", file=sys.stderr)
        return 2
    out, nrepos, ngh = compute(raw, gh)
    print("local_repo_records=%d github_repos=%d missing=%d" % (nrepos, ngh, len(out)), file=sys.stderr)
    json.dump(out, sys.stdout, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
