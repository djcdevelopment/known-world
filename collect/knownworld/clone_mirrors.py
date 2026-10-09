#!/usr/bin/env python3
"""clone_mirrors.py [--dry-run] [--include-forks] [--max-kb N]

Mirror stage helper. Takes the GitHub repositories no local remote names (missing_repos.py), runs
`git clone --mirror` for each into cache/clones/<owner>__<name>.git (the only git write the toolkit ever does,
confined to cache/clones) and writes one git_repo work item per clone to corpus/worklist/mirror-<name>.json with the
clone's host set to github. Forks are skipped unless --include-forks; repos over --max-kb (default 600000) are
reported and skipped. Prints counts and ids only.
"""
import json
import os
import re
import sys

sys.dont_write_bytecode = True  # -I ignores PYTHONDONTWRITEBYTECODE
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from knownworld import core, missing_repos  # noqa: E402
from knownworld.git_repo import clone_mirror  # noqa: E402


def main(argv):
    dry = "--dry-run" in argv
    forks = "--include-forks" in argv
    max_kb = 600000
    if "--max-kb" in argv:
        max_kb = int(argv[argv.index("--max-kb") + 1])
    core.setup_env()
    raw = os.path.join(core.KW_ROOT, "corpus", "raw")
    gh = os.path.join(raw, "github-list", "github_repos.json")
    if not os.path.isfile(gh):
        print("github_repos.json not found; run the github-list item first")
        return 2
    miss, nlocal, ngh = missing_repos.compute(raw, gh)
    todo, skipped = [], {"fork": 0, "too_big": 0, "bad_name": 0}
    for r in miss:
        m = re.match(r"^https://github\.com/([^/]+)/([^/]+)$", core.norm_remote(r["url"]) or "")
        if not m:
            skipped["bad_name"] += 1
            continue
        if r.get("fork") and not forks:
            skipped["fork"] += 1
            continue
        if isinstance(r.get("size_kb"), int) and r["size_kb"] > max_kb:
            skipped["too_big"] += 1
            continue
        todo.append((m.group(1), m.group(2), r))
    print("missing=%d to_clone=%d skipped=%s dry_run=%s" % (len(miss), len(todo), json.dumps(skipped), dry))
    if dry:
        return 0
    wl = os.path.join(core.KW_ROOT, "corpus", "worklist")
    os.makedirs(wl, exist_ok=True)
    cloned = failed = 0
    ids = []
    for owner, name, r in todo:
        dest = os.path.join(core.KW_ROOT, "cache", "clones", "%s__%s.git" % (owner, name))
        if not os.path.isdir(dest):
            rc, to = clone_mirror(r["url"], dest, 900)
            if rc != 0 or to:
                failed += 1
                continue
        cloned += 1
        iid = "mirror-" + re.sub(r"[^A-Za-z0-9_.-]", "_", name)
        item = {"id": iid, "source_type": "git_repo", "host": "omen-linux", "roots": [dest],
                "shard": {"k": 0, "n": 1, "rule": "sha1(path) % n"}, "since": None, "until": None,
                "out_dir": os.path.join(core.KW_ROOT, "corpus", "raw", iid), "timeout_s": 900, "mount": None,
                "options": {"scan_depth": 0, "host_override": "github", "display_map": {dest: "%s/%s" % (owner, name)}}}
        with open(os.path.join(wl, iid + ".json"), "w") as f:
            json.dump(item, f, indent=1)
        ids.append(iid)
    print("cloned=%d failed=%d items=%d" % (cloned, failed, len(ids)))
    print(json.dumps(ids))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
