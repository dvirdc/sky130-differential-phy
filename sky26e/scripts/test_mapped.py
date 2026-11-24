#!/usr/bin/env python3
"""Functional mapped-cell regression. No SDF, STA, analog or PEX claims."""
from pathlib import Path
import subprocess, os, json, hashlib, re
root=Path(__file__).resolve().parents[1]
pdk=Path(os.environ.get('PDK_ROOT',str(root.parents[1]/'toolchain/pdk/sky130A')))
assert '0536d02d875c8f67dd7cca3902ac457e62f20005' in (pdk/'SOURCES').read_text()
out=root/'build/rtl'; out.mkdir(parents=True,exist_ok=True)
lib=pdk/'libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
sources=[root/'rtl'/n for n in ['diff8_uart_tx.v','diff8_uart_rx.v','diff8_digital.v']]
script='read_verilog '+' '.join(str(p) for p in sources)+f"\nhierarchy -check -top diff8_digital\nsynth -top diff8_digital -flatten -noabc\ndfflibmap -liberty {lib}\nabc -liberty {lib}\nread_liberty -lib {lib}\nclean\ncheck -assert\nstat -liberty {lib}\nwrite_verilog -noattr {out}/sky130_mapped.v\n"
(out/'map.ys').write_text(script)
with (out/'sky130-map.log').open('w') as f:subprocess.run(['yosys','-Q','-s',str(out/'map.ys')],stdout=f,stderr=subprocess.STDOUT,check=True)
models=[pdk/'libs.ref/sky130_fd_sc_hd/verilog'/f for f in ['primitives.v','sky130_fd_sc_hd.v']]
extras=[root/'rtl/tt_um_dvirdc_sky130_diff8.v',root/'sim/phy_behavioral.v',root/'sim/tb.sv']
subprocess.run(['iverilog','-g2012','-DFUNCTIONAL','-DUNIT_DELAY=#1','-s','tb','-o',str(out/'mapped-test.vvp'),str(out/'sky130_mapped.v'),*map(str,extras+models)],check=True)
p=subprocess.run(['vvp',str(out/'mapped-test.vvp')],capture_output=True,text=True,timeout=240)
(out/'mapped-simulation.log').write_text(p.stdout+p.stderr)
m=re.search(r'ALL_PASS tests=(\d+)',p.stdout)
summary={'passed':p.returncode==0 and bool(m),'tests':int(m.group(1)) if m else 0,'scope':'functional SKY130 HD mapped gates with uniform 1ns model delay; no SDF/STA or extracted analog','source_sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sources+extras},'library_sha256':hashlib.sha256(lib.read_bytes()).hexdigest(),'netlist_sha256':hashlib.sha256((out/'sky130_mapped.v').read_bytes()).hexdigest()}
(out/'mapped-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
raise SystemExit(0 if summary['passed'] else 1)
