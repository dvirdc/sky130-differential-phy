#!/usr/bin/env python3
"""Independent transistor-level LVS of the final exported GDS, with no PHY blackbox."""
from pathlib import Path
import subprocess,sys,json,hashlib,re
root=Path(__file__).resolve().parents[2];run=Path(sys.argv[1]).resolve();candidate=Path(sys.argv[2]).resolve()
out=candidate/'verification';out.mkdir(exist_ok=True);top='tt_um_dvirdc_sky130_diff8';gds=candidate/'gds'/f'{top}.gds'
def local(p):return '/work/'+str(p.relative_to(root))
script=f'gds maskhints yes\ngds read {local(gds)}\nload {top}\nselect top cell\nextract do local\nextract no capacitance\nextract no coupling\nextract no resistance\nextract no adjust\nextract all\next2spice lvs\next2spice\nquit -noprompt\n'
(out/'extract.tcl').write_text(script)
args=['docker','run','--rm','--tmpfs','/tmp:rw,size=2g','-e','PDK_ROOT=/pdk','-v',str(root.parent/'toolchain/pdk')+':/pdk:ro','-v',str(root)+':/work','-w',local(out),'sky26e-eda:local','magic','-dnull','-noconsole','-rcfile','/pdk/sky130A/libs.tech/magic/sky130A.magicrc','extract.tcl']
with (out/'extract.log').open('w') as f:subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True)
s=next(run.glob('*-netgen-lvs/lvs_script.lvs')).read_text()
s=re.sub(r'set circuit1 \[readnet spice [^\]]+\]',f'set circuit1 [readnet spice {local(out)}/{top}.spice]',s)
s=re.sub(r'/nix/\S+/openlane/scripts/netgen/setup.tcl','/pdk/sky130A/libs.tech/netgen/sky130A_setup.tcl',s)
s=re.sub(r'/work/\S+/reports/lvs.netgen.rpt',local(out)+'/lvs.rpt',s).replace(' -blackbox','')
assert 'phy_reference.spice' in s,'Missing analog schematic reference'
(out/'lvs.tcl').write_text(s)
with (out/'netgen.log').open('w') as f:subprocess.run([sys.executable,str(root/'sky26e/tools/run_openlane.py'),'netgen','-batch','source',local(out/'lvs.tcl')],stdout=f,stderr=subprocess.STDOUT,check=True)
report=(out/'lvs.rpt').read_text();assert 'Final result: Circuits match uniquely.' in report
assert not re.search(r'cell sky130_diff_phy is a black box',report)
assert 'Number of devices: 29' in report
summary={'passed':True,'scope':'independent final GDS import, full transistor/resistor LVS, analog PHY explicitly included','gds_sha256':hashlib.sha256(gds.read_bytes()).hexdigest(),'extracted_spice_sha256':hashlib.sha256((out/f'{top}.spice').read_bytes()).hexdigest(),'reference_spice_sha256':hashlib.sha256((root/'sky26e/physical/phy_reference.spice').read_bytes()).hexdigest(),'lvs_report_sha256':hashlib.sha256(report.encode()).hexdigest()}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
