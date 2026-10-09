"""remote.py: ship a self-contained read-only script to an ssh host through stdin (CONTRACT.md section 6)."""
import json
import os

from knownworld import core

SSH_ADDR = {"am4": "10.44.0.2", "fx99": "100.122.130.124"}
HERE = os.path.dirname(os.path.abspath(__file__))
SSH_BASE = ["ssh", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-o", "ServerAliveInterval=15",
            "-o", "ServerAliveCountMax=4"]


def build_script(args, modules):
    parts = ["import json as _json\nKW_ARGS = _json.loads(%r)\n" % json.dumps(args)]
    for m in modules:
        with open(os.path.join(HERE, m), "r", encoding="utf-8") as f:
            parts.append(f.read())
    return "\n".join(parts).encode("utf-8")


def ssh_stream(host, args, timeout, modules=("core.py", "git_repo.py")):
    """Stream of the remote script's stdout lines. Remote commands are read-only; BatchMode=yes always."""
    addr = SSH_ADDR[host]
    argv = SSH_BASE + [addr, "python3", "-"]
    return core.Stream(argv, timeout, env=dict(os.environ), stdin_bytes=build_script(args, modules))
