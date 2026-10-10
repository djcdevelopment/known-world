#!/usr/bin/env python3
"""Make bounded private packets for cheap scouts from discovery output, not raw sources."""
import argparse
import collections
import json
from pathlib import Path

from discover import validate_output


def prepare(directories, out):
    validate_output(out)
    out.mkdir(parents=True, exist_ok=True)
    groups = collections.defaultdict(list)
    for directory in directories:
        for path in sorted(directory.glob("*.json")):
            obj = json.loads(path.read_text())
            if not isinstance(obj, dict) or not {"candidates", "root", "group", "status"} <= obj.keys():
                continue
            rollups = {}
            for candidate in obj["candidates"]:
                rel = Path(candidate["path"]).relative_to(obj["root"])
                prefix = "/".join(rel.parts[:2]) or "."
                row = rollups.setdefault(prefix, {"path": str(Path(obj["root"]) / prefix), "directories": 0,
                                                  "structured_files": collections.Counter(), "git_markers": 0})
                row["directories"] += 1
                row["structured_files"].update(candidate["structured_files_direct"])
                row["git_markers"] += candidate["git_marker"]
            ranked = sorted(rollups.values(), key=lambda r: (-sum(r["structured_files"].values()), r["path"]))
            groups[obj["group"]].append({"source_id": obj["id"], "host": obj["host"], "status": obj["status"],
                                        "gaps": obj["gaps"], "limits": obj.get("limits"),
                                        "rollups_omitted": max(0, len(ranked) - 12), "rollups": ranked[:12]})
    # One packet per source root. A scout gets a small packet, never an unbounded tree.
    packets = []
    for group, sources in sorted(groups.items()):
        for source in sources:
            packet = {"group": group, "warning": "Directory metadata only. Files are not jobs/sessions/trials. Roots may overlap. Mtime is not event time.", "source": source}
            path = out / (source["source_id"] + ".json")
            path.write_text(json.dumps(packet, indent=2) + "\n")
            packets.append({"id": source["source_id"], "group": group, "file": str(path.resolve()),
                            "status": source["status"], "bytes": path.stat().st_size})
    (out / "index.json").write_text(json.dumps({"packets": packets}, indent=2) + "\n")
    return packets


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    packets = prepare(args.inventory, args.out)
    print(json.dumps({"packets": len(packets), "max_bytes": max((p["bytes"] for p in packets), default=0)}))


if __name__ == "__main__":
    main()
