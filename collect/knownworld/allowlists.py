"""allowlists.py: exact key sets and validators per source (CONTRACT.md section 2).

privacy_scan.py enforces these; extractors are written to emit exactly these. A key outside the allowlist, a value
failing its validator, a string over 120 characters or a key from the never-read lists makes a record a violation.
"""
import re

EVENT_KEYS = {"ts", "ts_author", "ts_commit", "kind", "actor", "role", "host", "repo", "repo_local", "path", "files",
              "magnitude", "ref", "src", "meta"}
REQUIRED = {"ts", "kind", "actor", "host", "ref", "src", "magnitude"}
KINDS = {"commit", "repo_born", "branch", "worktree", "file_birth", "file_update", "chat_msg", "chat_session", "offload_call",
         "receipt", "run"}
CLASSES = {"human", "chatgpt", "claude", "codex", "opencode", "local_model", "automation", "third_party"}
HOSTS = {"omen-c", "omen-e", "omen-linux", "am4", "fx99", "github", "cloud"}
ROLES = {"user", "assistant", "tool"}

TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
REF_RE = re.compile(r"^[A-Za-z0-9_.:=\-]{1,80}$")
NAME_RE = re.compile(r"^[A-Za-z0-9._:()+/\- ]{1,64}$")
TOKEN_RE = re.compile(r"^[A-Za-z0-9_.:/\-]{1,64}$")
CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")
REPO_LOCAL_RE = re.compile(r"^[a-z0-9\-]+:[^\x00-\x1f]{0,110}$")
REPO_RE = re.compile(r"^(?:[0-9a-f]{40}|dir:[a-z0-9\-]+:[^\x00-\x1f]{1,100}|github:[^\x00-\x1f]{1,100})$")

EMAIL_RE = re.compile(r"[^\s@/:]+@[^\s@/:]+\.[A-Za-z]{2,}")
SECRET_RES = [re.compile(p) for p in (
    r"ghp_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"gho_[A-Za-z0-9]{20,}", r"sk-[A-Za-z0-9\-_]{20,}",
    r"AKIA[0-9A-Z]{16}", r"-----BEGIN [A-Z ]*PRIVATE KEY", r"xox[baprs]-[A-Za-z0-9\-]{10,}",
    r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}", r"[Bb]earer\s+[A-Za-z0-9._\-]{20,}",
    r"://[^/\s:@]+:[^@\s/]+@")]

# Keys that carry text or secrets in some source: never present in a corpus record at any depth.
FORBIDDEN_KEYS = {
    "message", "content", "text", "title", "title_hint", "summary", "slug", "customTitle", "aiTitle", "gitBranch",
    "toolUseResult", "input", "attachment", "pastedContents", "display", "prompt", "thread_name", "instructions",
    "base_instructions", "arguments", "output", "parts", "asset_refs", "key_file_paths", "search_index",
    "decision_trace", "args_preview", "result_digest", "intent", "reason_text", "note", "notes", "error", "body",
    "diff", "email", "author_email", "author", "password", "token", "secret", "api_key", "access_token",
    "refresh_token", "credential", "authorization", "message_body", "commit_message", "subject",
}
MAX_STR = 120


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def v_ts(v):
    return v is None or (isinstance(v, str) and bool(TS_RE.match(v)))


def v_path(v):
    if v is None:
        return True
    if not isinstance(v, str) or len(v) > MAX_STR or CTRL_RE.search(v) or v.startswith("/") or ".." in v.split("/"):
        return False
    return len([c for c in v.split("/") if c]) <= 2


def v_name(v):
    return isinstance(v, str) and bool(NAME_RE.match(v)) and "@" not in v


def v_token(v):
    return v is None or (isinstance(v, str) and bool(TOKEN_RE.match(v)))


def v_bool(v):
    return isinstance(v, bool)


def v_session(v):
    return isinstance(v, str) and bool(UUID_RE.match(v) or HEX40.match(v) or REF_RE.match(v))


def v_tools(v):
    return isinstance(v, dict) and len(v) <= 40 and all(
        isinstance(k, str) and TOKEN_RE.match(k) and is_int(n) for k, n in v.items())


def v_models(v):
    return isinstance(v, list) and len(v) <= 24 and all(v_name(x) for x in v)


def v_hosts(v):
    return isinstance(v, list) and all(x in HOSTS for x in v)


def v_str_short(v):
    return v is None or (isinstance(v, str) and len(v) <= 48 and not CTRL_RE.search(v) and "@" not in v)


M_SESSION = {"session": v_session, "sidechain": v_bool, "source": lambda v: v in ("live", "zip", "linux"),
             "tools": v_tools, "model": v_models, "hosts": v_hosts, "archived": v_bool, "voice": v_bool,
             "branches": v_bool, "user_n": is_int, "assistant_n": is_int, "cli_version": v_str_short,
             "provider": v_str_short, "tool_calls": is_int}

