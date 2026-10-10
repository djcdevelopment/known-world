from pathlib import Path
import subprocess,imageio_ffmpeg
r=Path(__file__).resolve().parent;ff=imageio_ffmpeg.get_ffmpeg_exe()
def run(a):subprocess.run([ff,'-y','-loglevel','error',*map(str,a)],check=True)
for folder,name in [('intro-frames','intro'),('frames','story')]:run(['-f','concat','-safe',0,'-i',r/folder/'segments.txt','-c','copy',r/(name+'.mp4')])
(r/'joined.txt').write_text(f"file '{r/'intro.mp4'}'\nfile '{r/'story.mp4'}'\n")
run(['-f','concat','-safe',0,'-i',r/'joined.txt','-map','0:v','-c:v','copy',r/'picture.mp4'])
run(['-i',r/'picture.mp4','-i',r/'build/audio.wav','-map','0:v','-map','1:a','-c:v','copy','-af','adelay=5000:all=1','-c:a','aac','-b:a','256k','-movflags','+faststart',r/'known-world-95s.mp4'])
for t in [2,57,80,93]:run(['-ss',t,'-i',r/'known-world-95s.mp4','-frames:v',1,r/'validation'/f'decoded-{t}.png'])
