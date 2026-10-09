#!/usr/bin/env python3
"""make_worklist.py: regenerate corpus/worklist/<id>.json and worklist.json (ids are stable).

Follows the seed table in known-world-plan/1-corpus.md. Shards are applied by run_item.py as
sha1(path) % n == k over each discovered source, so they are deterministic and disjoint. Run:
  .venv/bin/python -I collect/knownworld/make_worklist.py
"""
import json
import os
import sys

sys.dont_write_bytecode = True  # -I ignores PYTHONDONTWRITEBYTECODE
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from knownworld import core  # noqa: E402

KW = core.KW_ROOT
RAW = KW + "/corpus/raw/"
WL = KW + "/corpus/worklist/"
C, E = "/mnt/omen-c-read", "/mnt/omen-e-read"
H = "/home/derek"
RULE = "sha1(path) % n"
ZERO_COMMIT = ["*/hybrid-context-trial", "*/jepa-evidence-units-2026*", "*/jepa-confirmation-2026*",
               "*/jepa-project-holdout-2026*", "*/jepa-recorded-actions-2026*", "*/jepa-same-role-actions-2026*",
               "*/jepa-operation-representations-2026*", "*/known-world", "*/git-local-probe"]

items = []


def add(id, source_type, host, roots, timeout_s, mount=None, shard=(0, 1), **options):
    items.append({"id": id, "source_type": source_type, "host": host, "roots": roots,
                  "shard": {"k": shard[0], "n": shard[1], "rule": RULE}, "since": None, "until": None,
                  "out_dir": RAW + id, "timeout_s": timeout_s, "mount": mount, "options": options})


for k, s in enumerate("abc"):
    add("c-git-" + s, "git_repo", "omen-c", [C + "/work"], 1800, "c", (k, 3), scan_depth=1, log_timeout_s=600)
add("c-git-nested", "git_repo", "omen-c",
    [C + "/work/" + p for p in ("am4-harvest/*", "Diana/*", "_extract/*", "_retired/*", "orchestration/*",
                                "research/*", "deepagents-poc/target", "overview/episodes")],
    1200, "c", scan_depth=0, log_timeout_s=600)
for k, s in enumerate("abc"):
    add("e-git-" + s, "git_repo", "omen-e", [E + "/work"], 1800, "e", (k, 3), scan_depth=1, log_timeout_s=600)
add("e-git-nested", "git_repo", "omen-e",
    [E + "/work/" + p for p in ("start/*", "liveView/*", "vllm-xpu-win/*", "comfy/seer",
                                "battlemage/tempo-workbench", "repos/*")],
    1200, "e", scan_depth=0, log_timeout_s=600)
add("linux-git", "git_repo", "omen-linux",
    [H + "/work/*", H + "/work/trial/notebook*", H + "/work/clm-pilot/upstream", H + "/private-migration-20260923/*",
     H + "/git/*", H + "/.continuity/ledger", H + "/continuity-triage/*"],
    1200, None, scan_depth=0, log_timeout_s=600, exclude=ZERO_COMMIT)
add("am4-git", "git_repo", "am4", ["~/*", "~/.continuity/ledger", "~/o1/*", "~/baseline/*", "~/work/*"], 900, None,
    scan_depth=0, log_timeout_s=400)
add("fx99-git", "git_repo", "fx99", ["~/*", "~/.continuity/ledger"], 600, None, scan_depth=0, log_timeout_s=300)
add("github-list", "github_api", "github", [], 300, None, owner="djcdevelopment", orgs=["steppe-integrations"])
add("c-births", "fs_births", "omen-c",
    [C + "/" + d for d in ("hearth-var", "dirty-diffs", "omen-perception-authored", "tuning", "assessment",
                           "AM4-provision", "OMEN_prep")],
    2400, "c", children_of=[C + "/work"], exclude_children=["dotnet9", "jdk17", "godot-4.6.1", "fieldlab-postgres-data",
                                                             "model", "venvs"], find_timeout_s=900)
