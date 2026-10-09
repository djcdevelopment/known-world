"""core.py: shared helpers for the Known World collectors.

Pure stdlib, Python 3.12+ syntax only, no relative imports: this file is also shipped (concatenated with
git_repo.py) to ssh hosts through stdin, so it must stay self-contained.
Everything here is mechanical policy from CONTRACT.md section 6: environment, subprocess timeouts, credential and
never-walk exclusion, timestamp cleaning, remote-url normalisation, identity classification.
"""
import hashlib
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone

KW_ROOT = "/home/derek/work/known-world"
HOME = os.path.expanduser("~")
MIN_EPOCH = 1104537600  # 2005-01-01T00:00:00Z
MOUNTS = {"/mnt/omen-c-read": "omen-c", "/mnt/omen-e-read": "omen-e"}

GIT_ENV = {
    "PYTHONDONTWRITEBYTECODE": "1",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_NO_LAZY_FETCH": "1",
    "GIT_PAGER": "cat",
    "GIT_CONFIG_COUNT": "1",
    "GIT_CONFIG_KEY_0": "safe.directory",
    "GIT_CONFIG_VALUE_0": "*",
    "LC_ALL": "C.UTF-8",
}


def setup_env():
    os.environ.update(GIT_ENV)
    return dict(os.environ)


# ---------------------------------------------------------------- hashing / strings

def sha1hex(s):
    if isinstance(s, str):
        s = s.encode("utf-8", "replace")
    return hashlib.sha1(s).hexdigest()


def sha1_12(s):
    return sha1hex(s)[:12]


def clip(s, n=120):
    s = "" if s is None else str(s)
    return s if len(s) <= n else s[:n]


def slug(name, n=64):
    s = re.sub(r"\([^)]*\)", " ", str(name).lower())
    s = re.sub(r"[^a-z0-9.]+", "-", s).strip("-.")
    return s[:n] or "unknown"


# ---------------------------------------------------------------- timestamps

