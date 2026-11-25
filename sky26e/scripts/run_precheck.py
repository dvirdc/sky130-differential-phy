#!/usr/bin/env python3
"""Execute unmodified pinned TT precheck with isolated dependencies on the Mac."""
from pathlib import Path
import subprocess,sys,json
root=Path(__file__).resolve().parents[2];toolchain=root.parent/'toolchain'
custom=sys.argv[1:2]==['--python']
if not custom: (root/'sky26e/build/tools/tt/precheck/reports').mkdir(parents=True,exist_ok=True)
rel=None if custom else Path(sys.argv[1]).resolve().relative_to(root)
config=json.loads((toolchain/'openlane/config.json').read_text())['config']
nix_path=next(v[5:] for v in config['Env'] if v.startswith('PATH='))
args=['docker','run','--rm','--tmpfs','/tmp:rw,size=2g','-e','PDK_ROOT=/pdk','-e','PDK=sky130A','-e','PYTHONPATH=/work/sky26e/build/precheck-deps','-e','LD_LIBRARY_PATH=/work/sky26e/build/qhull-root/usr/lib/aarch64-linux-gnu','-e','PATH=/work/sky26e/build/precheck-deps/bin:/opt/eda-venv/bin:/usr/local/bin:'+nix_path+':/usr/bin:/bin','-v',str(toolchain/'openlane/rootfs/nix')+':/nix:ro','-v',str(root)+':/work','-v',str(toolchain/'pdk')+':/pdk:ro','-w','/work/sky26e/build/tools/tt/precheck','sky26e-eda:local','/opt/eda-venv/bin/python',* (sys.argv[2:] if custom else ['precheck.py','--gds','/work/'+str(rel),'--tech','sky130A'])]
raise SystemExit(subprocess.call(args))
