# Evidence discovery by shape

The earlier **41** was a count of finished B70tools/Vllama runner manifests, not a census of benchmarks. The film now foregrounds **1,487 measured experiment trials**, with **436 benchmark configurations**, **298 recorded benchmark runners**, **11,388 direct research attempts**, and **4,533 undated image results** separately labelled. These units overlap. Neither runner counts nor observed trial counts measure Derek's working hours.

## How the search changed

`collect/knownworld/hunt_shapes.py` inventories eligible filenames first, then reads representative schema keys and safe metadata across known roots. It learns native llama-bench records, explicit runner intervals, request traces, pressure-trial results, source-hashed exports, receipts and hardware probes. File size is a reader-selection hint, not evidence of work. Structured content stays metadata only; prompt/answer/body files, credentials, models, caches and dependencies are excluded.

Experiment outputs are often **gitignored**, so the discovery uses `rg --files --hidden --no-ignore` with explicit exclusions. It has a read-only directory-walk fallback on AM4/FX99 where ripgrep is absent. Per-directory schema sampling and read errors are reported, not disguised as whole-disk completeness. The unignored discovery inventories 769,691 C-work paths, 900,030 E-work paths and 572,864 Linux-work paths; source inventories also include E-omen, AM4 work and FX99 benchmark/fleet roots. These are metadata search counts, not added file/work totals.

Living documents (`LOCAL-MODEL-LAB-INDEX`, `ROTATION-PROGRAM`, `OMEN-LIMIT-TEST`, the Windtunnel log and September 19 retrospective) provide source paths and recorded experiment identities. Their prose claims are not added as additional experiments. Source SHA catalogs trigger a historical-Git search when the current tree no longer contains their artifacts.

The source-shape map, broad inventories, document leads, source hash reconciliation and remaining classifications are in `corpus/discovery/20261010-experimental/`. `EVIDENCE-HUNT.md` records the reusable workflow.

## Recovered and reconciled work

- **436 distinct native llama-bench configuration records**, preserving all previous 210. The broader pass added 226 from Denning, additional Battlemage probes/campaign benches and retained control records. Their **1,242 repeated measured samples** are counted explicitly as trials; repeated samples are not configuration rows.
- **3,356 copied configuration rows folded** by canonical native row identity. Worktrees, migrated repos and normalized backfills are not additional runs. Retained configuration ownership is where the record was found, not a claim about accelerator placement.
- **176 Denning request trials** from non-dry native `bench-<epoch>.jsonl` traces. The harness stamps that epoch at campaign completion: requests are shown as recorded at that completion, not given invented exact per-request dates. Admission/rejection remains metadata; `bench-dry` and duplicate `.summary.json` views are excluded.
- **Nine Denning pressure comparisons** from native `ts` result records; watchdog samples are excluded.
- **60 Memsplice experiment records** with original explicit start/end metadata. All **59 public source artifacts** were recovered from historical Git revision `5b17e02`; 58 hashes match the Windows CRLF checkout and one matches the Git blob directly. Source-hash identity folds public numeric exports and source results. Four source rows have no interval and remain undated coverage. Prompt bodies, generated answers, command lines and server addresses do not enter the sidecar.
- **1,487 total measured trials** = 1,242 native repeated samples + 176 request trials + nine pressure comparisons + 60 KV/backend experiments. This is a view of explicit measured trials, not an additive total alongside configurations, runner manifests or direct research attempts.
- **4,533 undated image results** now appear on the ending card with an explicit outside-the-timeline label; dates are not invented to animate them.

The frozen sidecar is `corpus/activity/20261010-experimental-recovery.json`; the compiler pins it and source coverage. Native benchmark timing samples contain about 4.99 summed measurement-hours, a narrow kernel/runtime measurement subset. This excludes setup, exploration, prefill/decode request experiments outside those sample arrays, troubleshooting and operator time; it is not presented as the hundreds of hours Derek worked.

## Other discovered shapes and explicit limits

Windows `ai-dev-system/output/runs` has 17 dated workflow manifests. Their workflow executions are not classified as benchmarks by filename. New AM4 dual-NVIDIA probe outputs are request-result records under dated campaign roots, not native llama-bench sample arrays. Linux Bench27/delivery records mix model outputs, review artifacts and measured calls; they are not classified from a generic `duration_ms` key alone. Tensor results mix native probes, summaries and untimed records. These remain categorized evidence leads rather than inflated benchmark counts. Existing Git activity still includes those projects where collected.

Coverage is partial: four undated Memsplice rows, older unlogged inference, missing VM archives, model-output-only records and representative schema omissions remain explicit. A discovered file, report, Git commit or changed SHA never automatically becomes a trial. Next readers can add verified adapters from the shape inventory without asking Derek to recall another project directory.

## Validation

Six existing focused checks passed in 0.009 seconds. Source identity/count assertions establish all prior configuration IDs remain, 59 Memsplice hashes verify, dry traces are excluded and the 1,487/436 counts are exact. Compiled counts match sources; previous world totals, soundtrack, 845 bursts, direct attempts, sessions and runner counts are unchanged. Desktop and portrait stills were inspected before one final film export. Validation is in `validation/`.

FX99 7B advisory job `job_d83abc526cc5f09c47161c0d4aac2e58` was reviewed by the frontier: partly useful format suggestions; its overlong answer and generic claims were not applied as evidence or code. No benchmark, model build, seat restart or cloud inference was performed.

## Published and checked

Live URL: https://fx99.tail8e749c.ts.net/chronicles/known-world/

Data SHA-256 `b395981fcd1e6a86dc91efdad9d198e5fb47dc62345f90e9ac28f2c5488cf1b4`; video SHA-256 `7fdfb10711d7a5eab6aed4a866365c7b065817a59dccc07a5208f2dc3224ef57`. One fresh 2,700-frame export, four workers, 46.391 seconds; no reused segments. Live index, manifest, poster and video match the packaged hashes. Byte-range playback returned 206. Actual served video played and decoded the ending at 88 seconds on desktop and phone; 1,487 trials, 436 configurations, 298 runners and 11,388 direct attempts matched public tables. No page errors or horizontal overflow. The decoded ending was inspected and shows the 4,533 explicitly undated image results as well.

Publication used an exclusive lock, unchanged-baseline check, SHA checks and atomic index replacement last. Previous release backup: FX99 `/home/derek/backups/known-world-publish/20261010-experimental-shapes`. Lock released after live verification; no service restart.
