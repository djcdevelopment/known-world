# LAP-21: audit and correction of published counts

Derek reported that visible sidebar numbers and totals did not reflect the recovered history. The previous
publication validation established matching release assets and playback, but failed to check whether each
visible counter had a clear and consistent meaning. This audit traced raw source records to compiled series,
actual canvas text and decoded frames in the live video before reporting completion.

## Findings and corrections

- The 18,447,909 quantity is recorded git line changes, not newly discovered files. It was already present in
  uncapped numstat; the earlier display cap hid part of it. Research did not discover eighteen million new files.
- World file touches reconcile exactly: 88,827 git touches + 116,099 non-bulk creations + 4,922 update observations
  = 209,848. Those are cumulative observations, not distinct files. Native attribution is retained; filesystem
  observations are not arbitrarily credited to a model.
- Large sidebar values such as Claude 453 and Codex 82 counted derived bursts, not commits or calls. They now say
  bursts explicitly. Git file totals now say git touches. ChatGPT's 451 linked-file yield no longer says files.
- Local participation included 88 possibly overlapping tool observations: 22,760 records versus 22,672 dispatches
  in the header. Both sidebar and header now count the same 22,672 native HEARTH dispatch records. Gemini's exact
  1,057 calls and local calls are visible as large, labelled figures.
- Session participation counted mirrored source records repeatedly. Claude's 1,925 session records resolve to
  498 distinct native sessions; Codex's 481 resolve to 253. ChatGPT has 157 and OpenCode 24. Earliest observation
  per class/native ID drives the cumulative counter. These values now appear explicitly in sidebar and ending.
- Ending participation fields came from launch participation rather than native activity, leaving Gemini at zero
  and local at 119. Ending rows now use the same native participation series as the sidebar, and include all six
  recovered activity totals. The crowded old table was replaced with a clear unit-labelled table and file breakdown.

Git counts remain 9,784 commits and 18,447,909 line changes. Commit authors and session-derived burst credit remain
different views: a Codex-credited burst can cover commits with a different recorded author. The page explains this
instead of inventing model attribution for recorded human commits. Research findings are records, not acceptance
verdicts. Calls, jobs and benchmark runs are overlapping views and are not added into a fictitious grand total.

## Evidence and publication

`source-audit.json` is an independent raw-record aggregate, filtered to 2026 through the pinned snapshot; it checks
commit SHA uniqueness, native session IDs, exact backend/source dispatch selection and filesystem exclusion rules.
All final nation commit/touch/add/remove arrays, native participation counters and ending-row values reconcile.
`rendered-text-audit.json` captures actual canvas fillText calls at frames 2520 and 2640, verifying sidebar labels,
exact calls/session values and the ending world breakdown. Both orientations were visually checked.

Six existing activity fixtures passed in 0.011 seconds, JavaScript syntax checks and git diff --check passed.
845 launches and the original WAV SHA-256 remain unchanged. The corrected film rendered all 2,700 frames once,
with four workers, in 46.738 seconds, no reused segments or browser errors. No new benchmark was run.

Published at https://fx99.tail8e749c.ts.net/chronicles/known-world/ via versioned assets and atomic index replacement.
The prior published release is backed up on FX99 at `/home/derek/backups/known-world-publish/20261010-count-audit`.
An exclusive publication lock and unchanged-baseline checks were used; the lock was released after verification.

Live HTML, manifest, poster and film hashes match the audited release. Video range returns 206. Desktop and phone
browser checks confirm playback, seeks to 84/88 seconds, 90-second duration, 21 public evidence rows and corrected
session/call values, with no browser errors or horizontal page overflow. `stills/live-1920-88.png` shows the corrected
ending table decoded from the deployed video; `stills/live-1920-84.png` shows the live corrected sidebar.

Data SHA-256: `951895754c45cfd51689c7ec39cf5a756b9c8bfe1640f4bb90e256678c34f028`.
Video SHA-256: `bae1b69c1fe103472dc0a34727557af7fde93adabca789dbd187df93a946a786`.
HEARTH engineering receipt: `br-20261010-155657-7bb6b112`.
