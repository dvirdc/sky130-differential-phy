#!/usr/bin/env python3
"""Conservative macro obstruction view; pin windows are verified against GDS metal."""
from pathlib import Path
import re,json,sys
root=Path(__file__).resolve().parents[1];out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root/'build/physical/phy-v2';p=out/'sky130_diff_phy.lef'
s=p.read_text();ports={}
for m in re.finditer(r'  PIN (\S+)\n(.*?)  END \1',s,re.S):
 name,body=m.groups();rects=re.findall(r'RECT ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',body)
 y1=float(rects[0][1]);y2=float(rects[0][3]);ports[name]=(2 if name in ['VDPWR','VGND'] else 232,y1,236,y2)
 def repl(rectmatch):return 'RECT '+' '.join(f'{x:.3f}' for x in ports[name])
 body=re.sub(r'RECT [\d.-]+ [\d.-]+ [\d.-]+ [\d.-]+',repl,body)
 # Collect replacements first; original match offsets need not be reused.
 old=m.group(0);s=s.replace(old,'  PIN '+name+'\n'+body+'  END '+name)
def subtract(rect,hole):
 x1,y1,x2,y2=rect;a,b,c,d=hole;a=max(a,x1);b=max(b,y1);c=min(c,x2);d=min(d,y2)
 if a>=c or b>=d:return [rect]
 return [r for r in [(x1,y1,x2,b),(x1,d,x2,y2),(x1,b,a,d),(c,b,x2,d)] if r[0]<r[2] and r[1]<r[3]]
regions=[(0,0,240,160)]
for a,b,c,d in ports.values():regions=[piece for r in regions for piece in subtract(r,(a-.4,b-.4,c+.4,d+.4))]
obs='  OBS\n'
for layer,rects in [('met1',[(0,0,240,160)]),('met2',[(0,0,240,160)]),('met3',regions),('met4',[(1.6,14.6,32.8,142.8)])]:
 obs+='    LAYER '+layer+' ;\n'+''.join('      RECT '+' '.join(f'{z:.3f}' for z in r)+' ;\n' for r in rects)
obs+='  END\n'
s=re.sub(r'  OBS\n.*?  END\n',obs,s,flags=re.S);p.write_text(s)
(out/'lef-pin-windows.json').write_text(json.dumps(ports,indent=2)+'\n')
