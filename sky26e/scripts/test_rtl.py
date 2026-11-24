#!/usr/bin/env python3
"""Port-level digital verification; the analog boundary is explicitly behavioral."""
from pathlib import Path
import subprocess, json, hashlib, shutil, re
root=Path(__file__).resolve().parents[1]
out=root/'build'/'rtl';out.mkdir(parents=True,exist_ok=True)
sources=[root/'rtl'/n for n in ['diff8_uart_tx.v','diff8_uart_rx.v','diff8_digital.v','tt_um_dvirdc_sky130_diff8.v']]+[root/'sim/phy_behavioral.v',root/'sim/tb.sv']
exe=shutil.which('iverilog');vvp=shutil.which('vvp')
if not exe or not vvp:raise SystemExit('iverilog and vvp are required')
subprocess.run([exe,'-g2012','-Wall','-s','tb','-o',str(out/'test.vvp'),*map(str,sources)],check=True)
p=subprocess.run([vvp,str(out/'test.vvp')],capture_output=True,text=True,timeout=240)
(out/'simulation.log').write_text(p.stdout+p.stderr)
print(p.stdout+p.stderr,end='')
m=re.search(r'ALL_PASS tests=(\d+)',p.stdout)
summary={'passed':p.returncode==0 and m is not None,'tests':int(m.group(1)) if m else 0,'boundary':'digital behavioral; not transistor/PEX/physical verification','source_sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sources}}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
raise SystemExit(0 if summary['passed'] else 1)
