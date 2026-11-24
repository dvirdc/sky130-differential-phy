#!/usr/bin/env python3
"""Run official OpenLane tools with host-backed Nix store; no Docker disk expansion."""
from pathlib import Path
import json, subprocess, sys
root=Path(__file__).resolve().parents[2]
tools=root.parent/'toolchain';image=tools/'openlane'
config=json.loads((image/'config.json').read_text())['config']
args=['docker','run','--rm','--tmpfs','/tmp:rw,size=2g','-v',str(image/'rootfs/nix')+':/nix:ro','-v',str(root)+':/work','-v',str(tools/'pdk')+':/pdk:ro','-w','/work']
for env in config['Env']:
 if env.startswith(('PATH=','NIX_PYTHONPATH=')):
  args+=['-e',env+(':/usr/local/bin:/usr/bin:/bin' if env.startswith('PATH=') else '')]
args+=['-e','PDK_ROOT=/pdk','sky26e-eda:local']
args+=sys.argv[1:] or ['python3','-m','openlane','--version']
raise SystemExit(subprocess.call(args))
