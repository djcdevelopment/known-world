"""Dated sidecar activity; distinct units, exact-time overlap, no launch inference."""
import collections
import datetime as dt
import json
from pathlib import Path

import numpy as np
import build_data as bd
import common

LANES = [('Antigravity', '#b5a2ef'), ('HEARTH runs', '#e2ef6a'), ('research', '#f1ba74'),
         ('bench runs', '#f0d883'), ('fleet results', '#93cdbd'),
         ('direct research', '#efb065'), ('bench measures', '#d6ba7a'),
         ('experiment trials', '#eac17c')]


def epoch(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


def overlap_changes(intervals):
    """Exact-time sweep. Equal-time ends precede starts; empty intervals vanish."""
    events = [(t, d) for a, b in intervals if b > a for t, d in ((a, 1), (b, -1))]
    active, peak, changes = 0, 0, []
    for t, d in sorted(events):
        active += d
        if active > peak:
            peak = active
            changes.append((t, peak))
    return changes


def build(params, clock, c, tiles, series):
    path = Path(params['activity_file']) if params.get('activity_file') else None
    if path is None:
        return None, {'status': 'disabled'}
    if not path.is_absolute():
        path = Path(common.ROOT) / path
    # A configured missing sidecar is an error, never silently empty coverage.
    source = json.loads(path.read_text())
    if source['version'] != 1:
        raise ValueError('Unsupported activity sidecar version')
    if source['repos_sha256'] != common.sha256_file(Path(common.MERGED) / 'repos.json'):
        raise ValueError('Activity workspace map is stale; recollect against this corpus')
    F = clock.F
    ticks = (clock.tau_frames() + clock.epoch0) * 86400
    lo, hi = clock.epoch0 * 86400, epoch(c.as_of)
    frame = lambda t: min(F - 1, int(np.searchsorted(ticks, t, side='left')))
    # These numeric series keep their distinct units all the way to the UI.
    names = ['conversations', 'executions', 'succeeded', 'failed', 'attempts', 'findings', 'investigations',
             'bench_runs', 'bench_jobs', 'fleet_results', 'direct_attempts',
             'direct_succeeded', 'direct_failed', 'direct_unknown', 'bench_measurements',
             'bench_trials', 'experiment_trials']
    increments = {k: np.zeros(F, dtype=np.int32) for k in names}
    hist = np.zeros((len(LANES), F), dtype=np.int32)
    pulses, intervals, seen = collections.Counter(), [], set()
    bench_intervals, bench_jobs_seen = [], set()
    skipped = collections.Counter(); mapped = collections.Counter()
    for r in sorted(source['records'], key=lambda r: epoch(r.get('end', r['ts']))):
        key = (r['source'], r['id'])
        if key in seen:
            skipped['duplicates'] += 1
            continue
        seen.add(key)
        a = epoch(r['ts'])
        t = epoch(r['end']) if r['source'] in ('hearth_execution', 'benchmark_run') else a
        if t < lo or a > hi:
            skipped['outside_story'] += 1
            continue
        if r['source'] == 'hearth_execution':
            # Still-running intervals can contribute historical overlap, but
            # their future completion/status must not leak into a counter.
            intervals.append((max(lo, a), min(hi, t)))
        elif r['source'] == 'benchmark_run':
            bench_intervals.append((max(lo, a), min(hi, t)))
        if t > hi:
            skipped['after_snapshot'] += 1
            continue
        f = frame(t)
        if r['source'] == 'antigravity':
            lane, measure = 0, 'conversations'
        elif r['source'] == 'hearth_execution':
            lane, measure = 1, 'executions'
            if r['status'] in ('succeeded', 'failed'):
                increments[r['status']][f] += 1
        elif r['source'] == 'lab_registry':
            lane, measure = 2, {'attempt': 'attempts', 'finding': 'findings', 'investigation': 'investigations'}[r['kind']]
        elif r['source'] == 'benchmark_run':
            lane, measure = 3, 'bench_runs'
            new_jobs = set(r['job_ids']) - bench_jobs_seen
            increments['bench_jobs'][f] += len(new_jobs)
            bench_jobs_seen.update(new_jobs)
        elif r['source'] == 'fleet_result':
            lane, measure = 4, 'fleet_results'
        elif r['source'] == 'direct_research':
            lane, measure = 5, 'direct_attempts'
            increments['direct_' + r['status']][f] += 1
        elif r['source'] == 'benchmark_measurement':
            lane, measure = 6, 'bench_measurements'
            increments['bench_trials'][f] += r.get('repeats', 1)
        elif r['source'] == 'experimental_trial':
            lane, measure = 7, 'experiment_trials'
            increments['bench_trials'][f] += 1
        else:
            skipped['unsupported_source'] += 1
            continue
        increments[measure][f] += 1; hist[lane, f] += 1
        # Only the evidenced host/path pair may light a mapped region. Never
        # fall back to the first host or attribute work to HEARTH's own repo.
        for lid in r.get('projects', []):
            ri = tiles.reg_index.get((lid, r['host']))
            if ri is not None:
                pulses[(f, ri, lane)] += 1
                mapped[r['source']] += 1
    peak = np.zeros(F, dtype=np.int32)
    for t, n in overlap_changes(intervals):
        peak[frame(t)] = max(peak[frame(t)], n)
    peak = np.maximum.accumulate(peak)
    cumulative = {k: np.cumsum(v) for k, v in increments.items()}
    dispatch = np.zeros(F, dtype=np.int32)
    for t in c.local_dispatch_t:
        if lo <= t <= hi:
            dispatch[frame(t)] += 1
    cumulative['local_calls'] = np.cumsum(dispatch)
    cumulative['overlap_peak'] = peak
    bench_peak = np.zeros(F, dtype=np.int32)
    for t, n in overlap_changes(bench_intervals):
        bench_peak[frame(t)] = max(bench_peak[frame(t)], n)
    cumulative['bench_overlap_peak'] = np.maximum.accumulate(bench_peak)
    pack = lambda v: bd.b64(np.asarray(v).astype('<i4'))
    historical_path = Path(common.ROOT) / 'corpus/activity/historical-coverage.json'
    historical = json.loads(historical_path.read_text())
    undated = {'image_results': historical['am4_image_benchmarks']['valid_result_ids']}
    data = {'undated': undated,
            'lanes': [{'name': name, 'color': col, 'hist': pack(hist[i])} for i, (name, col) in enumerate(LANES)],
            'counts': {k: pack(v) for k, v in cumulative.items()},
            'pulses': [[f, ri, lane, n] for (f, ri, lane), n in sorted(pulses.items())],
            'notes': ['Antigravity: one observation per conversation at its last recorded update; model unknown.',
                      'HEARTH runs: Windows archive plus canonical metadata for recovered benchmark/delivery jobs; partial coverage. Overlap is invocation overlap, not GPU utilization.',
                      'Research: first registry appearance of attempts, investigations and findings; not acceptance verdicts.',
                      'Bench runs: dated thinking-run job sets plus finished Windows runner manifests. Windows manifests do not invent native job IDs or calls. Copies folded.',
                      'Fleet results: dated promotion-risk assessments of result records; not execution completion timestamps.',
                      'Direct research: archived native attempts outside the gateway; server-log and driver dates retain source uncertainty. Not included in exact overlap.',
                      'Bench measures: explicit native test_time per configuration row; copies folded. Measured trials count native repeated samples separately, plus experimental trial records. These can underlie direct research attempts; do not add the views.',
                      'Experiment trials: Denning pressure comparisons and request trials, plus original source-hash-verified Memsplice intervals. Denning requests are observed at native campaign completion. No telemetry samples or rescoring counted.']}
    report = {'status': 'present', 'sha256': common.sha256_file(path), 'snapshot': c.as_of,
              'totals': {k: int(v[-1]) for k, v in cumulative.items()}, 'mapped_observations': dict(mapped),
              'skipped': dict(skipped), 'coverage': source['coverage'], 'map_pulses': len(pulses),
              'undated': undated, 'historical_coverage_sha256': common.sha256_file(historical_path)}
    return data, report
