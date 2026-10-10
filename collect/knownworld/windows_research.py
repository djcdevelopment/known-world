"""Read archived research receipts and native bench measurements, never payloads.

Attempts, measured rows and gateway jobs remain different accounting units.
The archive's reconstructed dates retain their original uncertainty.
"""
import collections
import hashlib
import json
from pathlib import Path


def archived_research(projects, timestamp, token):
    root = Path('/mnt/omen-c-read/work/commandcenter/hearth/var/seats')
    report = {'source': 'direct_research', 'path': str(root), 'files': [],
              'invalid': 0, 'copies': 0, 'conflicts': 0}
    cursor = json.loads((root / 'harvest-cursor.json').read_text())
    epochs = collections.defaultdict(set)
    for path, entry in cursor['logs'].items():
        if entry.get('eligible') is True and entry.get('seat_epoch_sha256'):
            epochs[entry['seat_epoch_sha256']].add(path.replace('\\', '/'))
    by_id, conflicts = {}, set()
    families = collections.Counter()
    for name, schema in [('receipts.ndjson', 'seat.physical-attempt.v1'),
                         ('run-records.ndjson', 'run.record-attempt.v1')]:
        path = root / name
        report['files'].append({'name': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        for line in path.open():
            obj = json.loads(line)
            rid = token(obj.get('attempt_id'))
            a, b = timestamp(obj.get('started_at')), timestamp(obj.get('finished_at'))
            src = obj.get('source') or {}
            if (obj.get('schema') != schema or not rid or not a or not b or b < a
                    or src.get('accounting_owner') != 'direct'
                    or obj.get('outcome') not in ('succeeded', 'failed', 'unknown')):
                report['invalid'] += 1
                continue
            host, owner = None, None
            if schema == 'seat.physical-attempt.v1':
                paths = epochs.get(obj.get('seat_epoch_sha256'), set())
                owners = set()
                for p in paths:
                    parts = p.split('/')
                    if len(parts) >= 4 and parts[0].lower() in ('c:', 'e:') and parts[1].lower() == 'work':
                        owners.add(('omen-' + parts[0][0].lower(), '/'.join(parts[1:3]).casefold()))
                if len(owners) == 1:
                    host, owner = next(iter(owners))
            else:
                owner = 'work/tuning' if src.get('adapter') == 'ollama-backend-lab' else 'work/commandcenter'
                host = 'omen-c'  # record owner, not a claim about GPU placement
            lid = projects.get((host, owner))
            usage = obj.get('usage') or {}
            derivation = obj.get('timestamp_derivation') or {}
            row = {'source': 'direct_research', 'id': rid, 'ts': a, 'end': b,
                   'time_kind': derivation.get('method'), 'time_error_bound_s': derivation.get('error_bound_s'),
                   'status': obj['outcome'], 'host': host, 'projects': [lid] if lid else [],
                   'project_role': 'record_owner', 'adapter': src.get('adapter'),
                   'model': token((obj.get('provider') or {}).get('model_name')),
                   'tokens_in': usage.get('tokens_in'), 'tokens_out': usage.get('tokens_out')}
            if rid in by_id:
                report['copies'] += 1
                if row != by_id[rid]:
                    conflicts.add(rid)
            else:
                by_id[rid] = row
                families[src.get('adapter')] += 1
    for rid in conflicts:
        del by_id[rid]
    report.update(status='partial' if report['invalid'] or conflicts else 'complete',
                  attempts=len(by_id), conflicts=len(conflicts), families=dict(families),
                  timing_note='Archive dates include mtime-derived epochs and day-bounded driver dates; not exact concurrency evidence.')
    return list(by_id.values()), report


def native_benchmarks(projects, timestamp):
    root = Path('/mnt/omen-e-read/work/battlemage')
    by_id = {}
    report = {'source': 'benchmark_measurement', 'path': str(root), 'copies': 0, 'invalid_dates': 0, 'files': []}
    # These two campaigns retain native llama-bench output with explicit test_time.
    # Other harness records are already represented by archived direct receipts.
    for sub in ['bench-2026-05-24', 'burnin-2026-08/results']:
        for path in sorted((root / sub).glob('*.jsonl')):
            raw = path.read_bytes()
            try:
                data = raw.decode('utf-16') if raw.startswith(b'\xff\xfe') else raw.decode('utf-8-sig')
            except UnicodeError:
                continue
            found = 0
            for line in data.splitlines():
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue  # native outputs can also carry non-JSON process diagnostics
                if not isinstance(obj, dict) or not all(k in obj for k in ('n_prompt', 'n_gen', 'test_time', 'samples_ns')):
                    continue
                t = timestamp(obj['test_time'])
                if not t:
                    report['invalid_dates'] += 1
                    continue
                rid = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                if rid in by_id:
                    report['copies'] += 1
                    continue
                lid = projects.get(('omen-e', 'work/battlemage'))
                by_id[rid] = {'source': 'benchmark_measurement', 'id': rid, 'ts': t,
                             'time_kind': 'native_test_time', 'host': 'omen-e',
                             'projects': [lid] if lid else [], 'project_role': 'record_owner',
                             'repeats': len(obj['samples_ns']),
                             'flagged_campaign': 'POISONED' in path.name}
                found += 1
            if found:
                report['files'].append({'relative': path.relative_to(root).as_posix(), 'rows': found,
                                        'sha256': hashlib.sha256(raw).hexdigest()})
    report.update(status='complete', measurements=len(by_id),
                  meaning='One native measured configuration row, not one HTTP call or one repeated sample; may underpin archived attempts.')
    return list(by_id.values()), report


def manifest_campaigns(projects, timestamp):
    """Dated runner manifests, never infer calls from telemetry or server starts."""
    by_id = {}
    report = {'source': 'windows_benchmark_run', 'copies': 0, 'undated_or_unfinished': 0, 'roots': []}
    for repo, sub in [('b70tools', 'eval/runs'), ('vllama', 'runs')]:
        root = Path('/mnt/omen-e-read/work') / repo / sub
        report['roots'].append(str(root))
        for path in sorted(root.rglob('manifest.json')):
            obj = json.loads(path.read_text(encoding='utf-8-sig'))
            a, b = timestamp(obj.get('started_at')), timestamp(obj.get('finished_at'))
            if not a or not b or b < a:
                report['undated_or_unfinished'] += 1
                continue
            # Config/probe + native start/end identifies the runner, while paths
            # and file modification dates do not establish an execution.
            identity = [repo, obj.get('config_name', obj.get('probe')), a, b]
            rid = hashlib.sha256(json.dumps(identity, separators=(',', ':')).encode()).hexdigest()
            if rid in by_id:
                report['copies'] += 1
                continue
            lid = projects.get(('omen-e', 'work/' + repo))
            by_id[rid] = {'source': 'benchmark_run', 'id': 'win-' + rid, 'ts': a, 'end': b,
                         'time_kind': 'native_runner_interval', 'host': 'omen-e',
                         'projects': [lid] if lid else [], 'project_role': 'record_owner',
                         'job_ids': [], 'status': 'recorded_finished', 'calls': None}
    report.update(status='partial' if report['undated_or_unfinished'] else 'complete',
                  distinct_runs=len(by_id), meaning='Finished native runner manifests; no inferred job IDs, calls or success verdicts.')
    return list(by_id.values()), report
