#!/usr/bin/env python3
"""Reproduce the isolated snapshot-reset area and external-pin regressions."""
from pathlib import Path
import json,hashlib,re,subprocess,os
EXP=Path(__file__).resolve().parent;SKY=EXP.parents[1];OUT=SKY/'build/snapshot_reset_reproduced';OUT.mkdir(parents=True,exist_ok=True)
PDK=Path(os.environ.get('PDK_ROOT',str(SKY.parent.parent/'toolchain/pdk/sky130A')))
assert '0536d02d875c8f67dd7cca3902ac457e62f20005' in (PDK/'SOURCES').read_text()
LIB=PDK/'libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
COMMON=[SKY/'rtl/diff8_uart_tx.v',SKY/'rtl/diff8_uart_rx.v']
EXTRAS=[SKY/'rtl/tt_um_dvirdc_sky130_diff8.v',SKY/'sim/phy_behavioral.v']
MODELS=[PDK/'libs.ref/sky130_fd_sc_hd/verilog'/p for p in ['primitives.v','sky130_fd_sc_hd.v']]
areas={}
for name,source in [('baseline',EXP/'baseline.v'),('trial',EXP/'diff8_digital.v')]:
 ys='read_verilog '+' '.join(map(str,COMMON+[source]))+f'\nhierarchy -check -top diff8_digital\nsynth -top diff8_digital -flatten -noabc\ndfflibmap -liberty {LIB}\nabc -liberty {LIB}\nread_liberty -lib {LIB}\nclean\ncheck -assert\nstat -liberty {LIB}\nwrite_verilog -noattr {OUT}/{name}_mapped.v\n'
 (OUT/f'{name}.ys').write_text(ys)
 with (OUT/f'{name}_map.log').open('w') as log:subprocess.run(['yosys','-Q','-s',str(OUT/f'{name}.ys')],stdout=log,stderr=subprocess.STDOUT,check=True)
 areas[name]=float(re.search(r'Chip area for module.*: ([0-9.]+)',(OUT/f'{name}_map.log').read_text())[1])
results={}
for name,files,defines in [('rtl',COMMON+[EXP/'diff8_digital.v']+EXTRAS+[SKY/'sim/tb.sv'],[]),('mapped',[OUT/'trial_mapped.v']+EXTRAS+[SKY/'sim/tb.sv']+MODELS,['-DFUNCTIONAL','-DUNIT_DELAY=#1']),('reset',COMMON+[EXP/'diff8_digital.v']+EXTRAS+[EXP/'tb_snapshot_reset.sv'],[])]:
 exe=OUT/f'{name}.vvp';subprocess.run(['iverilog','-g2012',*defines,'-s','tb','-o',str(exe),*map(str,files)],check=True)
 p=subprocess.run(['vvp',str(exe)],capture_output=True,text=True,timeout=240);(OUT/f'{name}.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0 and 'ALL_PASS tests=44' in p.stdout,name
 results[name]={'tests':44,'passed':True}
 if name=='reset':results[name]['zero_snapshot_byte_reads']=int(re.search(r'SNAPSHOT_RESET_READS=(\d+)',p.stdout)[1])
summary={'scope':'isolated area/functional experiment; no physical qualification','areas_um2':areas,'results':results,'inputs_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [EXP/'baseline.v',EXP/'diff8_digital.v',EXP/'tb_snapshot_reset.sv',SKY/'sim/tb.sv',LIB]}}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
