// Execute in Codex functions.exec (tools + text globals), from the Known World cwd.
// Reads the task-authored worklist, dispatches at most two local scouts concurrently,
// and preserves each candidate with its actual route/job metadata. No cloud fallback.
// Change task_id/out_dir in scouts.json for a new review; do not overwrite old evidence.
const read = await tools.exec_command({cmd: "cat /home/derek/work/known-world/collect/discovery/scouts.json", max_output_tokens: 8000});
if (read.exit_code !== 0) throw new Error("Scout worklist unavailable");
const spec = JSON.parse(read.output);
if (!/^corpus\/discovery\/[A-Za-z0-9_-]+\/scouts$/.test(spec.out_dir)) throw new Error("Invalid evidence destination");
let next = 0;
async function worker() {
  while (next < spec.scouts.length) {
    const item = spec.scouts[next++];
    if (!/^[A-Za-z0-9_-]+$/.test(item.id)) throw new Error("Invalid scout id");
    const destination = "/home/derek/work/known-world/" + spec.out_dir + "/" + item.id + ".json";
    const exists = await tools.exec_command({cmd: "test -e '" + destination + "'", max_output_tokens: 100});
    if (exists.exit_code === 0) { text({id: item.id, status: "existing_candidate_preserved"}); continue; }
    let result;
    try {
      const raw = await tools.mcp__hearth__local_generate({task_id: spec.task_id, task_family: item.task_family,
        files: item.files, prompt: spec.brief + "\n" + item.question, max_tokens: item.max_tokens, timeout_s: 180});
      result = JSON.parse(raw.content.find(c => c.type === "text").text);
    } catch (_) { result = {ok: false, error_code: "tool_or_decode_error"}; }
    const record = {scout: item.id, status: result.ok ? "awaiting_review" : "failed",
      cap_reached: result.tokens_out >= item.max_tokens, brief: item.question, result};
    const patch = "*** Begin Patch\n*** Add File: " + destination + "\n" +
      JSON.stringify(record, null, 2).split("\n").map(s => "+" + s).join("\n") + "\n*** End Patch";
    await tools.apply_patch(patch);
    text({id: item.id, status: record.status, cap_reached: record.cap_reached, backend: result.backend,
      model: result.model, job: result.execution?.job_id});
  }
}
const workers = await Promise.allSettled(Array.from({length: Math.min(2, Math.max(1, spec.parallelism || 1))}, worker));
for (const result of workers) if (result.status === "rejected") text({workflow_error: String(result.reason)});
