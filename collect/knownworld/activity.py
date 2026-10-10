"""Read explicit metadata sources into a private, versioned activity sidecar.

No transcript/payload columns are selected. Source databases and experiment
directories are read-only. Run: python3 collect/knownworld/activity.py --out PATH
"""
import argparse
import collections
from contextlib import closing
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
ID = re.compile(r"^[A-Za-z0-9_.:/=-]{1,160}$")


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        t = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if t.tzinfo is None or t.year < 2000:
            return None
        return t.astimezone(dt.timezone.utc).isoformat().replace('+00:00', 'Z')
    except ValueError:
        return None


def token(value):
    return value if isinstance(value, str) and ID.fullmatch(value) else None


def read_db(path):
    return closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro&immutable=1', uri=True, timeout=5))


def workspace_key(uri):
    u = urlparse(uri)
    if u.scheme != 'file' or u.netloc:
        return None
    p = unquote(u.path).rstrip('/')
    if re.match(r'^/[cCeE]:/', p):
        return ('omen-' + p[1].lower(), p[4:].casefold())
    if p.startswith('/home/derek/'):
        return ('omen-linux', '~/' + p[len('/home/derek/'):])
    return None


def project_index(repos):
    candidates = collections.defaultdict(set)
    for r in repos['lineages']:
        if r.get('third_party'):
            continue
        for host, paths in r.get('paths', {}).items():
            for path in paths:
                path = path.rstrip('/')
                candidates[(host, path.casefold() if host in ('omen-c', 'omen-e') else path)].add(r['id'])
    return {k: next(iter(v)) for k, v in candidates.items() if len(v) == 1}


def antigravity(stores, projects):
    by_id, coverage = {}, []
    for host, path in stores:
        report = {'source': 'antigravity', 'host': host, 'path': str(path), 'rows': 0,
                  'invalid_dates': 0, 'duplicates': 0, 'wal_present': Path(str(path) + '-wal').exists()}
        coverage.append(report)
        if not path.exists():
            report['status'] = 'missing'
            continue
        with read_db(path) as con:
            rows = con.execute('SELECT conversation_id, last_modified_time, last_user_input_time, '
                               'step_count, workspace_uris FROM conversation_summaries')
            for cid, modified, user_time, steps, uris in rows:
                report['rows'] += 1
                t = timestamp(modified)
                if not token(cid) or t is None:
                    report['invalid_dates'] += 1
                    continue
                try:
                    workspaces = json.loads(uris)
                except (ValueError, TypeError):
                    workspaces = []
                links = sorted({projects[k] for u in workspaces if isinstance(u, str)
                                and (k := workspace_key(u)) in projects}) if isinstance(workspaces, list) else []
                row = {'source': 'antigravity', 'id': cid, 'ts': t, 'time_kind': 'last_modified',
                       'last_user_input': timestamp(user_time), 'steps': max(0, int(steps)),
                       'host': host, 'projects': links, 'client': 'antigravity', 'model': None}
                if cid in by_id:
                    report['duplicates'] += 1
                if cid not in by_id or dt.datetime.fromisoformat(row['ts'].replace('Z', '+00:00')) > dt.datetime.fromisoformat(by_id[cid]['ts'].replace('Z', '+00:00')):
                    by_id[cid] = row
        report['status'] = 'partial_wal' if report['wal_present'] else 'complete'
    return list(by_id.values()), coverage


