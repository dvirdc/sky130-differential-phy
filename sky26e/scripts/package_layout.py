#!/usr/bin/env python3
"""Save the verified local candidate and evidence; refuse incomplete results."""
from pathlib import Path
import json,shutil,hashlib,xml.etree.ElementTree as ET,gzip
root=Path(__file__).resolve().parents[1];build=root/'build';candidate=build/'candidate_04';out=root/'layout';evidence=root/'verification/layout';phy=build/'physical/phy-v2'
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lvs=load(candidate/'verification/summary.json');pex=load(build/'analog/pex-phy-v2/summary.json');routed=load(build/'rtl/integrated_04/summary.json');export=load(candidate/'export.json')
assert lvs['passed'] and pex['passed'] and len(pex['results'])==30
assert routed['passed'] and routed['tests']==44
assert export['conductive_geometry_unchanged'] and export['changed_layers']==['86/20']
reportdir=build/'tools/tt/precheck/reports';xml=ET.parse(reportdir/'results.xml');checks=xml.findall('.//testcase');assert len(checks)==17 and not xml.findall('.//error') and not xml.findall('.//failure')
sta=load(root/'physical/runs/signoff_04/01-openroad-stapostpnr/state_out.json')['metrics']
for k,v in sta.items():
 if any(t in k for t in ['max_slew_violation__count','max_cap_violation__count','hold_vio__count','setup_vio__count']):assert v==0,(k,v)
corners=sorted(k.split('__corner:')[1] for k in sta if k.startswith('timing__setup_vio__count__corner:'));assert len(corners)==9
assert sta['antenna__violating__pins']==0 and sta['design__power_grid_violation__count']==0
name='tt_um_dvirdc_sky130_diff8';gds=candidate/'gds'/f'{name}.gds';assert sha(gds)==lvs['gds_sha256']==export['gds_sha256']
for path in [out,evidence,out/'analog',evidence/'precheck']:path.mkdir(parents=True,exist_ok=True)
def copy(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy(src,dst)
for d in ['gds','lef','src']:
 for p in (candidate/d).iterdir():copy(p,out/d/p.name)
copy(candidate/'info.yaml',out/'info.yaml');copy(candidate/'export.json',evidence/'export.json')
for n in ['summary.json','lvs.rpt','lvs.json',f'{name}.spice']:
 p=candidate/'verification'/n
 if p.exists():copy(p,(out/'spice'/n) if n.endswith('.spice') else evidence/('full-'+n))
for n in ['sky130_diff_phy.gds','sky130_diff_phy.lef','sky130_diff_phy.spice','verification.json']:
 copy(phy/n,out/'analog'/n)
copy(phy/'pex/phy_pex.spice',out/'analog/phy_pex.spice')
copy(phy/'reimport/lvs.rpt',evidence/'analog-lvs.rpt')
copy(build/'analog/pex-phy-v2/summary.json',evidence/'analog-pex.json')
copy(build/'rtl/integrated_04/summary.json',evidence/'routed-tests.json')
copy(build/'rtl/integrated_04/simulation.log',evidence/'routed-tests.log')
for p in reportdir.iterdir():
 if p.suffix in ['.xml','.md']:copy(p,evidence/'precheck'/p.name)
(evidence/'timing-metrics.json').write_text(json.dumps(sta,indent=2)+'\n')
run=root/'physical/runs/integrated_04'
for p in run.glob('*-openroad-checkantennas-1/reports/antenna_summary.rpt'):copy(p,evidence/'antenna.rpt')
for p in run.glob('*-openroad-rcx/*/*.spef'):
 dst=out/'spef'/(p.name+'.gz');dst.parent.mkdir(exist_ok=True);dst.write_bytes(gzip.compress(p.read_bytes(),mtime=0))
# Archive implementation and signoff constraints separately; do not hide the stricter target failures.
for p in [root/'physical/integrated.sdc',root/'physical/signoff.sdc']:copy(p,out/'constraints'/p.name)
summary={'status':'LOCAL_LAYOUT_CHECKS_PASS_NOT_SUBMISSION_READY','baseline_checkpoint':'85cf059682f8e0e3c3e95b3fe28ecce2affd72a5','target':'ttsky26e','tiles':'4x2','die_um':[682.64,225.76],'analog_pins':4,'clock_hz':1600000,'gds_sha256':sha(gds),'pdk_revision':'0536d02d875c8f67dd7cca3902ac457e62f20005','precheck_tools_revision':'7d2d2ef5261eb1df16d0bc342834d48a8a276881','precheck_pass':17,'routed_tests_pass':44,'analog_macro_rc_cases_pass':30,'full_transistor_lvs':True,'sta_corners':corners,'worst_setup_slack_ns':sta['timing__setup__ws'],'worst_hold_slack_ns':sta['timing__hold__ws'],'slew_capacitance_setup_hold_violations':0,'antenna_violations':0,'tools':{'magic_independent':'8.3.706','magic_openlane':'8.3.503','netgen':'1.5.287','openlane':'3.0.0.dev21','klayout_cli':'0.29.9','klayout_python':'0.30.14','ngspice':'46','iverilog':'12.0'},'notes':['Implementation used 1 ns / 0.10 pF margin targets; final signoff uses unchanged PDK library limits, all nine corners pass.','Resistor RPM-only ECO after routing; independent XOR proves every other layer identical; full exported GDS re-extracted and LVS matched.','Official unmodified precheck with KLayout 0.29.9 CLI; Python API 0.30.14. Official Nix now pins newer CLI for GF180-specific APIs; remote exact-version confirmation remains.','RC simulations cover the analog macro, not a full-chip transient or actual TT switch/package.','Source scope remains sky26e/; root GF180 artifacts and checkpoint branch retained.'],'remaining':['Confirm contiguous 4x2 analog allocation and accounting with Tiny Tapeout; nothing reserved.','Validate actual shuttle switch/pad/package load and mixed-signal noise/coupling; macro STA uses blackbox ports.','Prepare independent SKY candidate repository/root workflows and run exact-commit remote physical and Docs checks.','Validate controller firmware and final carrier/board pin map.','Shuttle post-fill/final integration checks and silicon characterization.']}
(evidence/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
manifest={str(p.relative_to(root)):sha(p) for folder in [out,evidence] for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='sha256.json'}
(evidence/'sha256.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(summary,indent=2))
