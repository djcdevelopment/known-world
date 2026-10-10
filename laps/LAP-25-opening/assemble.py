from pathlib import Path
import subprocess,json
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe();root=Path(__file__).resolve().parent
old=root.parent/'LAP-23-experimental-shapes/site/known-world-90s-7fdfb10711d7.mp4'
def run(args):subprocess.run([ff,'-y','-loglevel','error',*map(str,args)],check=True)
intro=root/'intro.mp4'
run(['-f','concat','-safe',0,'-i',root/'frames-short/segments.txt','-c','copy',intro])
joined=root/'joined.txt';joined.write_text(f"file '{intro}'\nfile '{old}'\n")
run(['-f','concat','-safe',0,'-i',joined,'-map','0:v','-c:v','copy',root/'picture.mp4'])
run(['-i',root/'picture.mp4','-i',root.parent/'LAP-23-experimental-shapes/build-final/audio.wav','-map','0:v','-map','1:a','-c:v','copy','-af','adelay=5000:all=1','-c:a','aac','-b:a','256k','-movflags','+faststart',root/'known-world-95s.mp4'])
# Compare decoded pixel hashes of every original story frame after the opener.
def hashes(path,skip=0):
 args=[ff,'-loglevel','error','-i',str(path),'-map','0:v']
 if skip:args+=['-vf',f'select=gte(n\\,{skip})']
 args+=['-f','framemd5','-']
 s=subprocess.check_output(args,text=True)
 return [x.rsplit(',',1)[-1].strip() for x in s.splitlines() if x and not x.startswith('#')]
a=hashes(old);b=hashes(root/'known-world-95s.mp4',150);assert a==b,(len(a),len(b))
(root/'validation/story-pixels.json').write_text(json.dumps({'identical_decoded_story_frames':len(a),'opening_frames':150,'audio_delay_ms':5000},indent=2)+'\n')
print('Story pixels identical:',len(a))
