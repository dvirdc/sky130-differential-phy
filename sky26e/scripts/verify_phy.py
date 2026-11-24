#!/usr/bin/env python3
"""Independently import macro GDS, check DRC/LVS, and extract distributed RC."""
from pathlib import Path
import sys,subprocess,json,re,hashlib
root=Path(__file__).resolve().parents[2]
phy=Path(sys.argv[1]).resolve();rel=phy.relative_to(root)
pdk=root.parent/'toolchain/pdk'
def magic(folder,script):
 folder.mkdir(parents=True,exist_ok=True);(folder/'check.tcl').write_text(script+'\nquit -noprompt\n')
 args=['docker','run','--rm','--tmpfs','/tmp:rw,size=1g','-e','PDK_ROOT=/pdk','-v',str(pdk)+':/pdk:ro','-v',str(root)+':/work','-w','/work/'+str(folder.relative_to(root)),'sky26e-eda:local','magic','-dnull','-noconsole','-rcfile','/pdk/sky130A/libs.tech/magic/sky130A.magicrc','check.tcl']
 p=subprocess.run(args,capture_output=True,text=True,timeout=240);(folder/'magic.log').write_text(p.stdout+p.stderr);assert p.returncode==0
 return p.stdout+p.stderr
prefix='gds maskhints yes\ngds read ../sky130_diff_phy.gds\nload sky130_diff_phy\nselect top cell\n'
log=magic(phy/'reimport',prefix+'drc check\ndrc catchup\nputs "DRC_TOTAL=[drc list count total]"\nputs "DRC_WHY=[drc listall why]"\nextract all\next2spice lvs\next2spice\n')
assert 'DRC_TOTAL=0\n' in log
out='/work/'+str(rel)+'/reimport'
subprocess.run([sys.executable,str(root/'sky26e/tools/run_openlane.py'),'netgen','-batch','lvs','/work/sky26e/physical/phy_reference.spice sky130_diff_phy',f'{out}/sky130_diff_phy.spice sky130_diff_phy','/pdk/sky130A/libs.tech/netgen/sky130A_setup.tcl',out+'/lvs.rpt','-json'],stdout=(phy/'reimport/netgen.log').open('w'),stderr=subprocess.STDOUT,check=True)
lvs=(phy/'reimport/lvs.rpt').read_text();assert 'Circuits match uniquely.' in lvs
magic(phy/'pex',prefix+'flatten phy_pex\nload phy_pex\nselect top cell\nextract all\next2sim labels on\next2sim\nextresist tolerance 10\nextresist all\next2spice lvs\next2spice cthresh 0\next2spice rthresh 0\next2spice extresist on\next2spice subcircuit top on\next2spice\n')
pex=(phy/'pex/phy_pex.spice').read_text()
result={'gds_sha256':hashlib.sha256((phy/'sky130_diff_phy.gds').read_bytes()).hexdigest(),'independent_gds_drc_errors':0,'lvs':'Circuits match uniquely','pex_resistors':sum(s.startswith('R') for s in pex.splitlines()),'pex_capacitors':sum(s.startswith('C') for s in pex.splitlines()),'pex_sha256':hashlib.sha256(pex.encode()).hexdigest()}
(phy/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