PER_SRC = {
    "git_repo": {"kinds": {"commit", "repo_born", "branch", "worktree"}, "mag": {"n", "files", "ins", "del"},
                 "meta": {"human_authored": v_bool, "files_capped": v_bool, "no_numstat": v_bool,
                          "unresolved": v_bool, "hosts": v_hosts}},
    "fs_births": {"kinds": {"file_birth", "file_update"}, "mag": {"n", "bytes"},
                  "meta": {"bulk_copy": v_bool, "birth_missing": v_bool, "hosts": v_hosts}},
    "claude_jsonl": {"kinds": {"chat_msg", "chat_session"},
                     "mag": {"n", "tokens_in", "tokens_out", "tokens_cache", "duration_s", "tool_calls"},
                     "meta": M_SESSION},
    "codex_jsonl": {"kinds": {"chat_msg", "chat_session"},
                    "mag": {"n", "tokens_in", "tokens_out", "tokens_cache", "duration_s", "tool_calls"},
                    "meta": M_SESSION},
    "chatgpt_export": {"kinds": {"chat_msg", "chat_session"}, "mag": {"n", "duration_s", "tokens_in", "tokens_out"},
                       "meta": M_SESSION},
    "opencode_db": {"kinds": {"chat_msg", "chat_session"},
                    "mag": {"n", "tokens_in", "tokens_out", "tokens_cache", "duration_s"}, "meta": M_SESSION},
    "hearth_ledger": {"kinds": {"offload_call"}, "mag": {"n", "tokens_in", "tokens_out", "duration_ms"},
                      "meta": {"tool": v_token, "ok": v_bool, "task_class": v_token, "backend": v_token,
                               "routed_by": v_token, "outcome": v_token, "error_code": v_token,
                               "caller": v_token, "hosts": v_hosts}},
    "continuity": {"kinds": {"receipt", "run", "offload_call"},
                   "mag": {"n", "tokens_in", "tokens_out", "duration_ms", "files", "bytes"},
                   "meta": {"type": v_token, "runner": v_token, "backend": v_token, "task_kind": v_token,
                            "outcome": v_token, "hosts": v_hosts}},
    "deepagents_runs": {"kinds": {"run", "offload_call"},
                        "mag": {"n", "tokens_in", "tokens_out", "duration_ms", "files", "bytes"},
                        "meta": {"type": v_token, "backend": v_token, "task_kind": v_token, "outcome": v_token,
                                 "hosts": v_hosts}},
    "github_api": {"kinds": {"repo_born"}, "mag": {"n", "kb"},
                   "meta": {"fork": v_bool, "private": v_bool, "language": v_str_short, "pushed": v_ts}},
}
MERGED_SRC = "merged"


def _src_spec(src):
    if src == MERGED_SRC:
        spec = {"kinds": KINDS, "mag": set(), "meta": {}}
        for s in PER_SRC.values():
            spec["mag"] |= s["mag"]
            spec["meta"].update(s["meta"])
        return spec
    return PER_SRC.get(src)


def validate_event(rec):
    """List of violation codes 'key:code' (never values)."""
    errs = []
    if not isinstance(rec, dict):
        return ["record:not_object"]
    for k in rec:
        if k not in EVENT_KEYS:
            errs.append("%s:unknown_key" % k[:40])
    for k in REQUIRED:
        if k not in rec:
            errs.append("%s:missing" % k)
    spec = _src_spec(rec.get("src"))
    if spec is None:
        errs.append("src:unknown")
        spec = {"kinds": KINDS, "mag": set(), "meta": {}}
    for k in ("ts", "ts_author", "ts_commit"):
        if k in rec and not v_ts(rec[k]):
            errs.append("%s:bad_ts" % k)
    if rec.get("kind") not in KINDS or rec.get("kind") not in spec["kinds"]:
        errs.append("kind:bad")
    a = rec.get("actor")
    if not (isinstance(a, dict) and set(a) == {"class", "name"} and a["class"] in CLASSES and v_name(a["name"])):
        errs.append("actor:bad")
    if "role" in rec and rec["role"] not in ROLES:
        errs.append("role:bad")
    if rec.get("host") not in HOSTS:
        errs.append("host:bad")
    if rec.get("repo") is not None and not (isinstance(rec["repo"], str) and REPO_RE.match(rec["repo"])):
        errs.append("repo:bad")
    if rec.get("repo_local") is not None and not (isinstance(rec["repo_local"], str)
                                                  and REPO_LOCAL_RE.match(rec["repo_local"])):
        errs.append("repo_local:bad")
    if "path" in rec and not v_path(rec["path"]):
        errs.append("path:bad")
    if "files" in rec and not (isinstance(rec["files"], list) and len(rec["files"]) <= 200
                               and all(isinstance(x, str) and v_path(x) for x in rec["files"])):
        errs.append("files:bad")
    m = rec.get("magnitude")
    if not (isinstance(m, dict) and "n" in m and set(m) <= spec["mag"] | {"n"}
            and all(v is None or is_int(v) for v in m.values())):
        errs.append("magnitude:bad")
    if not (isinstance(rec.get("ref"), str) and REF_RE.match(rec["ref"])):
        errs.append("ref:bad")
    if "meta" in rec:
        mt = rec["meta"]
        if not isinstance(mt, dict):
            errs.append("meta:bad")
        else:
            for k, v in mt.items():
                fn = spec["meta"].get(k)
                if fn is None:
                    errs.append("meta.%s:unknown_key" % k[:30])
                elif not fn(v):
                    errs.append("meta.%s:bad" % k[:30])
    return errs


