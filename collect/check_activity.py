"""Small fixtures for privacy, dedupe, timestamp semantics and interval overlap."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'collect'))
sys.path.insert(0, str(ROOT / 'compile'))
from knownworld import activity as collect
import activity as compile_activity


class ActivityChecks(unittest.TestCase):
    def test_benchmark_copies_and_dry_runs(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            row = {'schema': 'thinking-run.v1', 'dry_run': False, 'started_utc': '2026-10-03T10:00:00Z',
                   'finished_utc': '2026-10-03T10:01:00Z', 'backend': 'omen-dense-27b', 'ok': True,
                   'conversations': [{'work': {'job_id': 'job-a'}, 'final': {'job_id': 'job-b'}}]}
            for name in ['original', 'copied']:
                (p / name).mkdir(); (p / name / 'run.json').write_text(json.dumps(row))
            (p / 'dry').mkdir(); (p / 'dry/run.json').write_text(json.dumps(dict(row, dry_run=True)))
            records, coverage = collect.benchmark_runs(p, 'lab')
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]['calls'], 2)
            self.assertEqual(coverage['copies'], 1)
            self.assertEqual(coverage['dry_runs'], 1)
            (p / 'copied/run.json').write_text(json.dumps(dict(row, finished_utc='2026-10-03T10:02:00Z')))
            records, coverage = collect.benchmark_runs(p, 'lab')
            self.assertEqual(records, [])
            self.assertEqual(coverage['conflicting_identities'], 1)

    def test_fleet_dates_are_explicit_observations(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); (p / 'harvest').mkdir(); (p / 'results').mkdir()
            for sub, stamp in [('harvest', '2026-07-06T10:00:00Z'), ('results', '2026-07-05T10:00:00Z')]:
                row = {'plan_id': 'plan-a', 'promotion': {'risk': {'computed_at': stamp}}, 'builds': {'worker': {}}}
                (p / sub / 'dated.json').write_text(json.dumps(row))
            (p / 'results/undated.json').write_text(json.dumps({'plan_id': 'plan-b', 'builds': {}}))
            records, coverage = collect.fleet_results(p, 'cc')
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]['ts'], '2026-07-05T10:00:00Z')
            self.assertEqual(records[0]['time_kind'], 'promotion_risk_computed')
            self.assertEqual(coverage['undated'], 1)

    def test_half_open_and_empty_intervals(self):
        self.assertEqual(compile_activity.overlap_changes([(1, 2), (2, 3), (2, 2)]), [(1, 1)])
        self.assertEqual(compile_activity.overlap_changes([(1, 3), (2, 4)]), [(1, 1), (2, 2)])

    def test_summary_privacy_dedupe_and_invalid_dates(self):
        with tempfile.TemporaryDirectory() as d:
            stores = []
            for i, stamp in enumerate(['2026-07-01 00:00:00+00:00', '2026-07-01 00:00:00.5+00:00']):
                p = Path(d) / (str(i) + '.db')
                with closing(sqlite3.connect(p)) as c, c:
                    c.execute('CREATE TABLE conversation_summaries (conversation_id TEXT, last_modified_time TEXT, '
                              'last_user_input_time TEXT, step_count INTEGER, workspace_uris TEXT, title TEXT, preview TEXT)')
                    c.execute('INSERT INTO conversation_summaries VALUES (?,?,?,?,?,?,?)',
                              ('same-id', stamp, stamp, 3 + i, '["file:///c%3A/work/project"]', 'PRIVATE_BODY', 'PRIVATE_BODY'))
                    c.execute('INSERT INTO conversation_summaries VALUES (?,?,?,?,?,?,?)',
                              ('bad-date', '0001-01-01 00:00:00+00:00', '', 2, '[]', 'PRIVATE_BODY', 'PRIVATE_BODY'))
                stores.append(('omen-c', p))
            before = [p.read_bytes() for _, p in stores]
            rows, coverage = collect.antigravity(stores, {('omen-c', 'work/project'): 'lineage'})
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['steps'], 4)
            self.assertEqual(rows[0]['projects'], ['lineage'])
            self.assertEqual(sum(r['invalid_dates'] for r in coverage), 2)
            self.assertNotIn('PRIVATE_BODY', json.dumps(rows))
            self.assertNotIn('title', rows[0])
            self.assertEqual(before, [p.read_bytes() for _, p in stores])

    def test_project_joins_are_exact(self):
        index = collect.project_index({'lineages': [
            {'id': 'own', 'paths': {'omen-c': ['work/Project']}, 'third_party': False},
            {'id': 'third', 'paths': {'omen-linux': ['~/work/vendor']}, 'third_party': True}]})
        self.assertEqual(index[collect.workspace_key('file:///c%3A/work/project')], 'own')
        self.assertNotIn(collect.workspace_key('file:///c:/work'), index)
        self.assertNotIn(collect.workspace_key('file:///home/derek/work/vendor'), index)

    def test_unpaired_execution_is_not_completed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'projection.sqlite'
            with closing(sqlite3.connect(p)) as c, c:
                c.execute('CREATE TABLE jobs (state_json TEXT)')
                c.execute('CREATE TABLE events (event_id TEXT,timestamp TEXT,event_type TEXT,job_id TEXT,invocation_id TEXT)')
                for eid, stamp, kind, job, inv in [
                    ('a','2026-07-01T00:00:00Z','invocation.started','j1','i1'),
                    ('b','2026-07-01T00:00:01Z','invocation.succeeded','j1','i1'),
                    ('c','2026-07-01T00:00:00Z','invocation.started','j2','i2')]:
                    c.execute('INSERT INTO events VALUES (?,?,?,?,?)', (eid,stamp,kind,job,inv))
            rows, coverage = collect.execution(p)
            self.assertEqual(len(rows), 1)
            self.assertEqual(coverage['unpaired'], 1)
            self.assertEqual(rows[0]['status'], 'succeeded')


if __name__ == '__main__':
    unittest.main()