def execution(path):
    report = {'source': 'hearth_execution', 'path': str(path), 'wal_present': Path(str(path) + '-wal').exists(),
              'unpaired': 0, 'invalid': 0, 'duplicate_events': 0}
    if not path.exists():
        return [], dict(report, status='missing')
    with read_db(path) as con:
        # SQLite extracts only these metadata leaves; desired.arguments and all
        # output artifacts stay inside the source database.
        inv = {}
        for row in con.execute("SELECT json_extract(i.value,'$.invocation_id'), "
                               "json_extract(i.value,'$.backend'), json_extract(i.value,'$.model'), "
                               "json_extract(i.value,'$.tokens_in'), json_extract(i.value,'$.tokens_out') "
                               "FROM jobs j, json_each(j.state_json,'$.invocations') i"):
            inv[row[0]] = row[1:]
        grouped, seen = collections.defaultdict(list), set()
        for eid, ts, kind, job, iid in con.execute("SELECT event_id,timestamp,event_type,job_id,invocation_id "
                                                  "FROM events WHERE event_type LIKE 'invocation.%'"):
            if eid in seen:
                report['duplicate_events'] += 1
                continue
            seen.add(eid)
            t = timestamp(ts)
            if not t or not token(iid) or not token(job):
                report['invalid'] += 1
                continue
            grouped[iid].append((t, kind, job))
    out = []
    for iid, ev in grouped.items():
        starts = [r for r in ev if r[1] == 'invocation.started']
        ends = [r for r in ev if r[1] in ('invocation.succeeded', 'invocation.failed', 'invocation.cancelled')]
        if len(starts) != 1 or len(ends) != 1:
            report['unpaired'] += 1
            continue
        a, b = starts[0], ends[0]
        if dt.datetime.fromisoformat(b[0].replace('Z', '+00:00')) < dt.datetime.fromisoformat(a[0].replace('Z', '+00:00')) or a[2] != b[2]:
            report['invalid'] += 1
            continue
        backend, model, tin, tout = inv.get(iid, (None,) * 4)
        out.append({'source': 'hearth_execution', 'id': iid, 'job_id': a[2], 'ts': a[0], 'end': b[0],
                    'time_kind': 'invocation_interval', 'status': b[1].split('.')[1], 'host': 'omen-c',
                    'backend': token(backend), 'model': token(model), 'projects': [],
                    'tokens_in': tin if isinstance(tin, int) and tin >= 0 else None,
                    'tokens_out': tout if isinstance(tout, int) and tout >= 0 else None})
    report.update(status='partial_wal' if report['wal_present'] else 'complete', paired=len(out),
                  jobs=len({r['job_id'] for r in out}))
    return out, report


def registry(path, lineage):
    seen, out = set(), []
    report = {'source': 'lab_registry', 'path': str(path), 'files': 0, 'invalid': 0}
    for p in sorted(path.glob('*.json')):
        obj = json.loads(p.read_text())
        report['files'] += 1
        t = timestamp(obj.get('at'))
        if t is None:
            report['invalid'] += 1
            continue
        for r in obj.get('records', []):
            rid, kind = token(r.get('id')), r.get('kind')
            if not rid or kind not in ('attempt', 'investigation', 'finding') or rid in seen:
                continue
            seen.add(rid)
            out.append({'source': 'lab_registry', 'id': rid, 'ts': t, 'time_kind': 'first_registry_event',
                        'kind': kind, 'status': token(r.get('status')), 'host': 'omen-linux',
                        'projects': [lineage] if lineage else [], 'project_role': 'record_owner'})
    report.update(status='complete' if report['files'] else 'missing', objects=len(out))
    return out, report


