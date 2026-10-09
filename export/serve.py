"""export/serve.py: serve the repo over http on 127.0.0.1 so the player page can fetch audio.wav (a file:// page cannot).

    .venv/bin/python -I export/serve.py [port]      then open  http://127.0.0.1:PORT/render/index.html?data=../laps/LAP-13-player/build-full/kw-data.js
"""
import functools
import http.server
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
http.server.ThreadingHTTPServer(("127.0.0.1", port), h).serve_forever()
