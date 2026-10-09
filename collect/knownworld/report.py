#!/usr/bin/env python3
"""report.py: builds corpus/CORPUS-REPORT.md from corpus/merged/stats.json, repos.json, the raw manifests and SURVEY.md.

Counts, verdicts and repository directory names only (the names SURVEY.md already carries). Never prints or reads an
event line. Deterministic: no clock. Standard library only. Run after merge.py.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
KW = os.path.dirname(os.path.dirname(HERE))
MERGED = os.path.join(KW, "corpus", "merged")
RAW = os.path.join(KW, "corpus", "raw")
OUT = os.path.join(KW, "corpus", "CORPUS-REPORT.md")

S = json.load(open(os.path.join(MERGED, "stats.json")))
R = json.load(open(os.path.join(MERGED, "repos.json")))
M = S["manifests"]
NODES = {(n["host"], n["path"]): n for n in S["repo_nodes"]}

# Fleet verification verdicts (Haiku verify stage, handed to the Merge manager as counts and verdicts only).
VERIFY_FAIL = {"claude-linux": "verify_ok=false, privacy_ok=false: the scan flagged one text line over 400 characters in "
               "card.md (the card, not a corpus record); all counts matched. Fixed by reflowing the card line; "
               "privacy_scan.py now exits 0 on corpus/raw."}
VERIFY_NOTES = {
    "codex-win-a": "privacy scan counted 29,952 records against 29,950 events: the two extra are manifest.json and "
                   "checkpoint.json, which the scanner counts as records; no delta in events.",
    "codex-linux": "verifier recount differed from the manifest raw sum by 13 lines (0.02%): the Linux session trees "
                   "are live and grew between the collect and the verify; the corpus is a snapshot of 12:45Z.",
    "c-births": "privacy scan counted 609 records against 607 events (manifest and checkpoint); no delta.",
}


def esc(s):
    return str(s).replace("|", "/")


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(x) for x in r) + " |")
    return out


def fmt(n):
    return "{:,}".format(n) if isinstance(n, int) else str(n)


def ev(item):
    return M[item]["events"] if item in M else 0


def evs(*items):
    return sum(ev(i) for i in items)


# ---------------------------------------------------------------- SURVEY reconciliation

def survey_rows():
    txt = open(os.path.join(KW, "SURVEY.md")).read()

    def sect(a, b):
        i = txt.index(a)
        return txt[i:txt.index(b, i)]
    rows = []
    for host, a, b, pre in (("omen-c", "### 1a.", "### 1b.", "work/"), ("omen-e", "### 1b.", "### 1c.", "work/"),
                            ("omen-linux", "### 1c.", "### 1d.", "")):
        for line in sect(a, b).split("\n"):
            m = re.match(r"^\| (.+?) \| (.+?) \| (.+?) \| \**(\d+)\**.*? \| (\d+) \|$", line)
            if m and not m.group(1).startswith("Dir") and not m.group(1).startswith("Repo"):
                first = m.group(1).strip()
                tok = re.match(r"^(\S+)", first).group(1)
                rows.append({"host": host, "name": first, "key": pre + tok, "survey": int(m.group(4)),
                             "composite": ("(+" in first or "{" in first or "(bare" in first)})
    return rows


NESTED = {  # SURVEY 1a / 1b prose lists of nested repositories: (host, path) -> commits
    ("omen-c", "work/am4-harvest/ember"): 36, ("omen-c", "work/am4-harvest/gad"): 53,
    ("omen-c", "work/am4-harvest/manifest"): 32, ("omen-c", "work/Diana/oddlittlebird"): 2,
    ("omen-c", "work/Diana/showcase-site"): 292, ("omen-c", "work/_extract/comfy-quest-incomplete"): 111,
    ("omen-c", "work/_extract/comfy-quest-identity-wrong-tested"): 0, ("omen-c", "work/_retired/comfy"): 237,
    ("omen-c", "work/_retired/Lumberjacks"): 215,
    ("omen-c", "work/orchestration/local-operator-workspace-20260917"): 38,
    ("omen-c", "work/orchestration/truth-alignment-20260908"): 3, ("omen-c", "work/research/cnc-generals"): 1,
    ("omen-c", "work/deepagents-poc/target"): 0, ("omen-c", "work/overview/episodes"): 0,
    ("omen-e", "work/liveView/ingest"): 6, ("omen-e", "work/liveView/ui"): 13,
    ("omen-e", "work/start/planner"): 1660, ("omen-e", "work/start/precheck"): 42,
    ("omen-e", "work/start/precheckv2"): 1, ("omen-e", "work/start/contextforge"): 5,
    ("omen-e", "work/start/farmer"): 29, ("omen-e", "work/start/ashley"): 20, ("omen-e", "work/start/portmap"): 3,
    ("omen-e", "work/start/scarecrow"): 6, ("omen-e", "work/start/langfuse"): 8359,
    ("omen-e", "work/comfy/seer"): 1, ("omen-e", "work/battlemage/tempo-workbench"): 1,
    ("omen-e", "work/repos/multi-agent-build-blueprint"): 2, ("omen-e", "work/vllm-xpu-win/kernels"): 514,
    ("omen-e", "work/vllm-xpu-win/vllm-src"): 6,
}


def reconcile():
    rows = []
    for r in survey_rows():
        n = NODES.get((r["host"], r["key"]))
        rows.append((r["host"], r["name"], r["survey"], n, r["composite"]))
    for (h, p), c in NESTED.items():
        rows.append((h, p, c, NODES.get((h, p)), False))
    return rows


# ---------------------------------------------------------------- sections

L = []


def A(*xs):
    L.extend(xs)


def kinds(*items):
    """'33 repos, 10 worktrees, 1 bare' for the repo records of the given items."""
    c = Counter()
    for n in S["repo_nodes"]:
        if n["item"] in items:
            c["worktrees" if n["worktree"] else "bare" if n["bare"] else "repos"] += 1
    return ", ".join("%d %s" % (v, k) for k, v in sorted(c.items(), key=lambda kv: kv[0]))
tot = S["events_out"]
A("# CORPUS-REPORT.md: the Known World corpus run")
A("")
A("Work item w-26069fe96149, collection day 2026-10-09. Written by the Merge manager (Sonnet 5.5) from "
  "`corpus/merged/stats.json`, `repos.json` and the raw manifests by `collect/knownworld/report.py`; counts and "
  "verdicts only, no corpus line is quoted. Merge is `collect/knownworld/merge.py` (deterministic, stdlib only: two "
  "runs give byte-identical output).")
A("")
A("## 1. Totals")
A("")
lin = S["lineages"]
A(*table(["Measure", "Value"], [
    ["Raw events collected (26 items)", fmt(S["events_loaded"])],
    ["Merged events (`corpus/merged/events.ndjson`)", fmt(tot)],
    ["Span, first to last event", "%s to %s" % (S["first_ts"], S["last_ts"])],
    ["Git lineages (repository components)", fmt(lin["git"])],
    ["Local repository records walked (all hosts, mirrors included)", fmt(S["repo_records"])],
    ["Non-git directory lineages (file births)", fmt(lin["dir"])],
    ["GitHub-only lineages (listed on GitHub, no clone)", fmt(lin["github_only"])],
    ["Sessions (distinct class + session id, `sessions.json`)", fmt(S["sessions"])],
    ["chat_session records (one per transcript file or conversation)", fmt(S["chat_session_records"])],
    ["chat_msg records (folded per session, role, minute)", fmt(S["chat_msg_records"])],
    ["Messages folded into those chat_msg records", fmt(S["chat_msg_folded_messages"])],
    ["Actors (class + name)", fmt(S["actors"])],
    ["Candidate lineage links (never merged)", fmt(S["candidates"])],
    ["Null-ts events dropped by Merge", fmt(S["dropped_null_ts_total"])],
]))
A("")
A("The first event (2011-08-25) is the GitHub account's creation date (the `repo_born` of the 2011 fork). The first "
  "commits are 2015-08 (PoE-Item-Filter-Creator, two commits, flagged third_party because their author is not in the "
  "identity map), 2017-12 and 2018-08; the first chat is 2023-04 (ChatGPT).")
A("")

# ---- 2 source coverage
A("## 2. Source coverage against SURVEY.md sections 1 to 3")
A("")
A("Status: covered = collected and verified; partial = collected with a stated hole; absent = not collected, with "
  "the reason. Event counts are raw item totals before Merge folding.")
A("")
cov = []
cov.append(["1a C:\\work top-level repos (34 listed, 10 linked worktrees, 1 bare)", "covered", "c-git-a, c-git-b, c-git-c",
            fmt(evs("c-git-a", "c-git-b", "c-git-c")),
            "3 shards by sha1(path); records: " + kinds("c-git-a", "c-git-b", "c-git-c") + "; numstat missing on one partial clone"])
cov.append(["1a C: nested repos (14)", "covered", "c-git-nested", fmt(ev("c-git-nested")),
            "all 14 SURVEY-listed nested repos found; the 10 missing roots are work-list globs that match nothing"])
cov.append(["1b E:\\work top-level repos (38)", "covered", "e-git-a, e-git-b, e-git-c",
            fmt(evs("e-git-a", "e-git-b", "e-git-c")),
            "records: " + kinds("e-git-a", "e-git-b", "e-git-c") + "; numstat skipped on the llama.cpp fork (partial clone, "
            "11,272 commits): commit counts kept, ins/del are 0"])
cov.append(["1b E: nested repos (16)", "covered", "e-git-nested", fmt(ev("e-git-nested")),
            "all 16 SURVEY-listed nested repos found; the 18 missing roots are globs that match nothing"])
cov.append(["1c Linux repositories (~25 + ~/work/worktrees 94)", "covered", "linux-git", fmt(ev("linux-git")),
            "31 records; worktree branches read from the parents with `--all` (121 worktree events); zero-commit "
            "repos (jepa-*, hybrid-context-trial, git-local-probe) are not walked (immutable rule, 8 excluded); "
            "commandcenter-public is a tarball snapshot, not a repo"])
cov.append(["1d AM4 git repositories (11)", "covered", "am4-git", fmt(ev("am4-git")),
            "over ssh, read-only; 4 shallow clones (ComfyUI, level-zero-tests, libpng, llama.cpp) and a partial clone "
            "(quest-build, numstat missing)"])
cov.append(["1d AM4 non-git dirs (am4-dual-nvidia-poc, vllm-e3)", "covered", "am4-births", fmt(ev("am4-births")),
            "v1.4: births and updates over ssh (section 12)"])
cov.append(["1e FX99 git repositories (4)", "covered", "fx99-git", fmt(ev("fx99-git")),
            "continuity, fleet, fleet.git (bare), ledger"])
cov.append(["1e FX99 non-git dirs (dmos, menu, liferaft, ai-bench, apps, cookbook)", "covered", "fx99-births",
            fmt(ev("fx99-births")), "v1.4: births and updates over ssh (section 12)"])
cov.append(["1f GitHub: 50 public repos (djcdevelopment) + steppe-integrations", "partial", "github-list, mirror-0, "
            "mirror-1", fmt(evs("github-list", "mirror-0", "mirror-1")),
            "public view only (gh not authenticated): 54 repo_born events, 12 repos mirrored; 2 forks skipped; "
            "private repos pending auth (section 8)"])
cov.append(["2 C:\\work non-git dirs (omen-perception, _retired, orchestration, tools, ...)", "covered", "c-births",
            fmt(ev("c-births")), "38 sources; skip list honoured (dotnet9, jdk17, godot, fieldlab-postgres-data, "
            "model, venvs)"])
cov.append(["2 C: root dirs (hearth-var, dirty-diffs, omen-perception-authored, tuning, assessment, AM4-provision, "
            "OMEN_prep)", "partial", "c-births", "(in c-births)",
            "births and (v1.4) updates. Bulk-copied dirs are flagged `bulk_copy` (173 records) but their in-record timestamps "
            "(cycle.log lines, dirty-diffs content) were not read; hearth-var/execution/events.ndjson (573 events) "
            "is not in any item"])
cov.append(["2 E:\\work non-git dirs (comfy, vllm-xpu-win, start, battlemage, 8350, dump, ...)", "covered",
            "e-births", fmt(ev("e-births")), "49 sources plus loose files; models skipped"])
cov.append(["3 ChatGPT export, normalized (380 conversations, 19,045 messages)", "covered", "chatgpt",
            fmt(ev("chatgpt")), "metadata only; 4,932 system-role messages and 12 undated records dropped and "
            "counted; titles and text never read"])
cov.append(["3 Claude Code, Windows archive zip (413 jsonl)", "covered", "claude-zip", fmt(ev("claude-zip")),
            "`unzip -p` of allowlisted members only; archive never extracted; 412 members seen"])
cov.append(["3 Claude Code, Windows live (1,042 jsonl)", "covered", "claude-win", fmt(ev("claude-win")),
            "history.jsonl (454 lines) not read: its fields are prompt text (contract section 2)"])
cov.append(["3 Codex, Windows (432 jsonl, 10.6 GB)", "covered", "codex-win-a, codex-win-b",
            fmt(evs("codex-win-a", "codex-win-b")), "2 shards of 216 files; auth.json excluded"])
cov.append(["3 Claude Code, Linux (481 jsonl at survey, 499 at collect)", "covered", "claude-linux",
            fmt(ev("claude-linux")), "live tree: a snapshot of 12:45Z; history.jsonl not read"])
cov.append(["3 Codex, Linux (50 jsonl, 51 at collect)", "covered", "codex-linux", fmt(ev("codex-linux")),
            "snapshot of 12:45Z; session_index.jsonl and history.jsonl not read (thread names are text)"])
cov.append(["3 OpenCode sqlite (24 sessions)", "covered", "opencode", fmt(ev("opencode")),
            "opened `mode=ro&immutable=1`: WAL contents may be missed"])
cov.append(["3 HEARTH ledger, Linux (472,077 lines) and Windows copy (90,784)", "covered", "hearth-ledger",
            fmt(ev("hearth-ledger")), "535,587 polling rows dropped and counted; 1,293 event_ids present in both "
            "copies deduped; args_preview, result_digest and error text never read"])
cov.append(["3 Continuity (`ct`) ledgers: omen-linux, am4, fx99", "covered", "continuity-runs",
            fmt(ev("continuity-runs")), "event bodies never read; imported transcript copies under "
            "`transcripts/` not read (duplicates of Claude and OpenCode sessions)"])
cov.append(["3 deepagents runs and hearth-production obs-offload artifacts", "covered", "continuity-runs",
            "(in continuity-runs)", "133 run directories and 401 per-call observations; counts only"])
cov.append(["3 assessment transcripts (3 runs, C:)", "covered", "continuity-runs", "(in continuity-runs)",
            "3 run records; counts only"])
cov.append(["3 Downloads session exports (6 zips)", "absent", "-", "0",
            "SURVEY: unopened unless Scope decides they add span; Scope did not; the chat span is already "
            "continuous 2023-04 to 2026-10 without them"])
A(*table(["SURVEY row", "Status", "Item(s)", "Events", "Reason / note"], cov))
A("")
chat_months = [ym for ym, k in S["per_ym"].items() if ym >= "2024-11" and not k.get("chat_msg")]
A("Chat coverage by source: ChatGPT 2023-04 to 2026-03, Claude zip 2026-05 to 06, Windows live Claude and Codex "
  "from 2026-06-29, Linux Claude, Codex and OpenCode from 2026-09-27 to the snapshot. SURVEY.md calls this "
  "continuous; the merged corpus shows one hole: **no chat source covers %s** (the ChatGPT export ends 2026-03-12 "
  "and the first Claude transcript is 2026-05-09). Commits, births and the HEARTH ledger are the only record of "
  "that stretch. Months before 2024-11 are sparse because the ChatGPT export holds few conversations then, not "
  "because a source is missing." % (", ".join(chat_months) or "none"))
A("")

# ---- 3 reconciliation
A("## 3. Reconciliation of commit counts")
A("")
A("Two reconciliations. First, per item: the commit total the extractor declared in its repo records "
  "(`rev-list --count --all`) against the commit events it emitted, and the Haiku verifiers' independent recount. "
  "Second, per repository against the SURVEY.md figures. Merge then folds identical shas (section 5).")
A("")
byitem_d, byitem_e = Counter(), Counter()
for n in S["repo_nodes"]:
    byitem_d[n["item"]] += n["commits"]
    byitem_e[n["item"]] += n["commit_events"]
rows = []
for it in S["items_order"]:
    if it in byitem_d:
        rows.append([it, M[it]["repos"], fmt(byitem_d[it]), fmt(byitem_e[it]),
                     "match" if byitem_d[it] == byitem_e[it] else "DELTA %+d" % (byitem_e[it] - byitem_d[it]),
                     "ok" if it not in VERIFY_FAIL else "see section 7"])
A(*table(["Item", "Repo records", "Declared commits", "Commit events", "Declared vs events", "Verifier"], rows))
A("")
rec = reconcile()
ex = dl = ms = 0
detail = []
for host, name, sv, n, comp in rec:
    if n is None:
        ms += 1
        detail.append([host, name, sv, "-", "-", "not found as a repo record"])
        continue
    d = n["commits"] - sv
    if d == 0:
        ex += 1
        st = "exact"
    else:
        dl += 1
        st = "ours +%d" % d if d > 0 else "ours %d" % d
        if comp:
            st += " (composite row)"
    detail.append([host, name, sv, n["commits"], "%+d" % d, st])
A("Per-repository check against SURVEY.md sections 1a, 1b, 1c and the nested lists: **%d exact, %d differ, %d not "
  "found** of %d rows. SURVEY gives no per-repository counts for AM4 or FX99; there the verifiers' recounts "
  "(AM4 368 commits in 11 repos, FX99 102 in 4) equal the manifests." % (ex, dl, ms, len(rec)))
A("")
A("Rows that are not exact (the survey is a snapshot taken before collection; a repository that gained commits since, or "
  "whose composite row sums several records, differs by design):")
A("")
nz = [r for r in detail if r[5] != "exact"]
A(*table(["Host", "SURVEY row", "SURVEY", "Corpus", "Delta", "Verdict"], nz))
A("")
A("Linux deltas are repositories that were still being committed to on 2026-10-09 (continuity ledger, discengine, "
  "lab). Nothing in the corpus is short of a SURVEY figure without a reason listed above.")
A("")

# ---- 4 event totals
A("## 4. Event totals (merged)")
A("")
A("### Per kind")
A("")
A(*table(["Kind", "Events"], [[k, fmt(v)] for k, v in sorted(S["per_kind"].items(), key=lambda kv: -kv[1])]))
A("")
A("### Per host")
A("")
A(*table(["Host", "Events"], [[k, fmt(v)] for k, v in sorted(S["per_host"].items(), key=lambda kv: -kv[1])]))
A("")
A("### Per actor class")
A("")
A(*table(["Actor class", "Events"], [[k, fmt(v)] for k, v in sorted(S["per_class"].items(), key=lambda kv: -kv[1])]))
A("")
A("### Per source and kind")
A("")
A(*table(["Source / kind", "Merged", "Raw"], [[k, fmt(v), fmt(S["raw_src_kind"].get(k, 0))]
                                              for k, v in S["per_src_kind"].items()]))
A("")
A("### Per year-month")
A("")
rows = []
for ym, k in S["per_ym"].items():
    total = sum(k.values())
    rows.append([ym, fmt(total), fmt(k.get("commit", 0)), fmt(k.get("chat_msg", 0)), fmt(k.get("chat_session", 0)),
                 fmt(k.get("offload_call", 0)), fmt(total - k.get("commit", 0) - k.get("chat_msg", 0)
                                                    - k.get("chat_session", 0) - k.get("offload_call", 0))])
A(*table(["Year-month", "Total", "commit", "chat_msg", "chat_session", "offload_call", "other"], rows))
A("")

# ---- 5 dropped
A("## 5. Dropped counters")
A("")
rows = []
for it in S["items_order"]:
    d = M[it]["dropped"] or {}
    c = M[it]["coverage"] or {}
    rows.append([it, fmt(d.get("null_ts", 0)), fmt(d.get("polling", 0)), fmt(d.get("decode_errors", 0)),
                 fmt(d.get("other_role", 0)), fmt(c.get("null_ts_emitted", 0)), fmt(c.get("deduped", 0)),
                 "; ".join(w for w in (M[it]["warnings"] or []))[:150] or "-"])
A(*table(["Item", "null_ts", "polling", "decode_errors", "other_role", "null_ts_emitted", "deduped in item",
          "Warnings"], rows))
A("")
A("`null_ts` = records the extractor could not bucket (dropped there); `null_ts_emitted` = records emitted with a "
  "null `ts` (a branch with no unique commit, a bad commit date), which Merge drops. `other_role` = ChatGPT "
  "system messages (not user, assistant or tool).")
A("")
A("Merge-level drops and folds:")
A("")
A(*table(["Counter", "Value"],
         [["Null-ts events dropped, " + k, fmt(v)] for k, v in S["dropped_null_ts"].items()] +
         [["Duplicates folded, " + k, fmt(v)] for k, v in S["deduped"].items()] +
         [["Events loaded", fmt(S["events_loaded"])], ["Events written", fmt(tot)]]))
A("")
A("Check: loaded %s - duplicates %s - null-ts %s = written %s." % (
    fmt(S["events_loaded"]), fmt(sum(S["deduped"].values())), fmt(S["dropped_null_ts_total"]), fmt(tot)))
A("")
A("Claude zip against the live tree: %s sessions overlap (the zip ends 2026-06-22, the live tree starts "
  "2026-07-10). Three `chat_session` and 90 `chat_msg` duplicates were found inside the Linux tree (three transcript "
  "file names occur twice under `~/.claude/projects` with one session id) and folded. Dedupe is on the extractor's ref (session, file stem, "
  "role, minute), because message uuids are folded away at collection; a resumed session that copies history into "
  "a new file under a new stem would be counted twice and cannot be detected without reading message ids." % (
      "0" if not S["zip_live_overlap"] else str(S["zip_live_overlap"])))
A("")

# ---- 6 candidate links
A("## 6. Lineage components and candidate links")
A("")
A(*table(["Link basis", "Unions made"], [[k, v] for k, v in S["link_basis"].items()]))
A("")
lb = S["link_basis"]
A("%d components hold more than one repository record; the largest has %d. Unions made: %d by shared root, %d by "
  "shared sha, %d by linked worktree. No squash mirror needed the remote-URL or root-tree rule (the `private-migration` copies "
  "share root commits), and no shallow clone needed the boundary or remote fallback: the six shallow third-party "
  "clones (one to six commits each) stay singleton lineages (`rooted: false`, id `github:<owner>/<name>` where a remote names "
  "one)." % (S["components_multi"], S["largest_components"][0], lb.get("root", 0), lb.get("sha_overlap", 0),
              lb.get("worktree", 0)))
A("")
A("Lineages that merged several records (names are directory names): ")
A("")
multi = [x for x in R["lineages"] if x["kind"] == "git" and x.get("members", 1) > 1]
multi.sort(key=lambda x: -x["members"])
A(*table(["Lineage (first 8 of id)", "Records", "Hosts", "Unique commits", "Names"],
         [[x["id"][:8], x["members"], ",".join(x["hosts"]), fmt(x["commits"]), ", ".join(x["names"])[:110]]
          for x in multi]))
A("")
A("Candidate links (recorded in `repos.json`, none merged):")
A("")
cl = R["candidates"]
if cl:
    nm = {x["id"]: ",".join(x["names"])[:30] for x in R["lineages"]}
    A(*table(["Lineage A", "Lineage B", "Basis", "Key"],
             [[nm.get(c["a"], c["a"][:8]) + " (" + c["a"][:8] + ")", nm.get(c["b"], c["b"][:8]) + " (" +
               c["b"][:8] + ")", c["basis"], c["key"]] for c in cl]))
else:
    A("None.")
A("")
A("The three candidates are the `ct` ledgers on omen-linux, am4 and fx99: same directory name and an identical root "
  "tree (the empty bookkeeping commit), different root commits. They are separate ledgers by design, so they stay "
  "unmerged. Name-only and remote-only matches among the other lineages produced no further pairs: every repository "
  "that shares a name or a remote across hosts also shares a root commit and is already one lineage.")
A("")
A("Joins by path (chat, deepagents and ledger events to a lineage, by host and depth-2 path, Windows case-folded):")
A("")
rows = []
for s, c in S["join"].items():
    rows.append([s, fmt(c.get("joined", 0)), fmt(c.get("joined_dir", 0)), fmt(c.get("unmatched", 0)),
                 fmt(c.get("no_path", 0))])
A(*table(["Source", "To a git lineage", "To a non-git dir lineage", "Unmatched path", "No path"], rows))
A("")
A("ChatGPT, HEARTH ledger and `ct` events carry no path, so they stay unjoined (`repo` null). Unmatched paths are "
  "working directories that hold no repository (home, scratch, `work/trial`, worktrees, directories since deleted).")
A("")

# ---- 7 verification
A("## 7. Items that failed verification, and why")
A("")
fails = [k for k in VERIFY_FAIL]
A("One item of 26 returned `verify_ok=false`:")
A("")
for k, v in VERIFY_FAIL.items():
    A("- **%s**: %s" % (k, v))
A("")
A("Verifier remarks that were not failures:")
A("")
for k, v in VERIFY_NOTES.items():
    A("- **%s**: %s" % (k, v))
A("")
A("No quirk described a toolkit bug, so no extractor was patched and no item was re-run. Quirks that matter for "
  "later runs: partial clones lose numstat (ins/del 0, `meta.no_numstat`) in am4-git (quest-build), c-git-c and "
  "e-git-b (llamacpp-qwen38); `roots_missing` warnings count work-list globs that matched nothing, not repositories "
  "that failed.")
A("")
A("After the card fix, `privacy_scan.py corpus/raw` and `privacy_scan.py corpus/merged` both exit 0.")
A("")

# ---- 8 github
A("## 8. GitHub list and auth state")
A("")
gh_owner, gh_fork = Counter(), 0
p = os.path.join(RAW, "github-list", "events.ndjson")
if os.path.isfile(p):
    for line in open(p, "rb"):
        e = json.loads(line)
        gh_owner[(e.get("repo_local") or "github:?").split(":", 1)[1].split("/")[0]] += 1
        gh_fork += 1 if (e.get("meta") or {}).get("fork") else 0
A("`gh` is installed but **not authenticated**: the manifest warning is `pending auth: private repos not listed`, "
  "and the mirror phase reported `auth: unavailable`. The list is the public view (unauthenticated budget 60 "
  "requests per hour): %d repo_born events (%s; %d forks). Private repositories named in SURVEY (404-isolate, "
  "isolate, notebook, steppeintegrations-site, the E: privates) are present in the corpus through their local git "
  "history, but **their GitHub-side metadata (`created_at`, size, language) is pending**: after `gh auth login`, "
  "re-run `github-list` and `clone_mirrors.py` to add them. Of the 54 listed repositories, %d matched a lineage by "
  "remote URL and %d (the forks open-notebook and personal_website) have no clone and stay GitHub-only lineages. Mirror "
  "phase: 12 cloned (`mirror-0` 8 repos, `mirror-1` 4), 2 forks skipped." % (
      sum(gh_owner.values()), ", ".join("%s %d" % kv for kv in sorted(gh_owner.items())), gh_fork,
      S["github_event_match"].get("remote_url", 0) + S["github_event_match"].get("repo_local_node", 0),
      S["github_event_match"].get("github_only", 0)))
A("")

# ---- 9 local seat
A("## 9. Local-seat arm")
A("")
A("The local-seat arm (repo cards for the Linux repositories through `local_generate`, graded against the Haiku "
  "arm for substance and form) was **deferred**: the 30B and both AM4 tool seats are absent under the bench27 "
  "all-27B hold on 2026-10-09. This is recorded, not re-routed: no cloud or other seat was substituted (H-2). "
  "No repository cards exist from any arm, so the Haiku-versus-30B-versus-AM4 grading table and its three "
  "capability records are empty. The Haiku arm wrote per-item cards (`corpus/raw/<item>/card.md`), which are "
  "source cards, not repo cards.")
A("")

# ---- 10 sessions
A("## 10. Chat session counts against file counts")
A("")
rows = []
chat_items = [("chatgpt", "2 files (conversations + messages)"), ("claude-zip", "412 zip members"),
              ("claude-win", "1,042 jsonl"), ("claude-linux", "499 jsonl"), ("codex-win-a", "216 jsonl"),
              ("codex-win-b", "216 jsonl"), ("codex-linux", "51 jsonl"), ("opencode", "24 sessions in 1 db")]
for it, files in chat_items:
    c = S["chat_per_item"].get(it, {})
    seen = M[it]["coverage"].get("sources_seen")
    rows.append([it, files, fmt(seen), fmt(c.get("chat_session_records", 0)), fmt(c.get("messages", 0)),
                 fmt(M[it]["raw_sum"])])
A(*table(["Item", "Source files", "Sources seen", "chat_session records", "Messages folded", "Raw lines or rows"],
         rows))
A("")
A("Session records are one per transcript file that held at least one user or assistant line; files with none "
  "(queue-operation only, empty) produce no record (%s). Claude subagent transcripts share their parent's session id, so the 1,925 Claude records "
  "make %d distinct sessions in `sessions.json` (`segments` says how many files each had). By class: %s." % (
      ", ".join("%s %d" % (it, (M[it]["coverage"].get("sources_seen") or 0) - S["chat_per_item"].get(it, {}).get(
          "chat_session_records", 0)) for it, _ in chat_items if it not in ("chatgpt", "opencode")),
      S["sessions_by_class"].get("claude", 0),
      ", ".join("%s %d" % kv for kv in S["sessions_by_class"].items())))
A("")

# ---- 11 notes
A("## 11. Limits and open items")
A("")
for t in (
    "`repos.json` carries `third_party` by the CONTRACT rule (derek_share under 0.05, or a foreign org with no Derek "
    "identity) and `foreign_org` separately: resonantOS and showcase-site, where Derek has some commits, are "
    "`third_party: false, foreign_org: true`; the renderer may treat `foreign_org` as third-party.",
    "Region (`repos.json.region`) is null for every lineage: it is assigned by Compile (and by the deferred local-seat "
    "arm), not by Merge.",
    "Branch events cannot be matched across copies by name (the extractor hashes the repository path into the ref); "
    "Merge dedupes them per lineage and birth second, keeping the busiest copy. 178 were folded.",
    "Lineage ids of rootless components are not root shas: empty or one-commit clones carry `github:<owner>/<name>` "
    "(lower case) when a remote names one, else a `dir:` id (one empty local repo).",
    "Commit `ins`/`del` are 0 where numstat was unavailable (`meta.no_numstat`): about 11.5 thousand raw commit "
    "events, mostly the llamacpp-qwen38 partial clone (11,272 commits).",
    "Linux Claude and Codex trees are live; the corpus is the 12:45Z snapshot. A later run will add the sessions "
    "since then (this one included).",
    "Windows `hearth-var/execution/events.ndjson` (573 events) and the in-record timestamps of the bulk-copied "
    "C: directories are not collected (section 2).",
    "AM4 and FX99 non-git directories are collected from v1.4 (`am4-births`, `fx99-births`, section 12); "
    "non-git omen-linux directories likewise (`linux-births`).",
    "GitHub private repositories and fork metadata are pending authentication (section 8)."):
    A("- " + t)
A("")
# ---- 12 file activity (v1.4)
FA = S.get("file_activity", {})
A("## 12. File activity extension (v1.4)")
A("")
A("Section 7 of the v1.4 request; numbered 12 here because sections 7 to 11 already exist. Source `fs_births` now "
  "emits `file_update` beside `file_birth`: one record per (depth-2 directory, day), counted only when the file's "
  "last-modified day differs from its birth day. Items: `c-births`, `e-births`, `linux-births`, `am4-births`, "
  "`fx99-births`. Counts only.")
A("")
rows, tot_ = [], Counter()
for it, c in FA.get("per_item", {}).items():
    rows.append([it, M[it]["status"], fmt(c.get("birth_records", 0)), fmt(c.get("birth_files", 0)),
                 fmt(c.get("birth_bulk_records", 0)), fmt(c.get("update_records", 0)), fmt(c.get("update_files", 0)),
                 fmt(c.get("update_bulk_records", 0)), fmt(M[it]["coverage"].get("sources_seen") or 0),
                 fmt(len(M[it]["coverage"].get("sources_skipped") or [])),
                 fmt(M[it]["coverage"].get("update_null_mtime", 0))])
    tot_.update(c)
rows.append(["total", "", fmt(tot_["birth_records"]), fmt(tot_["birth_files"]), fmt(tot_["birth_bulk_records"]),
             fmt(tot_["update_records"]), fmt(tot_["update_files"]), fmt(tot_["update_bulk_records"]), "", "", ""])
A(*table(["Item", "Status", "file_birth records", "Files folded (births)", "Bulk-copy births", "file_update records",
          "Files folded (updates)", "Bulk-copy updates", "Sources", "Skipped", "Files with null mtime"], rows))
A("")
A("Per host and year-month, file activity = files folded into births + updates (merged corpus, after dedupe):")
A("")
hy = FA.get("per_host_ym", {})
yms = sorted({ym for h in hy.values() for ym in h})
hs = sorted(hy)
rows = []
for ym in yms:
    r = [ym]
    for h in hs:
        c = hy[h].get(ym, {})
        r.append(fmt(c.get("file_birth_files", 0) + c.get("file_update_files", 0)))
    rows.append(r)
rows.append(["total"] + [fmt(sum(c.get("file_birth_files", 0) + c.get("file_update_files", 0) for c in hy[h].values()))
                         for h in hs])
A(*table(["Year-month"] + hs, rows))
A("")
for t in (
    "**Lower bound.** A filesystem keeps one last-modified time per file, so a file edited on ten days counts as one "
    "update day; update frequency and density are floors. A file whose mtime day equals its birth day is a birth only.",
    "**Null rule.** Births use the birth time (mtime if the filesystem has none); a mtime before 2005 (the 1970 and "
    "1980 placeholders) or in the future yields no update and is counted in the manifest as `update_null_mtime` "
    "(column above). Copied files can carry an mtime earlier than their birth: those count as updates on the mtime day.",
    "**Bulk copies.** A record is flagged `bulk_copy` when 80 percent or more of its files share birth seconds "
    "that hold 100 or more files; the flagged counts are in the table. They are kept, not removed.",
    "**Skipped.** Nothing in these five items was skipped (no timeouts); never-walk directories (models, checkpoints, "
    "venvs, .venv, node_modules, .cache, .git, ComfyUI/models), credential-bearing files and symlinked roots are "
    "pruned inside the walk. `~/work/worktrees`, `~/work/amux` and `~/work/known-world` (this corpus) are excluded "
    "from `linux-births`; git repositories with commits stay with `*-git`.",
    "**Overlap.** Non-git directories can hold nested git repositories (for example under `trial`): their files "
    "count here and their commits in `linux-git`. Compile should treat file activity inside a directory that is also "
    "a lineage as density, not as new work."):
    A("- " + t)
A("")

A("Reproduce: `.venv/bin/python -I collect/knownworld/merge.py && .venv/bin/python -I "
  "collect/knownworld/report.py && .venv/bin/python -I collect/knownworld/privacy_scan.py corpus/merged` from "
  "`~/work/known-world` with `PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 GIT_TERMINAL_PROMPT=0`.")
A("")

import textwrap  # noqa: E402

W = []
for ln in L:
    if len(ln) > 118 and not ln.startswith("|") and not ln.startswith("#"):
        ind = "  " if ln.startswith("- ") else ""
        W.extend(textwrap.wrap(ln, width=118, subsequent_indent=ind, break_long_words=False, break_on_hyphens=False))
    else:
        W.append(ln)
with open(OUT, "w") as f:
    f.write("\n".join(W) + "\n")
print("wrote %s lines=%d" % (OUT, len(W)))
