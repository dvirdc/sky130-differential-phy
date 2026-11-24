#!/usr/bin/env python3
"""Generate and independently extract SKY130 device primitives; not full PHY layout."""
from pathlib import Path
import subprocess, json, re
root=Path(__file__).resolve().parents[1]
out=root/'build/physical/cells';out.mkdir(parents=True,exist_ok=True)
pdk=root.parents[1]/'toolchain/pdk'
devices=[('nfet_01v8',2,.15),('pfet_01v8',4,.15),('nfet_01v8',4,.15),('pfet_01v8',8,.15),('nfet_01v8',24,1),('pfet_01v8',12,1),('res_high_po_0p35',.35,28),('res_high_po_0p35',.35,1),('res_high_po_0p35',.35,20)]
results=[]
for kind,w,l in devices:
 name=f'{kind}_w{w}_l{l}'.replace('.','p');model='sky130_fd_pr__'+kind
 for suffix in ['.mag','.ext','.spice','.gds']:(out/(name+suffix)).unlink(missing_ok=True)
 # Extend only gate-contact M1 landing pads outward to meet met1.6 area.
 pads=''
 if l==.15:
  y=w/2+.275
  pads=f'box -0.145um {y-.115}um 0.145um {y+.235}um\npaint metal1\nbox -0.145um {-y-.235}um 0.145um {-y+.115}um\npaint metal1\n'
 script=f"""load {name} -silent
box 0 0 0 0
sky130::{model}_draw [dict merge [sky130::{model}_defaults] {{w {w} l {l}}}]
{pads}save {name}.mag
select top cell
drc check
drc catchup
puts "DRC_TOTAL=[drc list count total]"
puts "DRC_WHY=[drc listall why]"
extract all
ext2spice lvs
ext2spice
puts "BBOX=[box values]"
gds write {name}.gds
quit -noprompt
"""
 (out/(name+'.tcl')).write_text(script)
 cmd=['docker','run','--rm','-e','PDK_ROOT=/pdk','-v',str(pdk)+':/pdk:ro','-v',str(out)+':/work','sky26e-eda:local','magic','-dnull','-noconsole','-rcfile','/pdk/sky130A/libs.tech/magic/sky130A.magicrc',name+'.tcl']
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
 log=p.stdout+p.stderr;(out/(name+'.log')).write_text(log)
 m=re.search(r'DRC_TOTAL=(\d+)',log)
 net=out/(name+'.spice')
 result={'cell':name,'model':model,'w_um':w,'l_um':l,'drc_count':int(m[1]) if m else None,'extracted_model_found':net.exists() and model in net.read_text(),'tool_exit_code':p.returncode}
 results.append(result);print(json.dumps(result),flush=True)
(out/'summary.json').write_text(json.dumps({'scope':'individual generated primitive cells only; no connected PHY or integrated layout','cells':results},indent=2)+'\n')
raise SystemExit(0 if all(r['drc_count']==0 and r['extracted_model_found'] and r['tool_exit_code']==0 for r in results) else 1)