def iso(epoch):
    return datetime.fromtimestamp(int(epoch), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def to_epoch(x):
    """Number or ISO string -> int epoch seconds, or None. Milliseconds are detected."""
    if x is None or isinstance(x, bool):
        return None
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return None
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        except ValueError:
            try:
                x = float(s)
            except ValueError:
                return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if v != v or v in (float("inf"), float("-inf")):
        return None
    if v > 1e11:
        v /= 1000.0
    return int(v)


def good_epoch(e, now=None):
    """Contract section 1: null when before 2005-01-01, after now, or a placeholder."""
    if e is None:
        return None
    now = int(time.time()) if now is None else now
    if e < MIN_EPOCH or e > now + 120:
        return None
    return int(e)


def clean_ts(x, now=None):
    e = good_epoch(to_epoch(x), now)
    return None if e is None else iso(e)


def minute_bucket(epoch):
    return iso(int(epoch) - int(epoch) % 60)


def day_of(epoch):
    return datetime.fromtimestamp(int(epoch), timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------- credential and walk exclusion

CRED_NAME_RE = re.compile(
    r"^(\.credentials\.json|auth\.json|callers\.json.*|\.git-credentials|\.netrc|\.npmrc|id_(rsa|ed25519|ecdsa|dsa).*"
    r"|\.env.*|.*\.(pfx|secret|key|caddy|pem|p12))$", re.I)
SKIP_DIR_NAMES = {"models", "checkpoints", "venvs", ".venv", "node_modules", ".cache"}
SKIP_FILE_SUFFIX = (".safetensors", ".gguf")


def is_credential_name(name):
    return bool(CRED_NAME_RE.match(os.path.basename(name.rstrip("/"))))


def _norm(p):
    return os.path.normpath(os.path.expanduser(p))


def is_never_walk(path):
    p = _norm(path)
    parts = p.split(os.sep)
    if any(c in SKIP_DIR_NAMES for c in parts):
        return True
    if p.endswith(SKIP_FILE_SUFFIX):
        return True
    if "ComfyUI/models" in p:
        return True
    var = os.path.join(HOME, "hearth-production", "var")
    if p == var or p.startswith(var + os.sep):
        led = os.path.join(var, "ledger")
        return not (p == led or p.startswith(led + os.sep))
    scratch = os.path.join(HOME, "work", "amux", "scratch")
    return p == scratch or p.startswith(scratch + os.sep)


def guard_read(path):
    """Raise before any explicit read of a credential-bearing or never-walk path."""
    if any(is_credential_name(c) for c in _norm(path).split(os.sep) if c):
        raise PermissionError("credential path refused")
    if is_never_walk(path):
        raise PermissionError("never-walk path refused")
    return path


def guard_write(path):
    p = os.path.realpath(os.path.expanduser(path))
    if not (p == KW_ROOT or p.startswith(KW_ROOT + os.sep)):
        raise PermissionError("write outside known-world refused")
    for c in p.split(os.sep):
        if c.startswith("jepa-") or c == "hybrid-context-trial" or c == "runs":
            raise PermissionError("write into immutable directory refused")
    if p.startswith("/mnt/"):
        raise PermissionError("write into mount refused")
    return p


# ---------------------------------------------------------------- host / path display

def host_and_rel(abs_path, default_host="omen-linux"):
    """Absolute local path -> (host id, display path). Mount paths are drive-relative; $HOME paths are ~-relative."""
    p = os.path.normpath(abs_path)
    for m, h in MOUNTS.items():
        if p == m:
            return h, ""
        if p.startswith(m + "/"):
            return h, p[len(m) + 1:]
    if p == HOME:
        return default_host, "~"
    if p.startswith(HOME + "/"):
        return default_host, "~/" + p[len(HOME) + 1:]
    return default_host, p


def repo_local(host, disp):
    return "%s:%s" % (host, disp)


def drive_to_host(letter):
    l = (letter or "").upper()
    if l == "C":
        return "omen-c"
    if l in ("D", "E"):
        return "omen-e"
    return None


def win_path_to_mount(p):
    """'C:/work/x' or 'C:\\work\\x' -> '/mnt/omen-c-read/work/x' or None."""
    m = re.match(r"^([A-Za-z]):[\\/]*(.*)$", p.strip())
    if not m:
        return None
    h = drive_to_host(m.group(1))
    if h is None:
        return None
    base = "/mnt/omen-c-read" if h == "omen-c" else "/mnt/omen-e-read"
    return os.path.join(base, m.group(2).replace("\\", "/")).rstrip("/")


def depth2(rel):
    """Directory path clipped to depth 2 ('.' for the root)."""
    comps = [c for c in rel.replace("\\", "/").split("/") if c and c != "."]
    return "/".join(comps[:2]) if comps else "."


def surface_path(cwd):
    """A working directory as written by an agent -> (host or None, surface-relative path clipped to depth 2)."""
    c = cwd.strip()
    m = re.match(r"^([A-Za-z]):[\\/]*(.*)$", c)
    if m:
        return drive_to_host(m.group(1)), clip(depth2(m.group(2)), 120)
    if c.startswith(HOME + "/") or c == HOME:
        return None, clip(depth2(c[len(HOME):]), 120)
    if c.startswith("/home/") or c.startswith("/Users/"):
        parts = c.split("/")
        return None, clip(depth2("/".join(parts[3:])), 120)
    return None, clip(depth2(c.lstrip("/")), 120)


# ---------------------------------------------------------------- remotes

def norm_remote(url):
    u = (url or "").strip()
    if not u:
        return None
    m = re.match(r"^(?:[\w.\-]+@)?([\w.\-]+):(?!//)(?!\d+/)(?P<path>[^\s]+)$", u)
    if m and "://" not in u and not re.match(r"^[A-Za-z]:[\\/]", u) and not u.startswith("/"):
        host, path = m.group(1).lower(), m.group("path")
        path = re.sub(r"\.git/?$", "", path.strip("/"))
        return clip("https://%s/%s" % (host, path), 120) if host in ("github.com", "gitlab.com", "bitbucket.org") \
            else clip("ssh://%s/%s" % (host, path), 120)
    if "://" in u:
        scheme, rest = u.split("://", 1)
        scheme = scheme.lower()
        if scheme == "file":
            return clip("file:" + rest.replace("\\", "/"), 120)
        netloc, _, path = rest.partition("/")
        if "@" in netloc:
            netloc = netloc.rsplit("@", 1)[1]
        netloc = netloc.lower()
        path = re.sub(r"\.git/?$", "", path.strip("/"))
        if netloc in ("github.com", "www.github.com", "gitlab.com", "bitbucket.org"):
            scheme = "https"
            netloc = netloc.replace("www.", "")
        return clip("%s://%s/%s" % (scheme, netloc, path), 120)
    return clip(re.sub(r"\.git/?$", "", u.replace("\\", "/")), 120)


def remote_org(url):
    m = re.match(r"^https://github\.com/([^/]+)/", url or "", re.I)
    return m.group(1).lower() if m else None


# ---------------------------------------------------------------- identity

class Identity:
    def __init__(self, data):
        self.humans = {h.lower() for h in data.get("human_names", [])}
        self.rules = [(re.compile(r["regex"], re.I), r["class"], r.get("name", "slug")) for r in data.get("rules", [])]
        self.derek_orgs = {o.lower() for o in data.get("derek_orgs", [])}

    def classify(self, name):
        """(class, name) for any author or trailer name; third_party carries sha1(name)[:12]."""
        n = (name or "").strip()
        if not n:
            return ("third_party", sha1_12("unknown"))
        if n.lower() in self.humans:
            return ("human", "derek")
        for rx, cls, nm in self.rules:
            if rx.search(n):
                if nm == "slug":
                    return (cls, slug(n))
                return (cls, nm)
        return ("third_party", sha1_12(n))

    def trailer(self, name):
        """Co-Authored-By name: only agent classes count; humans and unknown people are not actors."""
        cls, nm = self.classify(re.sub(r"<[^>]*>", "", name or "").strip())
        if cls in ("human", "third_party"):
            return None
        return (cls, nm)


# ---------------------------------------------------------------- subprocesses

def tmp_dir():
    d = os.path.join(KW_ROOT, "cache", "tmp")
    os.makedirs(d, exist_ok=True)
    return d


def _kill_group(p):
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def run(argv, timeout, stdin_bytes=None, env=None, cwd=None, max_out=None):
    """(rc, stdout bytes, stderr length, timed_out). The child's process group is killed on timeout."""
    errf = tempfile.TemporaryFile(dir=tmp_dir())
    try:
        p = subprocess.Popen(argv, stdin=subprocess.PIPE if stdin_bytes is not None else subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=errf, env=env, cwd=cwd, start_new_session=True)
        try:
            out, _ = p.communicate(stdin_bytes, timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_group(p)
            try:
                p.communicate(timeout=10)
            except Exception:
                pass
            return -9, b"", errf.seek(0, 2), True
        return p.returncode, out, errf.seek(0, 2), False
    finally:
        errf.close()


class Stream:
    """Line stream over a subprocess with a hard wall-clock timeout; stderr goes to a temp file (length only)."""

    def __init__(self, argv, timeout, env=None, stdin_bytes=None, cwd=None):
        self.err = tempfile.TemporaryFile(dir=tmp_dir())
        self.timed_out = False
        self.p = subprocess.Popen(argv, stdin=subprocess.PIPE if stdin_bytes is not None else subprocess.DEVNULL,
                                  stdout=subprocess.PIPE, stderr=self.err, env=env, cwd=cwd, start_new_session=True,
                                  bufsize=1 << 20)
        self._timer = threading.Timer(timeout, self._expire)
        self._timer.daemon = True
        self._timer.start()
        if stdin_bytes is not None:
            def feed():
                try:
                    self.p.stdin.write(stdin_bytes)
                    self.p.stdin.close()
                except Exception:
                    pass
            t = threading.Thread(target=feed, daemon=True)
            t.start()
        self.rc = None

    def _expire(self):
        self.timed_out = True
        _kill_group(self.p)

    def lines(self):
        rl = self.p.stdout.readline
        while True:
            line = rl()
            if not line:
                return
            yield line

    def records(self, sep=b"\0", chunk=1 << 20):
        """NUL-separated records (find -printf '...\\0')."""
        buf = b""
        rd = self.p.stdout.read1
        while True:
            data = rd(chunk)
            if not data:
                break
            buf += data
            parts = buf.split(sep)
            buf = parts.pop()
            for x in parts:
                yield x
        if buf:
            yield buf

    def close(self):
        self._timer.cancel()
        if self.p.poll() is None:
            _kill_group(self.p)
        try:
            self.p.stdout.close()
        except Exception:
            pass
        self.rc = self.p.wait()
        self.err_len = self.err.seek(0, 2)
        self.err_head = b""
        try:
            self.err.seek(0)
            self.err_head = self.err.read(400)
        except Exception:
            pass
        self.err.close()
        return self.rc


ERR_CLASSES = [
    (r"dubious ownership", "dubious_ownership"), (r"not a git repository", "not_a_repo"),
    (r"promisor|lazy fetching", "partial_clone_missing_blobs"),
    (r"bad object|unable to read|missing object|did not receive expected object", "bad_object"),
    (r"does not have any commits|unknown revision|ambiguous argument", "no_commits"),
    (r"Permission denied|Operation not permitted", "permission"), (r"Input/output error", "io_error"),
    (r"Connection (refused|timed out|reset)|Could not resolve|No route", "network"),
    (r"Too many open files", "fd_limit"),
]


def err_class(head_bytes):
    t = head_bytes.decode("utf-8", "replace")
    for rx, name in ERR_CLASSES:
        if re.search(rx, t, re.I):
            return name
    return "other" if t.strip() else "none"
