"""export/encode.py: concat the segments (-c copy) and mux the WAV as AAC 256 kb/s. ffmpeg from imageio-ffmpeg."""
import os
import subprocess
import sys

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise SystemExit(r.stderr[-3000:])
    return r.stderr


def encode(outdir, wav, final):
    video = os.path.join(outdir, "video.mp4")
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(outdir, "segments.txt"), "-c", "copy", video])
    run([FFMPEG, "-y", "-loglevel", "error", "-i", video, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", final])
    return final


if __name__ == "__main__":
    encode(sys.argv[1], sys.argv[2], sys.argv[3])