add("e-births", "fs_births", "omen-e", [], 2400, "e", children_of=[E + "/work"], loose_files=True,
    exclude_children=["models"], find_timeout_s=900)
# --- task 1c: repositories and trees outside work/ (SURVEY 1g). Repo paths come from a bounded find
# (maxdepth 5 below the E: root, `work` and the skip list excluded), listed explicitly so nested repos are found.
E_ROOT_REPOS = ["gemini", "HANDOFF/_backup_staging/projects/meal-planner", "helloworld/old-goat-new-tricks",
                "omen/bf6-highlights-retired-20260828", "omen/CC/GeneralsReplays", "omen/CC", "omen/clippy",
                "omen/DMos-actor-controls", "omen/DMos-chronicle", "omen/DMos-chronicle-salience",
                "omen/DMos-command-freshness", "omen/DMos", "omen/DMos-rc1", "omen/DMos-rehearsal",
                "omen/DMos-secrets", "omen/imagegen", "omen/menu",
                "omen/steward-multi-era/deploy-worktree-creator-carousel-d1b90f1",
                "omen/steward-multi-era/deploy-worktree-creator-compact-a0db3a0",
                "omen/steward-multi-era/deploy-worktree-creator-explorer-808d15f",
                "omen/steward-multi-era/deploy-worktree-creator-guide-20260915",
                "omen/steward-multi-era/deploy-worktree-creator-heatmap-acc5eb7", "omen/tensor", "resume",
                "resume-wt/claude-seat-receipts", "resume-wt/gemini-proof-snapshot",
                "resume-wt/linux-proof-review-20261006", "World of Warcraft/code", "World of Warcraft/Tempo",
                "World of Warcraft/tempo-viewer", "World of Warcraft/Tempo-worktrees/agent-a",
                "World of Warcraft/Tempo-worktrees/agent-b", "World of Warcraft/Tempo-worktrees/agent-c",
                "World of Warcraft/Tempo-worktrees/stream-f-gamma", "World of Warcraft/Tempo-wt-A-1b9",
                "World of Warcraft/Tempo-wt-A", "World of Warcraft/Tempo-wt-B", "World of Warcraft/Tempo-wt-C",
                "World of Warcraft/Tempo-wt-D", "World of Warcraft/Tempo-wt-E", "World of Warcraft/Tempo-wt-F"]
for k, s in enumerate("ab"):
    add("e-root-git-" + s, "git_repo", "omen-e", [E + "/" + r for r in E_ROOT_REPOS], 1800, "e", (k, 2),
        scan_depth=0, log_timeout_s=600)
add("c-root-git", "git_repo", "omen-c", [C + "/assessment", C + "/tuning"], 900, "c", scan_depth=0, log_timeout_s=600)
# births: E-root directories that are not repos (git children are skipped by fs_births); containers of repos are
# walked through children_of so their repo children are not counted twice. Installers, caches, app installs and the
# game client (_retail_) are skipped.
add("e-root-births", "fs_births", "omen-e", [], 2400, "e",
    children_of=[E, E + "/omen", E + "/World of Warcraft", E + "/helloworld", E + "/resume-wt"], loose_files=True,
    exclude_children=["work", "omen", "World of Warcraft", "helloworld", "resume-wt", "ComfyUI", "SteamLibrary",
                      "pip-cache", ".pnpm-store", "Comfy-Desktop", "Program Files", "Recovery", "$RECYCLE.BIN",
                      "System Volume Information", "msdownld.tmp", "Audacity", "ISO", "_retail_", "models"],
    find_timeout_s=900)

import glob  # noqa: E402

zero = sorted(d for pat in ("hybrid-context-trial", "jepa-evidence-units-2026*", "jepa-confirmation-2026*",
                            "jepa-project-holdout-2026*", "jepa-recorded-actions-2026*",
                            "jepa-same-role-actions-2026*", "jepa-operation-representations-2026*")
              for d in glob.glob(H + "/work/" + pat) if os.path.isdir(d))
