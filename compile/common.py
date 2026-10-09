"""Shared helpers for the Known World compile layer: deterministic IO, hashing, time parsing, params."""
import calendar
import hashlib
import json
import os
import re
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGED = os.path.join(ROOT, "corpus", "merged")
DEFAULT_PARAMS = os.path.join(ROOT, "compile", "params.json")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def dumps(obj):
    """Canonical JSON: sorted keys, fixed separators, ASCII. Same input gives the same bytes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = (dumps(obj) + "\n").encode()
    with open(path, "wb") as f:
        f.write(data)
    return sha256_bytes(data)


def load_params(path=None, overrides=None):
    p = json.load(open(path or DEFAULT_PARAMS))
    for k in list(p):
        if k.startswith("_"):
            del p[k]
    for kv in overrides or []:
        k, v = kv.split("=", 1)
        try:
            v = json.loads(v)
        except ValueError:
            pass
        p[k] = v
    return p


def params_hash(p):
    return sha256_bytes(dumps(p).encode())


_TS = re.compile(r"^(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)")


def parse_ts(s):
    """UTC ISO-8601 string to integer epoch seconds."""
    m = _TS.match(s)
    y, mo, d, h, mi, se = map(int, m.groups())
    return calendar.timegm((y, mo, d, h, mi, se))


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(t)))


def day_epoch(datestr):
    y, m, d = map(int, datestr.split("-"))
    return calendar.timegm((y, m, d, 0, 0, 0))


def corpus_inputs():
    names = ["events.ndjson", "repos.json", "sessions.json", "hosts.json", "actors.json", "stats.json",
             "relations.json", "chatgpt_links.json"]
    out = {}
    for n in names:
        p = os.path.join(MERGED, n)
        out[n] = sha256_file(p) if os.path.exists(p) else None
    return out