def benchmark_runs(path, lineage):
    """Thinking-run manifests are copies of runs, not additional executions.

    Identity is the complete set of native execution job IDs. Timing is from
    the enclosing run, never reconstructed from individual call durations.
    """
    by_id, conflicts = {}, set()
    report = {'source': 'benchmark_run', 'path': str(path), 'files': 0,
              'unsupported_format': 0, 'invalid': 0, 'copies': 0, 'dry_runs': 0}
    for p in sorted(path.rglob('run.json')):
        report['files'] += 1
        try:
            obj = json.loads(p.read_text())
        except (ValueError, OSError):
            report['invalid'] += 1
            continue
        if not isinstance(obj, dict) or obj.get('schema') != 'thinking-run.v1':
            report['unsupported_format'] += 1
            continue
        if obj.get('dry_run') is not False:
            report['dry_runs'] += 1
            continue
        jobs = sorted({jid for cv in obj.get('conversations', []) for k in ('work', 'final')
                       if isinstance(z := cv.get(k), dict) and (jid := token(z.get('job_id')))})
        a, b = timestamp(obj.get('started_utc')), timestamp(obj.get('finished_utc'))
        if not jobs or not a or not b or dt.datetime.fromisoformat(b.replace('Z', '+00:00')) < dt.datetime.fromisoformat(a.replace('Z', '+00:00')):
            report['invalid'] += 1
            continue
        rid = hashlib.sha256('\n'.join(jobs).encode()).hexdigest()
        row = {'source': 'benchmark_run', 'id': rid, 'job_ids': jobs, 'ts': a, 'end': b,
               'time_kind': 'benchmark_run_interval', 'host': 'omen-linux',
               'backend': token(obj.get('backend')), 'status': 'succeeded' if obj.get('ok') is True else 'not_succeeded',
               'projects': [lineage] if lineage else [], 'project_role': 'record_owner', 'calls': len(jobs)}
        if rid in by_id:
            report['copies'] += 1
            if row != by_id[rid]:
                conflicts.add(rid)
        else:
            by_id[rid] = row
    for rid in conflicts:
        del by_id[rid]  # conflicting copies require review, never pick a convenient one
    jobs = {j for r in by_id.values() for j in r['job_ids']}
    report.update(status='partial_formats' if report['unsupported_format'] else 'complete',
                  conflicting_identities=len(conflicts), distinct_runs=len(by_id), distinct_jobs=len(jobs))
    return list(by_id.values()), report


def fleet_results(path, lineage):
    """Count dated result observations, not inferred execution intervals."""
    by_id = {}
    report = {'source': 'fleet_result', 'path': str(path), 'files': 0, 'undated': 0, 'copies': 0}
    for sub in ('harvest', 'results'):
        for p in sorted((path / sub).glob('*.json')):
            obj = json.loads(p.read_text())
            rid = token(obj.get('plan_id'))
            if not rid:
                continue
            report['files'] += 1
            risk = (obj.get('promotion') or {}).get('risk') or {}
            t = timestamp(risk.get('computed_at'))
            if not t:
                report['undated'] += 1
                continue
            row = {'source': 'fleet_result', 'id': rid, 'ts': t, 'time_kind': 'promotion_risk_computed',
                   'host': 'omen-c', 'projects': [lineage] if lineage else [], 'project_role': 'record_owner',
                   'builds': len(obj.get('builds') or {}), 'promoted': (obj.get('promotion') or {}).get('promoted') is True}
            if rid in by_id:
                report['copies'] += 1
                if row['ts'] < by_id[rid]['ts']:
                    by_id[rid] = row
            else:
                by_id[rid] = row
    report.update(status='partial_dates' if report['undated'] else 'complete', dated_results=len(by_id))
    return list(by_id.values()), report


def canonical_executions(path):
    """Consume the frozen allowlisted API responses; never dispatch from collection."""
    obj = json.loads(path.read_text())
    rows, seen = [], set()
    report = {'source': 'canonical_execution', 'path': str(path), 'requested': obj['requested'],
              'unavailable_jobs': len(obj['failures']), 'invalid_or_unpaired': 0, 'duplicates': 0}
    for job in obj['jobs']:
        for inv in job['invocations']:
            iid, jid = token(inv.get('invocation_id')), token(job.get('job_id'))
            a, b = timestamp(inv.get('started_at')), timestamp(inv.get('finished_at'))
            if not iid or not jid or not a or not b or inv.get('status') not in ('succeeded', 'failed', 'cancelled'):
                report['invalid_or_unpaired'] += 1
                continue
            if dt.datetime.fromisoformat(b.replace('Z', '+00:00')) < dt.datetime.fromisoformat(a.replace('Z', '+00:00')):
                report['invalid_or_unpaired'] += 1
                continue
            if iid in seen:
                report['duplicates'] += 1
                continue
            seen.add(iid)
            rows.append({'source': 'hearth_execution', 'transport': 'canonical_api', 'id': iid, 'job_id': jid,
                         'ts': a, 'end': b, 'time_kind': 'invocation_interval', 'status': inv['status'],
                         'host': 'omen-linux', 'projects': [], 'backend': token(inv.get('backend')),
                         'model': token(inv.get('model')),
                         'tokens_in': inv.get('tokens_in') if isinstance(inv.get('tokens_in'), int) else None,
                         'tokens_out': inv.get('tokens_out') if isinstance(inv.get('tokens_out'), int) else None})
    report.update(status='complete' if not report['unavailable_jobs'] and not report['invalid_or_unpaired'] else 'partial',
                  paired=len(rows))
    return rows, report


