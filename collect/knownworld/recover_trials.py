"""Reconcile learned evidence shapes into frozen metadata for Known World.

Never execute source harnesses. Never retain prompts, answers or command lines.
Native repeats, configuration rows, comparative experiments and runner manifests
are different views. Their totals cannot be added into a grand work total.
"""
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess

from activity import project_index, timestamp, ROOT
from discover import excluded

DISCOVERY = ROOT / 'corpus/discovery/20261010-experimental'


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def objects(path):
    raw = path.read_bytes()
    text = raw.decode('utf-16') if raw.startswith(b'\xff\xfe') else raw.decode('utf-8-sig')
    if path.suffix == '.json':
        obj = json.loads(text)
        return obj if isinstance(obj, list) else [obj]
    out = []
    for line in text.splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def owner(path, projects):
    for prefix, host in [('/mnt/omen-c-read/', 'omen-c'), ('/mnt/omen-e-read/', 'omen-e'),
                         ('/home/derek/', 'omen-linux')]:
        if str(path).startswith(prefix):
            rel = str(path)[len(prefix):]
            key = rel if host != 'omen-linux' else '~/' + rel
            matches = [(len(p), lid) for (h, p), lid in projects.items()
                       if h == host and (key.casefold() if host != 'omen-linux' else key).startswith(p + '/')]
            if matches:
                return host, max(matches)[1]
    return None, None