add("linux-births", "fs_births", "omen-linux", zero + ([H + "/research"] if os.path.isdir(H + "/research")
                                                      and not os.path.islink(H + "/research") else []),
    3000, None, children_of=[H + "/work"], loose_files=True,
    exclude_children=["worktrees", "amux", "known-world"], find_timeout_s=900)
add("am4-births", "fs_births", "am4", ["~/work/am4-dual-nvidia-poc", "~/work/vllm-e3-20260923"], 900, None,
    find_timeout_s=600)
add("fx99-births", "fs_births", "fx99", ["~/dmos", "~/menu", "~/liferaft", "~/ai-bench", "~/apps", "~/cookbook"],
    900, None, find_timeout_s=600)
add("chatgpt", "chatgpt_export", "cloud", [E + "/work/chatGPT_parser/data/normalized"], 600, "e")
add("claude-zip", "claude_jsonl", "omen-e", [E + "/work/claude-20260623T084942Z-3-001.zip"], 1800, "e",
    zip=E + "/work/claude-20260623T084942Z-3-001.zip")
add("claude-win", "claude_jsonl", "omen-c", [C + "/Users/derek/.claude/projects"], 2400, "c")
for k, s in enumerate("ab"):
    add("codex-win-" + s, "codex_jsonl", "omen-c", [C + "/Users/derek/.codex/sessions"], 3600, "c", (k, 2))
add("claude-linux", "claude_jsonl", "omen-linux", [H + "/.claude/projects"], 900)
add("codex-linux", "codex_jsonl", "omen-linux", [H + "/.codex/sessions"], 900)
add("opencode", "opencode_db", "omen-linux", [H + "/.local/share/opencode/opencode.db"], 300)
add("hearth-ledger", "hearth_ledger", "omen-linux", [], 1800, "c",
    ledgers=[{"path": H + "/hearth-production/var/ledger", "host": "omen-linux"},
             {"path": C + "/hearth-var/ledger", "host": "omen-c"}])
add("continuity-runs", "continuity", "omen-linux", [], 900, "c", parts=[
    {"kind": "ct_ledger", "host": "omen-linux", "path": H + "/.continuity/ledger"},
    {"kind": "ct_ledger", "host": "am4", "path": "~/.continuity/ledger"},
    {"kind": "ct_ledger", "host": "fx99", "path": "~/.continuity/ledger"},
    {"kind": "deepagents_runs", "host": "omen-linux", "path": H + "/work/deepagents-linux/runs"},
    {"kind": "obs_offload", "host": "omen-linux", "path": H + "/hearth-production/runs"},
    {"kind": "assessment_runs", "host": "omen-c", "path": C + "/assessment/transcripts"}])


def main(only=()):
    os.makedirs(WL, exist_ok=True)
    index = []
    for it in items:
        if only and not any(it["id"].startswith(o) for o in only):
            index.append({"id": it["id"], "source_type": it["source_type"], "host": it["host"],
                          "mount": it["mount"] or "none", "timeout_s": it["timeout_s"], "file": WL + it["id"] + ".json",
                          "shard": "%d/%d" % (it["shard"]["k"], it["shard"]["n"])})
            continue
        p = WL + it["id"] + ".json"
        with open(p, "w") as f:
            json.dump(it, f, indent=1)
            f.write("\n")
        index.append({"id": it["id"], "source_type": it["source_type"], "host": it["host"],
                      "mount": it["mount"] or "none", "timeout_s": it["timeout_s"], "file": p,
                      "shard": "%d/%d" % (it["shard"]["k"], it["shard"]["n"])})
    with open(WL + "worklist.json", "w") as f:
        json.dump(index, f, indent=1)
        f.write("\n")
    print("items=%d" % len(index))


if __name__ == "__main__":
    main(sys.argv[1:])  # optional id prefixes: write only those items
