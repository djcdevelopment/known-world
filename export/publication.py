"""Package a reviewed film and aggregate-only public evidence summary."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package(build, video, poster, out, opening_seconds=0, closing_fade_seconds=0):
    receipt = json.loads((build / 'receipt.json').read_text())
    if sha(build / 'kw-data.js') != receipt['kw_data_sha256']:
        raise ValueError('Build differs from its reviewed receipt')
    counts = receipt['activity']['totals']
    world = receipt['running_totals']['world']
    rows = [
        ('Animation bursts', receipt['counts']['launches'], 'Derived episodes shown as flashes; separate from commits, calls and sessions.'),
        ('Commits', world['commits'], 'Deduplicated recorded commits.'),
        ('File touches', world['files'],
         f"{sum(n['files_changed'] for n in receipt['running_totals']['nation'].values()):,} git touches + "
         f"{sum(s['files_created'] for s in receipt['running_totals']['surface'].values()):,} creations + "
         f"{sum(s['files_updated'] for s in receipt['running_totals']['surface'].values()):,} update observations; not unique files."),
        ('Line changes', world['lines'], 'Uncapped additions plus removals, not current code size.'),
        ('Local HEARTH calls', counts['local_calls'], 'Dispatch records with evidenced local backends.'),
        ('Gemini calls', receipt['gemini_calls']['count'], 'Gemini participation recorded through HEARTH.'),
        ('Antigravity conversations', counts['conversations'], 'Observed at last recorded update; model unknown.'),
        ('Completed invocations', counts['executions'],
         f"{counts['succeeded']:,} succeeded; {counts['failed']:,} failed. Partial execution history."),
        ('Benchmark runs', counts['bench_runs'],
         f"{counts['bench_jobs']:,} distinct HEARTH jobs in thinking runs, plus native Windows runner manifests without job IDs; copies folded."),
        ('Fleet result observations', counts['fleet_results'], 'Dated result assessments, not inferred job completion times.'),
        ('Research attempts', counts['attempts'], 'Distinct registry records at first appearance.'),
        ('Research investigations', counts['investigations'], 'Distinct registry records, separate from attempts.'),
        ('Research findings', counts['findings'], 'Finding records; not automatically accepted capabilities.'),
        ('Direct research attempts', counts['direct_attempts'],
         f"{counts['direct_succeeded']:,} succeeded; {counts['direct_failed']:,} failed; {counts['direct_unknown']:,} unknown. Archived research outside HEARTH; dates retain log/driver uncertainty."),
        ('Native benchmark measurements', counts['bench_measurements'],
         'Distinct dated configuration rows, including Denning and other discovered sources; copied evidence folded.'),
        ('Measured experiment trials', counts['bench_trials'],
         f"Native repeated benchmark samples plus {counts['experiment_trials']:,} Denning/Memsplice trial records. Overlaps configurations, runners and some direct attempts; do not add these views."),
    ]
    data_text = (build / 'kw-data.js').read_text()
    data = json.loads(data_text.split('=', 1)[1].rstrip().rstrip(';'))
    for actor in data['card']:
        if actor.get('part_label') == 'sessions' and actor.get('parts'):
            rows.append((actor['name'] + ' sessions', actor['parts'], 'Distinct native session IDs; mirrored records folded.'))
    coverage = [
        ('Windows research recovery', f"{counts['direct_attempts']:,} direct attempts; 41 runner manifests; {counts['bench_measurements']:,} bench configurations",
         'Research-seat archive includes burn-in, Qwen, planning-matrix/Windtunnel, Tuning and AM4 load work. Counts are overlapping views, not an additive grand total.'),
        ('Further research coverage', 'Partial; 19 unfinished or undated runner manifests excluded',
         'Earlier server timing logs, undated GPU-level records and derived Windtunnel summaries remain source leads. File/schema searches include ignored outputs; missing archives and representative-schema limits remain explicit.'),
        ('Historical Memsplice results', '59 source artifacts recovered; 60 dated trials',
         'Earlier Git records match all public source hashes after accounting for Windows line endings. Four undated rows remain outside the film.'),
        ('Conductor code history', '36 commits already included',
         'GitHub and collected history match. The mirror was last pushed July 3, 2026.'),
        ('AM4 image benchmarks', '4,533 valid results without dates',
         'Retained as coverage, outside the time-lapse; 17 malformed records were excluded.'),
        ('Later MechNet history', 'Original execution archive unavailable',
         'Surviving older fleet results are included where explicit dates exist.'),
        ('Antigravity coverage', 'Last-update observations',
         'One invalid date and 14 observations after the cutoff are excluded. The Windows WAL may contain additional history.'),
    ]
    # Public values are aggregate counts and authored interpretations only.
    summary = {'snapshot_utc': receipt['activity']['snapshot'],
               'dated_measures': [{'measure': a, 'count': b, 'meaning': c} for a, b, c in rows],
               'coverage': [{'measure': a, 'status': b, 'meaning': c} for a, b, c in coverage],
               'recorded_peak_invocation_overlap': counts['overlap_peak'],
               'recorded_peak_benchmark_run_overlap': counts['bench_overlap_peak']}
    out.mkdir(parents=True, exist_ok=False)
    names = {'video': 'known-world-90s-' + sha(video)[:12] + '.mp4',
             'poster': 'poster-' + sha(poster)[:12] + '.png'}
    for src, name in [(video, names['video']), (poster, names['poster'])]:
        shutil.copyfile(src, out / name)
    # Older entry pages reference these stable names. Publish them with every
    # release so a cached page cannot select a permanently abandoned film.
    for name, alias in [(names['video'], 'known-world-90s.mp4'),
                        (names['poster'], 'poster.png')]:
        shutil.copyfile(out / name, out / alias)
    manifest = {'version': 1, 'snapshot_utc': summary['snapshot_utc'], 'duration_seconds': 90 + opening_seconds + closing_fade_seconds,
                'closing_fade_seconds': closing_fade_seconds,
                'opening_seconds': opening_seconds,
                'frame_rate': 30, 'width': 1920, 'height': 1080,
                'data_sha256': receipt['kw_data_sha256'],
                'audio_sha256': receipt['audio_sha256'], 'evidence': summary,
                'assets': {name: {'sha256': sha(out / name), 'bytes': (out / name).stat().st_size}
                           for name in [*names.values(), 'known-world-90s.mp4', 'poster.png']}}
    (out / 'release.json').write_text(json.dumps(manifest, indent=2) + '\n')
    def table(items):
        body = ''.join('<tr>' + ''.join('<td>' + html.escape(f'{v:,}' if isinstance(v, int) else v) + '</td>'
                                      for v in row) + '</tr>' for row in items)
        return '<div class="table-wrap"><table><thead><tr><th>Measure</th><th>Recorded evidence</th><th>Meaning</th></tr></thead><tbody>' + body + '</tbody></table></div>'
    page = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Known World</title>
<meta property="og:title" content="Known World"><meta property="og:description" content="January to October 2026 in ninety seconds: projects as land, work as flashes, and the growing scale of AI collaboration.">
<meta property="og:image" content="POSTER"><meta property="og:type" content="video.other"><meta property="og:video" content="VIDEO">
<style>
:root{color-scheme:dark;--bg:#07090e;--fg:#e8edf6;--muted:#96a3b9;--line:#293141}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--fg);font-family:ui-monospace,Menlo,Consolas,monospace}
.stage{height:100vh;height:100dvh;display:flex;align-items:center;justify-content:center}
video{display:block;width:min(100vw,calc(100dvh * 16 / 9));height:auto;aspect-ratio:16/9;background:#000}
main{max-width:1100px;margin:0 auto;padding:28px 20px 60px}h1{font-size:20px;font-weight:500;margin:0 0 12px}h2{font-size:16px;font-weight:500;margin:32px 0 12px}
p{color:var(--muted);font-size:13px;line-height:1.7;margin:12px 0}.snapshot{color:var(--fg)}
.table-wrap{width:100%;overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:12px;line-height:1.6}th,td{text-align:left;vertical-align:top;padding:11px 12px;border-bottom:1px solid var(--line)}th{color:var(--muted);font-weight:500}td:first-child{width:25%}td:nth-child(2){width:24%;font-variant-numeric:tabular-nums}td:last-child{color:var(--muted)}
@media(max-width:600px){main{padding:24px 12px 44px}th,td{padding:10px 7px;font-size:11px}td:first-child{width:27%}td:nth-child(2){width:25%}}
</style></head><body>
<div class="stage"><video src="VIDEO" poster="POSTER" controls playsinline preload="metadata"></video></div>
<main><h1>Known World</h1>
<p>January to October 2026 in ninety seconds. Land is projects; each flash is a burst of focused work, sized by what it produced; each color is a collaborator, human or machine. The score below traces their activity, with additional rows for execution, research and benchmark history. Listen with headphones.</p>
<p class="snapshot">Evidence through October 9, 2026, 15:41 UTC · Updated October 10, 2026</p>
<h2>Recorded work and activity</h2>DATED_TABLE
<p>The large sidebar figures labelled “bursts” count animation episodes. Gemini and local figures labelled “calls” count HEARTH dispatches. Git totals use recorded commit authors; burst credit can use session evidence. Calls, invocations and benchmark jobs are overlapping views of work and should not be added together. The recorded peak is PEAK invocations at once and BENCH_PEAK overlapping benchmark runs; this partial history does not measure GPU utilization or the lab’s capacity ceiling.</p>
<h2>Recovered history and remaining coverage</h2>COVERAGE_TABLE
<p>The animation uses explicit dates and native identities. Undated results remain visible here as evidence of scale, without being assigned invented dates in the film.</p>
</main></body></html>'''
    for key, value in {'VIDEO': names['video'], 'POSTER': names['poster'],
                       'DATED_TABLE': table(rows), 'COVERAGE_TABLE': table(coverage),
                       'BENCH_PEAK': str(counts['bench_overlap_peak']), 'PEAK': str(counts['overlap_peak'])}.items():
        page = page.replace(key, value)
    (out / 'index.html').write_text(page)
    if opening_seconds:
        page = page.replace('in ninety seconds', 'in ninety-five seconds')
        page = page.replace('Listen with headphones.</p>', 'A five-second visual key opens the film. Connection paths hold for five story days after recorded activity, then fade out by day seven. Listen with headphones.</p>')
        (out / 'index.html').write_text(page)
    if closing_fade_seconds:
        page = page.replace('in ninety-five seconds', 'in ninety-eight seconds')
        (out / 'index.html').write_text(page)
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    for arg in ('build', 'video', 'poster', 'out'):
        ap.add_argument('--' + arg, type=Path, required=True)
    ap.add_argument('--opening-seconds', type=int, default=0)
    ap.add_argument('--closing-fade-seconds', type=int, default=0)
    args = ap.parse_args()
    manifest = package(args.build, args.video, args.poster, args.out, args.opening_seconds, args.closing_fade_seconds)
    print(json.dumps({'snapshot': manifest['snapshot_utc'], 'assets': manifest['assets']}))
