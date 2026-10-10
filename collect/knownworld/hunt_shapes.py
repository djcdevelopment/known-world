"""Broad read-only evidence discovery by learned format, not project names.

Inventory filenames first; inspect bounded representative structured files in
each candidate directory. Emit schema keys and safe date/count metadata only.
All omissions are explicit. This inventory is never itself an activity count.
"""
import argparse
import collections
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import shutil
import time

from discover import excluded

SKIP = ['.git', 'node_modules', '.venv', 'venv', 'venvs', 'models', 'model',
        'checkpoints', '.cache', '__pycache__', 'site-packages', '_deps', 'build',
        'build-public', 'build-prototypes', 'obj', 'bin', '.claude', '.codex',
        '.test-output', 'browser_profiles', 'BrowserMetrics', 'Default', 'amux',
        '.pytest_cache', '.ruff_cache', 'dist', 'target', '.pixi', 'envs', 'known-world']
PAYLOAD = re.compile(r'prompt|body|answer|completion|transcript|conversation|chat|credential|secret|tokenizer', re.I)
SIGNAL = re.compile(r'bench|experiment|research|[/_-]rnd|campaign|results?|receipts?|measure|eval|probe|trial|raw|manifest|summary|observation|provenance', re.I)
FORMATS = {'.json', '.jsonl', '.ndjson', '.csv', '.tsv', '.sqlite', '.db'}


def classify(keys):
    k = set(keys)
    kinds = []
    for name, required in [('native_bench', {'test_time', 'n_prompt', 'n_gen'}),
                           ('thinking_run', {'started_utc', 'finished_utc', 'conversations'}),
                           ('runner_interval', {'started_at', 'finished_at'}),
                           ('native_attempt', {'attempt_id', 'source'}),
                           ('source_hashed_measurements', {'source_sha256', 'measurements'}),
                           ('request_trace', {'arrival_ms', 'admitted', 'tokens'}),
                           ('dated_pressure_trial', {'ts', 'baseline', 'analysis'}),
                           ('hardware_probe', {'probe', 'status'}),
                           ('measurement_export', {'schema_version', 'records'}),
                           ('benchmark_row', {'row_id', 'run_id', 'metric'}),
                           ('request_result', {'t_start', 'ok'}),
                           ('dated_result', {'timestamp', 'results'}),
                           ('receipt', {'experiment', 'timestamp'})]:
        if required <= k:
            kinds.append(name)
    if any(key in k for key in ['timings', 'prefill_timings', 'b70_cold_timings', 'measurements', 'decode_tps', 'avg_ts', 'latency_ms', 'duration_ms', 'throughput', 'ttft_ms', 'PromptTokPerSec']):
        kinds.append('measured_result')
    return kinds


def inspect(path):
    size = path.stat().st_size
    if size > 4_000_000:
        return {'path': str(path), 'bytes': size, 'disposition': 'large_file_requires_targeted_reader'}
    if path.suffix.lower() in ('.db', '.sqlite'):
        return {'path': str(path), 'bytes': size, 'disposition': 'database_requires_selected_columns'}
    try:
        with path.open('rb') as f:
            header = f.read(2)
        encoding = 'utf-16' if header == b'\xff\xfe' else 'utf-8-sig'
        with path.open('r', encoding=encoding) as f:
            text = f.read() if path.suffix.lower() == '.json' else f.readline(262144)
        if path.suffix.lower() in ('.csv', '.tsv'):
            keys = next(csv.reader([text], delimiter='\t' if path.suffix == '.tsv' else ','))
            obj = None
        else:
            obj = json.loads(text)
            if isinstance(obj, list):
                obj = next((x for x in obj if isinstance(x, dict)), {})
            keys = list(obj) if isinstance(obj, dict) else []
        row = {'path': str(path), 'bytes': size, 'keys': keys, 'shapes': classify(keys)}
        if isinstance(obj, dict):
            for key in ['records', 'results', 'receipts', 'observations']:
                arr = obj.get(key)
                if isinstance(arr, list) and arr and isinstance(arr[0], dict):
                    row['nested_keys'] = list(arr[0])
                    row['shapes'] += classify(arr[0])
                    row['records_in_container'] = len(arr)  # inventory, not native attempt count
                    break
        return row
    except (OSError, UnicodeError, ValueError, StopIteration):
        return {'path': str(path), 'bytes': size, 'disposition': 'format_requires_targeted_reader'}


def hunt(root):
    started = time.monotonic()
    if not Path(root).is_dir():
        return {'root': root, 'enumeration_status': 'missing_root', 'rows': [], 'omissions': []}
    # Experiment outputs are frequently gitignored. Honoring .gitignore here
    # silently discards exactly the data this workflow exists to recover.
    args = ['rg', '--files', '--hidden', '--no-ignore', root]
    for name in SKIP:
        args += ['-g', '!**/' + name + '/**']
    for suffix in ['gguf', 'safetensors', 'pt', 'pth', 'vhdx', 'zip']:
        args += ['-g', '!**/*.' + suffix]
    if shutil.which('rg'):
        proc = subprocess.run(args, capture_output=True, text=True, timeout=90)
        filenames = proc.stdout.splitlines()
        enumeration_status = 'complete' if proc.returncode == 0 else 'partial_read_errors'
    else:
        filenames, errors = [], []
        for directory, children, files in os.walk(root, onerror=lambda e: errors.append(e.errno)):
            children[:] = [n for n in children if n not in SKIP and not excluded(Path(directory) / n)
                           and not (Path(directory) / n).is_symlink()]
            filenames.extend(str(Path(directory) / n) for n in files if not (Path(directory) / n).is_symlink())
        enumeration_status = 'partial_read_errors' if errors else 'complete'
    dirs = collections.defaultdict(list)
    for s in filenames:
        p = Path(s)
        if excluded(p) or any(part in SKIP for part in p.parts) or p.suffix.lower() not in FORMATS or PAYLOAD.search(p.name) or not SIGNAL.search(s):
            continue
        dirs[str(p.parent)].append(p)
    rows, omissions = [], []
    for directory, paths in sorted(dirs.items()):
        # Different basename families/extensions get representatives before repeats.
        groups = collections.defaultdict(list)
        for p in paths:
            family = re.sub(r'\d+', '#', p.name)
            groups[(p.suffix, family)].append(p)
        selected = [min(v, key=lambda p: p.stat().st_size) for v in groups.values()]
        if len(selected) > 50:
            omissions.append({'directory': directory, 'families_not_inspected': len(selected) - 50})
        for p in sorted(selected)[:50]:
            rows.append(inspect(p))
    return {'root': root, 'enumerated_files': len(filenames),
            'candidate_files': sum(map(len, dirs.values())), 'candidate_directories': len(dirs),
            'inspected': len(rows), 'rows': rows, 'omissions': omissions,
            'enumeration_status': enumeration_status,
            'elapsed_s': round(time.monotonic() - started, 2),
            'policy': 'Representative schema discovery only; no work counts inferred. Payload files, credentials and runtime/model caches excluded.'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--root', required=True); ap.add_argument('--out')
    args = ap.parse_args(); result = hunt(args.root)
    if args.out:
        p = Path(args.out);p.write_text(json.dumps(result, indent=1) + '\n')
        print(json.dumps({k: v for k, v in result.items() if k not in ['rows', 'omissions']}))
    else:
        print(json.dumps(result))
