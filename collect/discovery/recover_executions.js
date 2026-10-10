// Run in Codex functions.exec, with tools globals. Read-only canonical API calls.
// Edit these two paths for a new recovery. Never print or persist full projections.
const worklist = 'corpus/activity/execution-job-worklist.json';
const destination = 'corpus/activity/canonical-executions-NEW.json';
const root = '/home/derek/work/known-world/';
for (const p of [worklist, destination]) {
  if (!/^corpus\/activity\/[A-Za-z0-9_-]+\.json$/.test(p)) throw Error('Invalid path');
}
const exists = await tools.exec_command({cmd: "test -e '" + root + destination + "'", max_output_tokens: 100});
if (exists.exit_code === 0) throw Error('Existing recovery preserved; choose a new destination');
const read = await tools.exec_command({cmd: "cat '" + root + worklist + "'", max_output_tokens: 120000});
if (read.exit_code !== 0) throw Error('Worklist unavailable');
const ids = Object.keys(JSON.parse(read.output).jobs).sort();
if (ids.some(id => !/^job_[0-9a-f]{32}$/.test(id))) throw Error('Invalid native job ID');
const result = {source: 'hearth.get_execution', requested: ids.length, jobs: [], failures: []};
const fields = ['invocation_id', 'started_at', 'finished_at', 'status', 'backend', 'model', 'tokens_in', 'tokens_out'];
let next = 0;
async function worker() {
  while (next < ids.length) {
    const id = ids[next++];
    try {
      const raw = await tools.mcp__hearth__get_execution({job_id: id});
      const obj = JSON.parse(raw.content.find(c => c.type === 'text').text);
      if (obj.job_id !== id || !Array.isArray(obj.invocations)) throw Error('Unavailable projection');
      result.jobs.push({job_id: id, operation: obj.operation,
        invocations: obj.invocations.map(inv => Object.fromEntries(fields.map(k => [k, inv[k] ?? null])))});
    } catch (_) {
      result.failures.push({job_id: id, error_code: 'unavailable_or_invalid_projection'});
    }
  }
}
await Promise.all(Array.from({length: 4}, worker));
result.jobs.sort((a, b) => a.job_id.localeCompare(b.job_id));
const patch = '*** Begin Patch\n*** Add File: ' + root + destination + '\n' +
  JSON.stringify(result, null, 1).split('\n').map(s => '+' + s).join('\n') + '\n*** End Patch';
await tools.apply_patch(patch);
text({requested: ids.length, recovered: result.jobs.length, unavailable: result.failures.length, destination});
