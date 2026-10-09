"""ct_remote.py: shipped over ssh (with core.py). Prints type, recorded_at, runner and id of each continuity ledger
event, one JSON object per line. Event bodies are loaded by the JSON parser and discarded; nothing else is printed."""
import glob
import json
import os
import sys


def _ct_main(args):
    d = os.path.join(os.path.expanduser(args["path"]), "events")
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            with open(p, "rb") as f:
                o = json.load(f)
        except Exception:
            print(json.dumps({"bad": 1}))
            continue
        r = o.get("runner")
        if isinstance(r, dict):
            r = r.get("kind") or r.get("name") or r.get("id")
        print(json.dumps({"id": o.get("id") if isinstance(o.get("id"), str) else None,
                          "type": o.get("type") if isinstance(o.get("type"), str) else None,
                          "at": o.get("recorded_at") if isinstance(o.get("recorded_at"), str) else None,
                          "runner": r if isinstance(r, str) else None}))
    return 0


if __name__ == "__main__" and "KW_ARGS" in globals():
    sys.exit(_ct_main(KW_ARGS))  # noqa: F821
