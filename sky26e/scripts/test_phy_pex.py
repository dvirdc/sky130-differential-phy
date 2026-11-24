#!/usr/bin/env python3
"""Post-layout RC checks of the exact analog macro; external pad/load remains assumed."""
from pathlib import Path
import subprocess,json,hashlib,bisect,concurrent.futures,re,sys
ROOT=Path(__file__).resolve().parents[1];PHY=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'build/physical/phy-v2';PEX=PHY/'pex/phy_pex.spice';OUT=ROOT/'build/analog'/('pex-'+PHY.name);OUT.mkdir(parents=True,exist_ok=True)
seq=0xa5;bits=[]
for _ in range(12):
 bits += [0]+[(seq>>i)&1 for i in range(8)]+[1]
 seq=((seq<<1)|(((seq>>7)^(seq>>5)^(seq>>4)^(seq>>3))&1))&255
cases=[(c,t,v,b) for c in ['tt','ff','ss','fs','sf'] for t,v in [(27,1.8),(-40,1.95),(125,1.62)] for b in [0,1]]
def run(case):
 c,t,v,b=case;name=f'{c}_{t}_{v}_b{b}';folder=OUT/name;folder.mkdir(exist_ok=True)
 src=ROOT/f'build/analog/matrix/{c}_{t}_{v}_b{b}_cmNone_seedNone_r0/test.spice';deck=src.read_text()
 deck=re.sub(r'\.include "[^"\n]+/analog/phy.spice"',f'.include "{PEX}"',deck)
 deck=deck.replace('Xphy din boost rp rn tp tn dout vdd 0 phy','Xphy din boost rp rn tp tn dout vdd 0 phy_pex')
 (folder/'test.spice').write_text(deck)
 p=subprocess.run(['ngspice','-b','test.spice'],cwd=folder,capture_output=True,text=True,timeout=240)
 (folder/'ngspice.log').write_text(p.stdout+p.stderr)
 if p.returncode or not (folder/'wave.dat').exists():return {'name':name,'passed':False,'error':'ngspice failed'}
 rows=[[float(x) for x in s.split()] for s in (folder/'wave.dat').read_text().splitlines()[1:]];times=[r[0] for r in rows]
 samples=[rows[bisect.bisect_left(times,20e-6+(i+.7)*10e-6)] for i in range(120)]
 bad=[i for i,(bit,r) in enumerate(zip(bits,samples)) if (r[2]>v/2)!=bool(bit) or (bit and r[2]<.8*v) or (not bit and r[2]>.2*v)]
 swings=[abs(r[3]-r[4]) for r in samples]
 return {'name':name,'passed':not bad and min(swings)>.07 and max(swings)<.30,'bad_bit_samples':bad,'tx_diff_min_v':min(swings),'tx_diff_max_v':max(swings),'deck_sha256':hashlib.sha256((folder/'test.spice').read_bytes()).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,cases))
text=PEX.read_text();summary={'passed':all(r['passed'] for r in results),'scope':'exact analog macro GDS RC extraction; 30 PVT loopback cases; assumed external switch/load; not full integrated top/post-fill','resistors':sum(s.startswith('R') for s in text.splitlines()),'capacitors':sum(s.startswith('C') for s in text.splitlines()),'active_and_pdk_resistor_devices':sum(s.startswith('X') for s in text.splitlines()),'pex_sha256':hashlib.sha256(PEX.read_bytes()).hexdigest(),'gds_sha256':hashlib.sha256((PHY/'sky130_diff_phy.gds').read_bytes()).hexdigest(),'results':results}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));raise SystemExit(0 if summary['passed'] else 1)
