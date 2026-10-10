"""Extract native job IDs from lab evidence; no inference or source writes."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('/home/derek/work/lab-rnd/research/evidence')
JOB = re.compile(r'job_[0-9a-f]{32}')
SKIP = {'prompt', 'brief', 'text', 'content', 'body', 'messages', 'report',
        'answer', 'answers', 'source', 'output', 'reason', 'summary', 'criteria'}


def ids(value, depth=0):
    if depth > 8:
        return set()
    found = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == 'job_id' and isinstance(child, str) and JOB.fullmatch(child):
                found.add(child)
            elif key not in SKIP:
                found.update(ids(child, depth + 1))
    elif isinstance(value, list):
        for child in value:
            found.update(ids(child, depth + 1))
    return found


def collect():
    jobs, other = {}, {}
    for p in sorted(SOURCE.rglob('run.json')):
        obj = json.loads(p.read_text())
        found = ids(obj)
        if obj.get('schema') != 'thinking-run.v1':
            for name in ('work.json', 'calls.json', 'delivery.json', 'output.json'):
                sibling = p.parent / name
                if sibling.is_file():
                    found.update(ids(json.loads(sibling.read_text())))
            other[str(p.relative_to(SOURCE))] = len(found)
        for job in sorted(found):
            jobs.setdefault(job, []).append(str(p.relative_to(SOURCE)))
    return {'source_root': str(SOURCE), 'jobs': jobs, 'other_run_job_counts': other}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = Path(args.out).resolve()
    if not out.is_relative_to(ROOT / 'corpus/activity') or out.exists():
        raise SystemExit('Choose a new output under corpus/activity/')
    result = collect()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x') as f:
        json.dump(result, f, indent=1)
        f.write('\n')
    print(json.dumps({'jobs': len(result['jobs']), 'other_runs': len(result['other_run_job_counts'])}))
