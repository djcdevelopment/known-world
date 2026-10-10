from pathlib import Path
import subprocess,json
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe();root=Path(__file__).resolve().parent
old=root.parent/'LAP-23-experimental-shapes/site/known-world-90s-7fdfb10711d7.mp4'
def run(args):subprocess.run([ff,'-y','-loglevel','error',*map(str,args)],check=True)
intro=root/'intro.mp4'
run(['-f','concat','-safe',0,'-i',root/'frames/segments.txt','-c','copy',intro])
joined=root/'joined.txt';joined.write_text(f"file '{intro}'\nfile '{old}'\n")
run(['-f','concat','-safe',0,'-i',joined,'-map','0:v','-c:v','copy',root/'picture.mp4'])
run(['-i',root/'picture.mp4','-i',root.parent/'LAP-23-experimental-shapes/build-final/audio.wav','-map','0:v','-map','1:a','-c:v','copy','-af','adelay=5000:all=1','-c:a','aac','-b:a','256k','-movflags','+faststart',root/'known-world-95s.mp4'])
