from pathlib import Path
import json,hashlib,subprocess
root=Path(__file__).resolve().parent
host='100.122.130.124';release='20261010-closing-fade';receipt='known-world-closing-fade-20261010'
def remote(code):return subprocess.check_output(['ssh',host,'python3','-'],input=code,text=True)
print(remote(f'''from pathlib import Path
import json,hashlib,shutil
root=Path('/srv/sites/chronicles/known-world');lock=Path('/srv/sites/chronicles/.known-world-publish.lock');lock.mkdir()
(lock/'owner.json').write_text(json.dumps({{'task':{receipt!r},'release':{release!r}}}))
backup=Path('/home/derek/backups/known-world-publish/{release}');backup.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline={{p.name:sha(p) for p in root.iterdir() if p.is_file()}}
(backup/'baseline.json').write_text(json.dumps(baseline))
for p in root.iterdir():
 if p.is_file():shutil.copy2(p,backup/p.name)
Path('/srv/sites/chronicles/.known-world-stage-{release}').mkdir()
print('Locked; rollback saved')
'''))
subprocess.run(['scp',*[str(p) for p in (root/'site').iterdir()],f'{host}:/srv/sites/chronicles/.known-world-stage-{release}/'],check=True)
expected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'site').iterdir()}
print(remote(f'''from pathlib import Path
import json,hashlib,os
root=Path('/srv/sites/chronicles/known-world');stage=Path('/srv/sites/chronicles/.known-world-stage-{release}')
assert json.loads(Path('/srv/sites/chronicles/.known-world-publish.lock/owner.json').read_text())['task']=='{receipt}'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads(Path('/home/derek/backups/known-world-publish/{release}/baseline.json').read_text())
assert {{p.name:sha(p) for p in root.iterdir() if p.is_file()}}==baseline
expected={expected!r}
assert {{p.name:sha(p) for p in stage.iterdir()}}==expected
for name in expected:
 if name not in ('index.html','release.json'):os.replace(stage/name,root/name)
os.replace(stage/'release.json',root/'release.json');os.replace(stage/'index.html',root/'index.html');stage.rmdir()
print('Published current and stable assets; index last')
'''))