def conductor_backup(path):
    """Frozen metadata from a copied archive; source host is not execution placement."""
    obj = json.loads(path.read_text())
    rows, undated = [], 0
    for item in obj['records']:
        rid, t = token(item.get('plan_id')), timestamp(item.get('computed_at'))
        if not rid or not t:
            undated += 1
            continue
        rows.append({'source': 'fleet_result', 'id': rid, 'ts': t,
                     'time_kind': 'promotion_risk_computed', 'host': obj['source_host'],
                     'projects': [], 'archive_copy': True})
    return rows, {'source': 'conductor_backup', 'path': str(path), 'files': len(obj['records']),
                  'dated_results': len(rows), 'undated': undated,
                  'status': 'partial_dates' if undated else 'complete'}


def collect():
    from windows_research import archived_research, native_benchmarks, manifest_campaigns
    repos = json.loads((ROOT / 'corpus/merged/repos.json').read_text())
    projects = project_index(repos)
    direct, direct_cov = archived_research(projects, timestamp, token)
    measurements, measurement_cov = native_benchmarks(projects, timestamp)
    campaigns, campaign_cov = manifest_campaigns(projects, timestamp)
    rows, coverage = antigravity([
        ('omen-c', Path('/mnt/omen-c-read/Users/derek/.gemini/antigravity/conversation_summaries.db')),
        ('omen-linux', Path('/home/derek/.gemini/antigravity-cli/conversation_summaries.db'))], projects)
    rows += direct + measurements + campaigns
    coverage += [direct_cov, measurement_cov, campaign_cov]
    ex, cov = execution(Path('/mnt/omen-c-read/hearth-var/execution/projection.sqlite'))
    rows += ex; coverage.append(cov)
    reg, cov = registry(Path('/home/derek/work/lab-rnd/research/state/events'), projects.get(('omen-linux', '~/work/lab-rnd')))
    rows += reg; coverage.append(cov)
    bench, cov = benchmark_runs(Path('/home/derek/work/lab-rnd/research/evidence'), projects.get(('omen-linux', '~/work/lab-rnd')))
    rows += bench; coverage.append(cov)
    fleet, cov = fleet_results(Path('/mnt/omen-c-read/work/commandcenter/campaign'), projects.get(('omen-c', 'work/commandcenter')))
    rows += fleet; coverage.append(cov)
    backup_path = ROOT / 'corpus/activity/fx99-conductor-backup.json'
    if backup_path.exists():
        backup, cov = conductor_backup(backup_path)
        rows += backup; coverage.append(cov)
    api_path = ROOT / 'corpus/activity/canonical-executions.json'
    if api_path.exists():
        api, cov = canonical_executions(api_path)
        rows += api; coverage.append(cov)
    return {'version': 1, 'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            'repos_sha256': hashlib.sha256((ROOT / 'corpus/merged/repos.json').read_bytes()).hexdigest(),
            'records': sorted(rows, key=lambda r: (r['ts'], r['source'], r['id'])), 'coverage': coverage}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); args = ap.parse_args()
    out = Path(args.out).resolve()
    if not out.is_relative_to(ROOT / 'corpus/activity') or out.exists():
        raise SystemExit('Choose a new output under corpus/activity/')
    result = collect()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1) + '\n')
    print(json.dumps({'records': len(result['records']), 'coverage': result['coverage']}))
