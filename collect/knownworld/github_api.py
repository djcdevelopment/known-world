"""github_api.py: the GitHub repository list (names, flags, sizes, dates) -> repo_born events + github_repos.json.

Authenticated (`gh auth status` succeeds): `gh repo list <owner> --limit 400 --json ...` for the owner and the
configured orgs. Otherwise the unauthenticated public list through curl, at most 2 requests, with the warning
'pending auth: private repos not listed'. Tokens are never read or printed; gh and curl use their own stores.
"""
import json
import os
import re
import shutil

from knownworld import core

SRC = "github_api"
GH_FIELDS = "id,name,isPrivate,isFork,createdAt,pushedAt,diskUsage,primaryLanguage,url"


def enumerate_sources(ctx):
    return [{"label": "github-list", "kind": "api", "shard_key": "github", "spec": {}}]


def _gh():
    p = shutil.which("gh") or os.path.expanduser("~/.local/bin/gh")
    return p if os.path.exists(p) else None


def _env():
    e = dict(os.environ)
    e["GH_PROMPT_DISABLED"] = "1"
    e["GH_NO_UPDATE_NOTIFIER"] = "1"
    e["NO_COLOR"] = "1"
    return e


def _tok(v):
    return v[:48] if isinstance(v, str) and re.match(r"^[A-Za-z0-9_.+#\-]{1,48}$", v) else None


def process_source(ctx, src, cursor):
    opts = ctx.item.get("options") or {}
    owner = opts.get("owner", "djcdevelopment")
    orgs = opts.get("orgs", ["steppe-integrations"])
    rows, authed = [], False
    gh = _gh()
    if gh:
        rc, _, _, to = core.run([gh, "auth", "status"], 30, env=_env())
        authed = rc == 0 and not to
    if authed:
        for who in [owner] + list(orgs):
            rc, out, _, to = core.run([gh, "repo", "list", who, "--limit", "400", "--json", GH_FIELDS], 120, env=_env())
            if rc != 0 or to:
                ctx.warn("gh_list_failed:" + core.clip(who, 30))
                continue
            try:
                for r in json.loads(out):
                    rows.append({"node": r.get("id"), "name": r.get("name"), "owner": who, "url": r.get("url"),
                                 "private": r.get("isPrivate"), "fork": r.get("isFork"),
                                 "size_kb": r.get("diskUsage"), "created": r.get("createdAt"),
                                 "pushed": r.get("pushedAt"),
                                 "lang": (r.get("primaryLanguage") or {}).get("name") if isinstance(r.get("primaryLanguage"), dict) else None})
            except ValueError:
                ctx.drop("decode_errors")
        if not rows:
            return {"status": "skipped", "reason": "gh_list_empty"}
    else:
        ctx.warn("pending auth: private repos not listed")
        urls = ["https://api.github.com/users/%s/repos?per_page=100&type=owner" % owner]
        if orgs:
            urls.append("https://api.github.com/orgs/%s/repos?per_page=100" % orgs[0])
        for i, u in enumerate(urls[:2]):
            rc, out, _, to = core.run(["curl", "-sS", "-m", "40", "-H", "Accept: application/vnd.github+json",
                                       "-H", "User-Agent: knownworld-collector", u], 60, env=dict(os.environ))
            if rc != 0 or to:
                ctx.warn("curl_failed:%d" % i)
                continue
            try:
                data = json.loads(out)
            except ValueError:
                ctx.drop("decode_errors")
                continue
            if not isinstance(data, list):
                ctx.warn("api_not_list:%d" % i)  # rate limited or not found
                continue
            who = owner if i == 0 else orgs[0]
            for r in data:
                if not isinstance(r, dict):
                    continue
                rows.append({"node": r.get("node_id"), "name": r.get("name"), "owner": who, "url": r.get("html_url"),
                             "private": bool(r.get("private")), "fork": bool(r.get("fork")), "size_kb": r.get("size"),
                             "created": r.get("created_at"), "pushed": r.get("pushed_at"), "lang": r.get("language")})
        if not rows:
            return {"status": "skipped", "reason": "no_rows_unauthenticated"}
    listing = []
    for r in rows:
        if not isinstance(r["name"], str) or not re.match(r"^[A-Za-z0-9_.\-]{1,100}$", r["name"]):
            continue
        created = core.clean_ts(r["created"])
        pushed = core.clean_ts(r["pushed"])
        kb = r["size_kb"] if isinstance(r["size_kb"], int) and r["size_kb"] >= 0 else None
        listing.append({"name": r["name"], "url": core.clip(core.norm_remote(r["url"] or ""), 120), "private": bool(r["private"]),
                        "fork": bool(r["fork"]), "size_kb": kb, "created": created, "pushed": pushed})
        if created is None:
            ctx.drop("null_ts")
        node = r["node"]
        ref = node if isinstance(node, str) and re.match(r"^[A-Za-z0-9_.:=\-]{1,80}$", node) else core.sha1hex("gh|%s/%s" % (r["owner"], r["name"]))
        meta = {"fork": bool(r["fork"]), "private": bool(r["private"])}
        lang = _tok(r["lang"])
        if lang:
            meta["language"] = lang
        if pushed:
            meta["pushed"] = pushed
        ctx.emit({"ts": created, "kind": "repo_born", "actor": {"class": "human", "name": "derek"}, "host": "github",
                  "repo": None, "repo_local": "github:%s/%s" % (r["owner"], r["name"]), "path": None,
                  "magnitude": {"n": 1, "kb": kb}, "ref": ref, "src": SRC, "meta": meta})
    ctx.log("github list authenticated=%s rows=%d" % (authed, len(listing)))
    out_path = os.path.join(ctx.out_dir, "github_repos.json")
    tmp = out_path + ".tmp"
    core.guard_write(out_path)
    with open(tmp, "w") as f:
        json.dump(listing, f, indent=0)
    os.replace(tmp, out_path)
    return {"status": "done", "raw": len(rows)}
