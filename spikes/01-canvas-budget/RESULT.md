# 01-canvas-budget result

Headless Chromium (Playwright 1.64, chromium-1248), 1920x1080, DPR 1, software rendering. 10 frames per N after 2 warm-up frames. "Render" is the in-page performance.now() around render(t); "screenshot" is page.screenshot({type:'png'}); "total" is the whole per-frame round trip.

| N tiles | render ms (med / max) | screenshot ms (med / max) | total ms (med / max) | 20,000-frame export (min, at median total) |
|---|---|---|---|---|
| 5,000  | 3.4 / 3.6   | 244.8 / 255.3 | 249.1 / 259.6 | 83.0  |
| 20,000 | 11.6 / 13.2 | 258.1 / 272.3 | 270.6 / 285.3 | 90.2  |
| 80,000 | 56.9 / 67.3 | 280.6 / 294.7 | 335.8 / 360.8 | 111.9 |

WebGL2: `document.createElement('canvas').getContext('webgl2')` is non-null (true; software, no GPU).

Encode (N=20000, 60 PNG frames, 2 s 48 kHz stereo 440 Hz pinging tone, libx264 crf18 + aac): out.mp4 is 1,481,257 bytes, duration 2.00 s, h264 High yuv420p 1920x1080 30 fps plus aac LC 48000 Hz stereo; ffmpeg encode time 0.41 s (PNG decode included).

Caveat: the render ms is JS command-recording time only; Chromium rasterizes the canvas lazily at capture, so raster cost is inside the screenshot column.

## Implications (11 min at 30 fps = 19,800 frames)
1080p CPU export is feasible but slow: roughly 1.4 to 1.9 hours per 11-minute piece with the screenshot path at any of these tile counts, which is acceptable for an offline batch. Capture (PNG screenshot plus the rasterization it forces, about 245 to 280 ms/frame) is the bottleneck at every N, and canvas JS time only becomes material at 80k tiles (57 ms); ffmpeg encode is negligible. The obvious levers are replacing page.screenshot with canvas.toDataURL/toBlob (JPEG or raw ImageData, skipping the full-page compositor and PNG compression), piping frames straight into ffmpeg instead of disk, running several browser pages in parallel across cores, and dropping to 24 fps or 1600x900 for roughly 20 to 45 percent fewer pixels or frames.
