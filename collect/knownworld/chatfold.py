"""chatfold.py: per-session folding of chat traffic into chat_msg / chat_session records (CONTRACT.md section 1).

One chat_msg per (session, role, minute) with n = messages folded, one chat_session per session. Only counts,
timestamps, model names, tool names and token numbers pass through; no text ever reaches this module.
"""
from collections import Counter

from knownworld import core


def safe_tool(name):
    import re
    return name if isinstance(name, str) and re.match(r"^[A-Za-z0-9_.:\-]{1,64}$", name) else "other"


def safe_model(name):
    import re
    if isinstance(name, str) and re.match(r"^[A-Za-z0-9._:/\-]{1,64}$", name) and not name.startswith("<"):
        return name
    return None


class Fold:
    def __init__(self):
        self.b = {}
        self.models = Counter()
        self.first = None
        self.last = None
        self.nmsg = 0
        self.req_home = {}

    def add(self, role, epoch, model=None, tin=None, tout=None, tcache=None, tools=None, req=None, n=1):
        if epoch is None:
            return
        if self.first is None or epoch < self.first:
            self.first = epoch
        if self.last is None or epoch > self.last:
            self.last = epoch
        model = safe_model(model)
        key = "%s|%d" % (role, epoch - epoch % 60)
        bk = self.b.get(key)
        if bk is None:
            bk = self.b[key] = {"n": 0, "tin": None, "tout": None, "tcache": None, "tools": {}, "models": {},
                                "reqs": {}}
        if model:
            self.models[model] += 1
            bk["models"][model] = bk["models"].get(model, 0) + 1
        for name, c in (tools or {}).items():
            bk["tools"][name] = bk["tools"].get(name, 0) + c
        toks = (tin, tout, tcache)
        bk["n"] += n
        self.nmsg += n
        if req is not None:
            home = self.req_home.get(req)
            if home is None:
                self.req_home[req] = key
                bk["reqs"][req] = list(toks)
            else:
                hb = self.b[home]
                prev = hb["reqs"][req]
                hb["reqs"][req] = [max(a or 0, b or 0) if (a is not None or b is not None) else None
                                   for a, b in zip(prev, toks)]
        else:
            for i, k in enumerate(("tin", "tout", "tcache")):
                if toks[i] is not None:
                    bk[k] = (bk[k] or 0) + toks[i]

    def to_state(self):
        return {"b": self.b, "models": dict(self.models), "first": self.first, "last": self.last, "nmsg": self.nmsg}

    @classmethod
    def from_state(cls, s):
        f = cls()
        f.b, f.models, f.first, f.last, f.nmsg = s["b"], Counter(s["models"]), s["first"], s["last"], s["nmsg"]
        return f

    def primary_model(self):
        return self.models.most_common(1)[0][0] if self.models else None

    def events(self, src, cls, default_name, host, path, session, stem, sidechain=False, source=None, extra_meta=None,
               emit_session=True):
        out = []
        pm = self.primary_model() or default_name
        for key, bk in sorted(self.b.items()):
            role, minute = key.split("|")
            minute = int(minute)
            tin, tout, tcache = bk["tin"], bk["tout"], bk["tcache"]
            if bk["reqs"]:
                vals = list(bk["reqs"].values())
                tin = sum(v[0] or 0 for v in vals) if any(v[0] is not None for v in vals) else None
                tout = sum(v[1] or 0 for v in vals) if any(v[1] is not None for v in vals) else None
                tcache = sum(v[2] or 0 for v in vals) if any(v[2] is not None for v in vals) else None
            name = (max(bk["models"].items(), key=lambda kv: kv[1])[0] if (role == "assistant" and bk["models"])
                    else pm)
            mag = {"n": bk["n"], "tokens_in": tin, "tokens_out": tout}
            if tcache is not None:
                mag["tokens_cache"] = tcache
            tc = sum(bk["tools"].values())
            if tc:
                mag["tool_calls"] = tc
            meta = {"session": session}
            if sidechain:
                meta["sidechain"] = True
            if bk["tools"]:
                top = dict(sorted(bk["tools"].items(), key=lambda kv: -kv[1])[:30])
                meta["tools"] = top
            ev = {"ts": core.iso(minute) if core.good_epoch(minute) else None, "kind": "chat_msg",
                  "actor": {"class": cls, "name": name}, "role": role, "host": host, "repo": None, "path": path,
                  "magnitude": mag, "ref": core.sha1hex("%s|%s|%s|%d" % (session, stem, role, minute)),
                  "src": src, "meta": meta}
            out.append(ev)
        if self.first is not None and emit_session:
            meta = {"session": session}
            if sidechain:
                meta["sidechain"] = True
            ms = [m for m, _ in self.models.most_common(12)]
            if ms:
                meta["model"] = ms
            if source:
                meta["source"] = source
            if extra_meta:
                meta.update(extra_meta)
            out.append({"ts": core.iso(self.first) if core.good_epoch(self.first) else None, "kind": "chat_session",
                        "actor": {"class": cls, "name": pm}, "host": host, "repo": None, "path": path,
                        "magnitude": {"n": self.nmsg, "duration_s": max(0, (self.last or 0) - self.first)},
                        "ref": core.sha1hex("sess|%s|%s" % (session, stem)), "src": src, "meta": meta})
        return out