def recover():
    base = json.loads((ROOT / 'corpus/activity/20261010-windows-research-v2.json').read_text())
    projects = project_index(json.loads((ROOT / 'corpus/merged/repos.json').read_text()))
    rows = [r for r in base['records'] if r['source'] != 'benchmark_measurement']
    measures, trials, runs = {}, {}, {}
    report = {'source': 'experimental_recovery', 'copies': 0, 'native_bench_files': [],
              'invalid_or_undated': 0, 'unmapped_files': 0, 'source_hashes': {}}
    directories = set()
    for name in ['shapes-c-work-unignored.json', 'shapes-e-work-unignored.json', 'shapes-linux-work-unignored.json']:
        for row in json.loads((DISCOVERY / name).read_text())['rows']:
            if 'native_bench' in row.get('shapes', []):
                directories.add(Path(row['path']).parent)
    # Canonical owners precede worktree copies, whose data must not create new work.
    for directory in sorted(directories, key=lambda p: (any(x in p.parts for x in ['worktrees', 'orchestration']), str(p))):
        for path in sorted(directory.iterdir()):
            if path.suffix not in ('.json', '.jsonl') or excluded(path) or path.stat().st_size > 4_000_000:
                continue
            try:
                obs = objects(path)
            except (ValueError, UnicodeError):
                continue
            found = 0
            for obj in obs:
                if not isinstance(obj, dict) or not all(k in obj for k in ['test_time', 'n_prompt', 'n_gen', 'samples_ns']):
                    continue
                t = timestamp(obj['test_time'])
                if not t or not t.startswith('2026-'):
                    report['invalid_or_undated'] += 1
                    continue
                host, lid = owner(path, projects)
                if not lid:
                    report['unmapped_files'] += 1
                    continue
                rid = digest(obj)
                if rid in measures:
                    report['copies'] += 1
                    continue
                samples = obj['samples_ns']
                if not isinstance(samples, list) or not samples or not all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in samples):
                    report['invalid_or_undated'] += 1
                    continue
                measures[rid] = {'source': 'benchmark_measurement', 'id': rid, 'ts': t,
                                 'time_kind': 'native_test_time', 'host': host, 'projects': [lid],
                                 'project_role': 'record_owner', 'repeats': len(samples),
                                 'measured_seconds': sum(samples) / 1e9,
                                 'flagged_campaign': 'POISONED' in path.name}
                found += 1
            if found:
                report['native_bench_files'].append({'path': str(path), 'distinct_rows': found,
                                                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

    # Denning comparative pressure trials carry an explicit native epoch, and
    # request traces are stamped at completion by denning/bench.py itself.
    denning = Path('/mnt/omen-e-read/work/denning/results/raw')
    host, lid = owner(denning, projects)
    for path in sorted(denning.glob('*.result.json')):
        obj = objects(path)[0]
        if not isinstance(obj.get('ts'), (int, float)) or not obj.get('baseline'):
            continue
        t = dt.datetime.fromtimestamp(obj['ts'], dt.timezone.utc).isoformat().replace('+00:00', 'Z')
        rid = digest(['denning-pressure', obj['ts']])
        trials[rid] = {'source': 'experimental_trial', 'id': rid, 'ts': t, 'host': host,
                       'projects': [lid] if lid else [], 'project_role': 'record_owner',
                       'time_kind': 'native_result_epoch', 'kind': 'pressure_comparison'}
        report['source_hashes'][str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(denning.glob('bench-*.jsonl')):
        m = re.fullmatch(r'bench-(\d+)\.jsonl', path.name)
        if not m:
            continue  # bench-dry is a fabricated adapter run
        t = dt.datetime.fromtimestamp(int(m[1]), dt.timezone.utc).isoformat().replace('+00:00', 'Z')
        for obj in objects(path):
            if not isinstance(obj, dict) or not all(k in obj for k in ['i', 'admitted', 'arrival_ms', 'tokens']):
                continue
            rid = digest(['denning-request', int(m[1]), obj['i']])
            trials[rid] = {'source': 'experimental_trial', 'id': rid, 'ts': t, 'host': host,
                           'projects': [lid] if lid else [], 'project_role': 'record_owner',
                           'time_kind': 'native_campaign_completion_epoch', 'kind': 'request_trial',
                           'admitted': obj['admitted'] is True}
        report['source_hashes'][str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()

    # Memsplice sources were removed from the public tree. A pinned historical
    # tree and the public source hash catalog recover their metadata read-only.
    repo = Path('/mnt/omen-c-read/work/memsplice'); revision = '5b17e02'
    provenance = json.loads((repo / 'data/provenance.json').read_text())
    host, lid = owner(repo / 'results', projects)
    mem = collections.Counter()
    for entry in provenance['artifacts']:
        if entry['status'] != 'included':
            continue
        raw = subprocess.check_output(['git', '-C', str(repo), 'show', revision + ':results/' + entry['source']])
        variants = [('git_blob', raw), ('windows_checkout_crlf', raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))]
        match = next((name for name, data in variants if hashlib.sha256(data).hexdigest() == entry['sha256']), None)
        if not match:
            raise ValueError('Historical Memsplice artifact does not match provenance: ' + entry['source'])
        mem['hash_verified_artifacts'] += 1; mem[match] += 1
        obj = json.loads(raw.decode('utf-8-sig'))
        items = obj if isinstance(obj, list) else [obj]
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            a, b = timestamp(item.get('started_at')), timestamp(item.get('finished_at'))
            if not a or not b:
                mem['undated_rows'] += 1
                continue
            rid = digest(['memsplice-source', entry['sha256'], i])
            trials[rid] = {'source': 'experimental_trial', 'id': rid, 'ts': a, 'end': b,
                           'time_kind': 'native_experiment_interval', 'kind': 'kv_backend_experiment',
                           'host': host, 'projects': [lid] if lid else [], 'project_role': 'record_owner',
                           'source_sha256': entry['sha256'], 'git_revision': revision}
            mem['dated_trials'] += 1
    report['memsplice'] = dict(mem)
    report.update(status='partial', distinct_measurements=len(measures),
                  native_repeated_trials=sum(r['repeats'] for r in measures.values()),
                  distinct_other_trials=len(trials),
                  timing_note='Native benchmark records date groups of repeated samples. Denning request traces date the campaign completion, not an invented per-request timestamp. Memsplice dates come from original native intervals, with source hashes verified across line endings.')
    rows += list(measures.values()) + list(trials.values())
    base['records'] = sorted(rows, key=lambda r: (r['ts'], r['source'], r['id']))
    base['coverage'] += [report]
    out = ROOT / 'corpus/activity/20261010-experimental-recovery.json'
    if out.exists():
        raise ValueError('Choose a fresh frozen recovery path')
    out.write_text(json.dumps(base, indent=1) + '\n')
    (DISCOVERY / 'reconciliation.json').write_text(json.dumps(report, indent=1) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['native_bench_files', 'source_hashes']}))


if __name__ == '__main__':
    recover()
