#!/usr/bin/env python3
"""Pinned-PDK schematic checks. Not extracted layout or shuttle qualification."""
from pathlib import Path
import os, json, subprocess, hashlib, bisect, concurrent.futures, sys
ROOT=Path(__file__).resolve().parents[1]
PDK=Path(os.environ.get('PDK_ROOT',str(ROOT.parents[1]/'toolchain/pdk/sky130A')))
PIN='0536d02d875c8f67dd7cca3902ac457e62f20005'
assert PIN in (PDK/'SOURCES').read_text(), 'Wrong PDK revision'
OUT=ROOT/'build/analog/matrix'; OUT.mkdir(parents=True,exist_ok=True)
seq=0xa5; bits=[]
for _ in range(12):
 bits += [0]+[(seq>>i)&1 for i in range(8)]+[1]
 seq=((seq<<1)|(((seq>>7)^(seq>>5)^(seq>>4)^(seq>>3))&1))&255
T0=20e-6; BT=10e-6; END=T0+(len(bits)+2)*BT

def pwl(vlo,vhi):
 pairs=[(0,vhi)]; prev=1
 for i,b in enumerate(bits+[1]):
  t=T0+i*BT
  if b!=prev: pairs.extend([(t,vhi if prev else vlo),(t+1e-8,vhi if b else vlo)])
  prev=b
 return 'PWL('+' '.join(f'{t:.12g} {v:.9g}' for t,v in pairs)+')'

def run(case):
 corner,temp,vdd,boost,cm,seed,rep=case
 name=f'{corner}_{temp}_{vdd}_b{boost}_cm{cm}_seed{seed}_r{rep}'
 folder=OUT/name;folder.mkdir(exist_ok=True)
 (folder/'.spiceinit').write_text('* Seed is set in the input deck, not init file (ngspice issue 873).\n')
 external=cm is not None
 wire=(f'Vrp srcp 0 {pwl(cm-.05,cm+.05)}\nVrn srcn 0 {pwl(cm+.05,cm-.05)}\nRswp srcp rp 1000\nRswn srcn rn 1000' if external else 'Rswp tp rp 1000\nRswn tn rn 1000')
 deck=f"""SKY130 schematic experiment {name}
.option scale=1e-6 seed={seed or 1}
.lib "{PDK}/libs.tech/ngspice/sky130.lib.spice" {corner}
.param mc_mm_switch={int(seed is not None)} mc_pr_switch=0
.include "{ROOT}/analog/phy.spice"
.temp {temp}
Vdd vdd 0 {vdd}
Vin din 0 {pwl(0,vdd)}
Vboost boost 0 {vdd*boost}
Xphy din boost rp rn tp tn dout vdd 0 phy
* Assumed load, NOT extracted TT pad/switch parasitics.
{wire}
Crp rp 0 20p
Crn rn 0 20p
Rload rp rn 1meg
Cout dout 0 5p
.control
set wr_singlescale
set wr_vecnames
tran 100n {END:.12g}
wrdata wave.dat v(din) v(dout) v(tp) v(tn) i(vdd)
quit
.endc
.end
"""
 (folder/'test.spice').write_text(deck)
 p=subprocess.run(['ngspice','-b','test.spice'],cwd=folder,capture_output=True,text=True,timeout=180)
 (folder/'ngspice.log').write_text(p.stdout+p.stderr)
 result=dict(runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),deck_sha256=hashlib.sha256((folder/'test.spice').read_bytes()).hexdigest(),name=name,corner=corner,temp_c=temp,vdd=vdd,boost=boost,rx_common_mode=cm,mismatch_seed=seed,passed=False)
 if p.returncode or not (folder/'wave.dat').exists():return dict(result,error='ngspice failed')
 rows=[[float(v) for v in line.split()] for line in (folder/'wave.dat').read_text().splitlines()[1:]]
 times=[r[0] for r in rows];samples=[rows[bisect.bisect_left(times,T0+(i+.7)*BT)] for i in range(len(bits))]
 bad=[i for i,(b,r) in enumerate(zip(bits,samples)) if (r[2]>vdd/2)!=bool(b) or (b and r[2]<.8*vdd) or (not b and r[2]>.2*vdd)]
 swings=[abs(r[3]-r[4]) for r in samples];cmerr=max(abs((r[3]+r[4])/2-vdd/2) for r in samples)
 elapsed=energy=0
 for a,b in zip(rows,rows[1:]):
  if a[0]>=T0:
   dt=b[0]-a[0];elapsed+=dt;energy+=dt*(-a[5]-b[5])/2
 result.update(passed=not bad and times[-1]>=END*.999 and (external or (min(swings)>.07 and max(swings)<.30 and cmerr<.1*vdd)),bad_sample_indices=bad,tx_diff_min_v=min(swings),tx_diff_max_v=max(swings),tx_cm_max_error_v=cmerr,mean_supply_current_a=energy/elapsed,wave_sha256=hashlib.sha256((folder/'wave.dat').read_bytes()).hexdigest())
 return result

cases=[(c,t,v,b,None,None,0) for c in ['tt','ff','ss','fs','sf'] for t,v in [(27,1.8),(-40,1.95),(125,1.62)] for b in [0,1]]
cases += [('tt',27,1.8,b,None,s,0) for b in [0,1] for s in range(1,6)]
cases += [('tt',27,1.8,0,None,1,1)]
cases += [(c,27,1.8,0,cm,None,0) for c in ['tt','ff','ss','fs','sf'] for cm in [.6,.9,1.2]]
reused=[]
if '--mismatch-only' in sys.argv:
 prior=json.loads((OUT/'results.json').read_text())
 prior_summary=json.loads((OUT/'summary.json').read_text())
 reused=[r for r in prior if r['mismatch_seed'] is None]
 for r in reused:
  r.setdefault('runner_sha256',prior_summary['source_sha256']['scripts/test_analog.py'])
  r.setdefault('deck_sha256',hashlib.sha256((OUT/r['name']/'test.spice').read_bytes()).hexdigest())
 cases=[c for c in cases if c[5] is not None]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 results=reused+list(pool.map(run,cases))
for r in results:print(('PASS ' if r['passed'] else 'FAIL ')+r['name'],flush=True)
seeds=[r for r in results if r['mismatch_seed'] and r['boost']==0]
seed_verified=len(set(r.get('wave_sha256') for r in seeds[:5]))==5 and seeds[0].get('wave_sha256')==seeds[-1].get('wave_sha256')
summary={'passed':all(r['passed'] for r in results) and seed_verified,'cases':len(results),'passed_cases':sum(r['passed'] for r in results),'unchanged_non_mismatch_cases_reused':len(reused),'mismatch_seed_variation_and_repeatability':seed_verified,'pdk_revision':PIN,'scope':'pre-layout schematic; MOS corner sweep, paired voltage/temperature extremes; typical resistor process; assumed switch/load; small mismatch sample only','unverified':['layout','DRC/LVS','PEX','actual TT switch/pad model','yield','noise immunity','post-fill'],'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'analog/phy.spice',Path(__file__)]}}
(OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
raise SystemExit(0 if summary['passed'] else 1)
