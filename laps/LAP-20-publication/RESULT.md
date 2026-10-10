# LAP-20: recovered history published on FX99

Live: https://fx99.tail8e749c.ts.net/chronicles/known-world/

The existing 90-second video page now serves the validated LAP-19 film, a complete-snapshot poster and a public
evidence table. It includes Gemini, Antigravity, benchmark, research and fleet activity, plus uncapped numeric
line changes. The soundtrack and map retain the existing rendering. The film's evidence cutoff is explicitly
October 9, 2026, 15:41 UTC; the publication date is October 10.

The summary keeps three distinctions visible: dated activity, copied code/run history already folded into totals,
and undated or unavailable history. Conductor's 36 commits remain included once; 4,533 valid AM4 image-benchmark
results remain outside the timeline and visible as undated coverage. Later MechNet archive gaps remain explicit.
Calls, invocations and benchmark jobs are separate overlapping views; the page explains why they are not summed.
The public manifest and HTML contain aggregate counts and authored interpretations, without native IDs, private
repository URLs, source paths or transcript content. Detailed recovery records stay local.

## Build and release

All 2,700 frames rendered once with four workers in 47.056 seconds; zero reused segments and zero browser errors.
The film is H.264 1920×1080 at 30 fps, 90 seconds, with the existing audio muxed as stereo AAC at 256 kb/s.
`export/publication.py` checks the reviewed data hash and packages the video, poster, public HTML and release.json.

Data SHA-256: `62012e6d05475a414cdf50530b8005e66943fbed0649781b335c38b99978e656`.
Video SHA-256: `b58c7df86cf1f36c3c68d593402eafb811207138173ce89cf6eee5c5b42b58f4`.
Poster SHA-256: `078f51e936f584c5f247fb421b89fe90cd7110c4eaf26eab92467a5a24488f1f`.

Publication acquired the exclusive directory `/srv/sites/chronicles/.known-world-publish.lock`. The previous
HTML, video and poster were backed up on FX99 to `/home/derek/backups/known-world-publish/20261010-b58c7df86cf1`.
Staged assets were hash-checked, and all original files were rechecked against the preflight baseline before
replacement. Versioned media were placed first, release.json next, and index.html atomically replaced last.
Caddy needed no restart. The lock was released after live verification.

Rollback: acquire the same exclusive publication lock, copy that backup's index.html to a temporary file in the
site directory and atomically replace the current index.html. The old video/poster filenames remain available,
so the previous page immediately works. Remove release.json, which describes the new version, when rolling back.
Release the lock after verifying the old page. No privileged command is required.

## Validation

- All twelve public dated totals reconcile to the reviewed compiler receipt and validated source counts.
- Local desktop and phone pages contain all sixteen evidence rows without horizontal page overflow.
- Live HTTPS HTML, manifest, video and poster return 200 and match staged hashes byte for byte.
- Video range request returns 206 with the correct first sixteen bytes and content range.
- Live desktop and phone browser checks confirm playback, seeking to 84 seconds, 90-second duration,
  1920×1080 media, native controls, inline playback and zero browser errors.
- Existing LAP-19 source reconciliation and six focused fixtures are reused; no benchmark or broad test suite ran.

Evidence: `live-http-checks.json`, `live-browser-checks.json`, `page-checks.json`, `validation.json`, `media-probe.txt`
and `frames/timing.json`. Stills include both orientations of the deployed page. `site/` is the exact release package.
HEARTH engineering receipt: `br-20261010-153817-6531009a`.

To package another reviewed film, use `python3 export/publication.py --build BUILD --video VIDEO --poster POSTER
--out NEW-SITE-DIRECTORY`. Preserve the same staging, exclusive-writer, baseline-hash and index-last sequence.