REPO_KEYS = {"repo_local", "host", "path", "remotes", "roots", "root_tree", "tip_tree", "shallow", "shallow_boundary",
             "is_bare", "is_worktree", "common_dir", "empty", "first_ts", "last_ts", "commits", "refs", "authors",
             "third_party", "derek_share"}


def validate_repo(rec):
    errs = []
    if not isinstance(rec, dict):
        return ["record:not_object"]
    for k in rec:
        if k not in REPO_KEYS:
            errs.append("%s:unknown_key" % k[:40])
    for k in REPO_KEYS:
        if k not in rec:
            errs.append("%s:missing" % k)
    if errs:
        return errs
    chk = [
        ("repo_local", isinstance(rec["repo_local"], str) and bool(REPO_LOCAL_RE.match(rec["repo_local"]))),
        ("host", rec["host"] in HOSTS),
        ("path", isinstance(rec["path"], str) and len(rec["path"]) <= MAX_STR and not CTRL_RE.search(rec["path"])),
        ("remotes", isinstance(rec["remotes"], list) and all(
            isinstance(u, str) and len(u) <= MAX_STR and "@" not in u and not CTRL_RE.search(u) for u in rec["remotes"])),
        ("roots", isinstance(rec["roots"], list) and all(isinstance(x, str) and HEX40.match(x) for x in rec["roots"])),
        ("root_tree", rec["root_tree"] is None or bool(HEX40.match(str(rec["root_tree"])))),
        ("tip_tree", rec["tip_tree"] is None or bool(HEX40.match(str(rec["tip_tree"])))),
        ("shallow_boundary", isinstance(rec["shallow_boundary"], list) and all(
            isinstance(x, str) and HEX40.match(x) for x in rec["shallow_boundary"])),
        ("flags", all(isinstance(rec[k], bool) for k in ("shallow", "is_bare", "is_worktree", "empty", "third_party"))),
        ("common_dir", rec["common_dir"] is None or (isinstance(rec["common_dir"], str)
                                                     and len(rec["common_dir"]) <= MAX_STR)),
        ("ts", v_ts(rec["first_ts"]) and v_ts(rec["last_ts"])),
        ("counts", is_int(rec["commits"]) and is_int(rec["refs"])),
        ("authors", isinstance(rec["authors"], dict) and all(k in CLASSES and is_int(v) for k, v in rec["authors"].items())),
        ("derek_share", is_num(rec["derek_share"]) and 0 <= rec["derek_share"] <= 1),
    ]
    return ["%s:bad" % k for k, ok in chk if not ok]


MANIFEST_KEYS = {"item", "src", "started", "finished", "status", "events", "events_sha256", "repos", "dropped",
                 "coverage", "warnings", "sources", "slices"}


def validate_manifest(rec):
    errs = []
    if not isinstance(rec, dict):
        return ["manifest:not_object"]
    for k in rec:
        if k not in MANIFEST_KEYS:
            errs.append("%s:unknown_key" % k[:40])
    if rec.get("status") not in ("complete", "partial", "failed"):
        errs.append("status:bad")
    if not isinstance(rec.get("warnings"), list):
        errs.append("warnings:bad")
    srcs = rec.get("sources", [])
    if not (isinstance(srcs, list) and all(isinstance(s, dict) and set(s) <= {"label", "kind", "raw"} for s in srcs)):
        errs.append("sources:bad")
    return errs


def scan_value(v, path="", errs=None, depth=0):
    """Generic recursive scan: forbidden keys, long strings, emails, secret shapes."""
    if errs is None:
        errs = []
    if depth > 8:
        errs.append("%s:too_deep" % path[:40])
        return errs
    if isinstance(v, dict):
        for k, x in v.items():
            if isinstance(k, str) and k in FORBIDDEN_KEYS:
                errs.append("%s:forbidden_key" % k[:40])
            scan_value(x, k if isinstance(k, str) else "?", errs, depth + 1)
    elif isinstance(v, list):
        for x in v:
            scan_value(x, path, errs, depth + 1)
    elif isinstance(v, str):
        if len(v) > MAX_STR:
            errs.append("%s:long_string" % path[:40])
        if EMAIL_RE.search(v):
            errs.append("%s:email" % path[:40])
        for rx in SECRET_RES:
            if rx.search(v):
                errs.append("%s:secret_shape" % path[:40])
                break
    return errs
