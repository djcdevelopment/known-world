"""Fill pass: camera fills more of the map area; re-render the 90 s cut. No receipts (prototype)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "export"))
import lapkit as K
SETS = ["camera_start_fill=0.85", "camera_end_fill=0.96", "camera_pad=0.03"]
d = os.path.join(HERE, "build-cut")
K.cli_build(90, d, SETS, hash_only=False)
audio = K.read_wav(os.path.join(d, "audio.wav")); F = len(audio) // 1600
K.export_piece(os.path.join(d, "kw-data.js"), audio, F, 0, F, K.PROBE_F, os.path.join(HERE, "out", "cut"))
print(os.path.join(HERE, "out", "cut", "final.mp4"))
