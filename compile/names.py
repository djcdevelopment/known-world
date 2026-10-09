"""Canonical generation names (STRATEGY 4.2.8). `claude-opus-4.7` = `opus-4.7` = `claude-opus-4-7`; seats map to models."""
import re

_DATE = re.compile(r"-20\d{6}$")


def canon_minor(name, cls=None):
    """Return a family-version name with dots (opus-4.7), or None when the string names no generation."""
    if not name:
        return None
    n = str(name).lower().strip()
    if n in ("auto", "none", "claude", "codex", "derek", "unknown", "default"):
        return None
    n = _DATE.sub("", n)
    n = re.sub(r"^claude[-_]", "", n)
    n = re.sub(r"[:@].*$", "", n) if n.startswith("qwen") is False else n
    m = re.match(r"^(opus|sonnet|haiku|fable)(?:-(\d+)(?:[-.](\d+))?)?", n)
    if m:
        fam, a, b = m.groups()
        return fam if a is None else (f"{fam}-{a}.{b}" if b is not None else f"{fam}-{a}")
    m = re.match(r"^gpt-?(\d+)(?:[-.](\d+))?", n)
    if m:
        a, b = m.groups()
        return f"gpt-{a}.{b}" if b is not None else f"gpt-{a}"
    return n


def canon(name, granularity="major"):
    g = canon_minor(name)
    if g is None or granularity == "off":
        return None
    if not re.search(r"\d", g):
        return None  # an unversioned trailer (opus, sonnet, ct) names no generation: no chip
    if granularity == "minor":
        return g
    m = re.match(r"^(opus|sonnet|haiku|fable|gpt)-(\d+)", g)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return g


def seat_model(backend, seat_models):
    if backend in seat_models:
        return seat_models[backend]
    return backend


def label_words(g):
    """A generation in words for the border: opus-4.5 -> 'opus 4.5', qwen3-30b-a3b -> 'qwen3 30b'; gpt keeps its hyphen."""
    if g.startswith("gpt-"):
        return g
    g = re.sub(r"-a\d+b$", "", g)
    return g.replace("-", " ")


def label_short(g):
    m = re.match(r"^([a-z]+)[- ]?(\d+(?:\.\d+)?)", g)
    return (m.group(1)[0] + m.group(2)) if m else g[:4]
