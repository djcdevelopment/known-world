"""fs_find.py: the read-only `find ... -exec stat` walk shared by fs_births.py and the ssh shipper (CONTRACT.md 1, 6).

Self-contained (stdlib only, no knownworld imports) so remote.py can ship it alone over ssh stdin. Prints, NUL
separated, `birth|mtime|size|path` for every regular file under a root; birth is 0 where the filesystem has none.
Prune and exclusion lists are the never-walk and credential lists of CONTRACT.md section 6.
"""
import os
import subprocess
import sys

PRUNE_NAMES = [".git", "node_modules", "models", "checkpoints", "venvs", ".venv", ".cache"]
EXCLUDE_NAMES = [".credentials.json", "auth.json", "callers.json*", "*.pfx", "*.secret", "*.key", ".env*", "*.caddy",
                 ".git-credentials", "*.safetensors", "*.gguf", "*.pem"]


def find_argv(path, loose):
    if loose:
        argv = ["find", path, "-maxdepth", "1", "-type", "f"]
    else:
        prune = []
        for n in PRUNE_NAMES:
            prune += ["-name", n, "-o"]
        prune += ["-path", "*/ComfyUI/models"]
        argv = ["find", path, "-xdev", "(", "-type", "d", "(", *prune, ")", "-prune", ")", "-o", "-type", "f"]
    for n in EXCLUDE_NAMES:
        argv += ["!", "-name", n]
    return argv + ["-exec", "stat", "--printf", "%W|%Y|%s|%n\\0", "--", "{}", "+"]


def _walk_fallback(path, loose):
    """No GNU find or stat: mtime only (birth 0). Same exclusions."""
    import fnmatch
    out = sys.stdout.buffer
    for root, dirs, files in os.walk(path):
        dirs[:] = sorted(d for d in dirs if d not in PRUNE_NAMES and not (root.endswith("/ComfyUI") and d == "models"))
        for f in sorted(files):
            if any(fnmatch.fnmatch(f, p) for p in EXCLUDE_NAMES):
                continue
            p = os.path.join(root, f)
            try:
                st = os.lstat(p)
            except OSError:
                continue
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            b = getattr(st, "st_birthtime", 0) or 0
            out.write(("%d|%d|%d|%s" % (b, st.st_mtime, st.st_size, p)).encode("utf-8", "surrogateescape") + b"\0")
        if loose:
            break
    out.flush()


def _remote_main(args):
    """Shipped over ssh with KW_ARGS: {"cmd": "discover"|"walk", ...}. Read-only."""
    if args["cmd"] == "discover":
        import json
        res = []
        for r in args["roots"]:
            p = os.path.normpath(os.path.expanduser(r))
            res.append({"path": p, "isdir": os.path.isdir(p), "islink": os.path.islink(p)})
        print(json.dumps({"home": os.path.expanduser("~"), "roots": res}))
        return 0
    sys.stdout.flush()
    try:
        rc = subprocess.run(find_argv(args["path"], args["loose"]), stdin=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, timeout=args["timeout"]).returncode
    except FileNotFoundError:
        _walk_fallback(args["path"], args["loose"])
        return 0
    except subprocess.TimeoutExpired:
        return 124
    return 0 if rc in (0, 1) else rc


if __name__ == "__main__" and "KW_ARGS" in globals():
    sys.exit(_remote_main(KW_ARGS))  # noqa: F821
