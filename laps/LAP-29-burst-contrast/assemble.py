from pathlib import Path
import subprocess,sys,numpy as np,imageio_ffmpeg
r=Path(__file__).resolve().parent;sys.path.insert(0,str(r.parents[1]/'compile'));import audio
ff=imageio_ffmpeg.get_ffmpeg_exe()
def run(a):subprocess.run([ff,'-y','-loglevel','error',*map(str,a)],check=True)
run(['-f','concat','-safe',0,'-i',r/'frames/segments.txt','-c','copy',r/'story.mp4'])
run(['-f','concat','-safe',0,'-i',r/'intro-frames/segments.txt','-c','copy',r/'intro.mp4'])
intro=r/'intro.mp4'
(r/'joined.txt').write_text(f"file '{intro}'\nfile '{r/'story.mp4'}'\n")
run(['-f','concat','-safe',0,'-i',r/'joined.txt','-map','0:v','-c:v','copy',r/'picture.mp4'])
source=(r.parent/'LAP-27-connection-memory/build/audio.wav').read_bytes()
x=np.frombuffer(source,dtype='<f4',offset=44).reshape(-1,2);split=87*48000
out=np.concatenate([x[:split],np.zeros((3*48000,2),dtype=np.float32),x[split:]])
audio.write_wav(r/'audio.wav',out)
run(['-i',r/'picture.mp4','-i',r/'audio.wav','-map','0:v','-map','1:a','-c:v','copy','-af','adelay=5000:all=1','-c:a','aac','-b:a','256k','-movflags','+faststart',r/'known-world-98s.mp4'])
for t in [2,80,92,93.5,94.95,95.5,96]:run(['-ss',t,'-i',r/'known-world-98s.mp4','-frames:v',1,r/'validation'/f'decoded-{t}.png'])
