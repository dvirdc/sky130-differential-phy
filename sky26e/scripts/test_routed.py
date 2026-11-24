#!/usr/bin/env python3
"""External-pin regression of the actual routed, powered digital netlist.

Uniform 1 ns functional cell models; analog PHY uses the boundary model.
This is not SDF simulation or a transistor-level simulation of the whole chip.
"""
from pathlib import Path
import subprocess,sys,json,hashlib,re
root=Path(__file__).resolve().parents[1];run=Path(sys.argv[1]).resolve()
pdk=root.parents[1]/'toolchain/pdk/sky130A'
out=root/'build/rtl'/run.name;out.mkdir(parents=True,exist_ok=True)
netlist=next(run.glob('*-openroad-fillinsertion/*.pnl.v'))
models=[pdk/'libs.ref/sky130_fd_sc_hd/verilog'/f for f in ['primitives.v','sky130_fd_sc_hd.v']]
inputs=[netlist,root/'sim/phy_behavioral.v',root/'sim/tb.sv',*models]
exe=out/'test.vvp'
subprocess.run(['iverilog','-g2012','-DFUNCTIONAL','-DUSE_POWER_PINS','-DUNIT_DELAY=#1','-s','tb','-o',str(exe),*map(str,inputs)],check=True)
p=subprocess.run(['vvp',str(exe)],capture_output=True,text=True,timeout=360)
(out/'simulation.log').write_text(p.stdout+p.stderr)
m=re.search(r'ALL_PASS tests=(\d+)',p.stdout)
summary={'passed':p.returncode==0 and bool(m),'tests':int(m[1]) if m else 0,'scope':__doc__.strip(),'inputs_sha256':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in inputs}}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));raise SystemExit(0 if summary['passed'] else 1)
