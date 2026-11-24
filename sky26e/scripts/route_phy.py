#!/usr/bin/env python3
"""Connected SKY130 PHY prototype; deterministic channel routes, then real DRC/extraction."""
from pathlib import Path
import json,re,shutil,subprocess,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'build/physical/cells';OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'build/physical/phy-v2';OUT.mkdir(parents=True,exist_ok=True)
TOP='sky130_diff_phy';DEV=[]
def mos(inst,model,w,l,d,g,s,b):DEV.append((inst,f'{model}_w{w}_l{l}'.replace('.','p'),dict(D=d,G=g,S=s,B=b)))
for inv,a,y in [('xi0','din','dinb'),('xi1','dinb','dp'),('xib','boost','boostb'),('xis','pre','q'),('xbuf','q','qb'),('xout','qb','dout')]:
 mos(inv+'_xn','nfet_01v8',2,.15,y,a,'VGND','VGND');mos(inv+'_xp','pfet_01v8',4,.15,y,a,'VDPWR','VDPWR')
for tg,a,b in [('xtp','dp','ap'),('xtn','dinb','an')]:
 mos(tg+'_xn','nfet_01v8',4,.15,a,'boost',b,'VGND');mos(tg+'_xp','pfet_01v8',8,.15,a,'boostb',b,'VDPWR')
mos('xn1','nfet_01v8',24,1,'n1','rxn','tail','VGND');mos('xn2','nfet_01v8',24,1,'pre','rxp','tail','VGND')
mos('xp1','pfet_01v8',12,1,'n1','n1','VDPWR','VDPWR');mos('xp2','pfet_01v8',12,1,'pre','n1','VDPWR','VDPWR')
for inst,l,a,b in [('xrp',28,'dp','txp'),('xrn',28,'dinb','txn'),('xrbp',1,'txp','cm'),('xrbn',1,'txn','cm'),('xrc1',20,'VDPWR','cm'),('xrc2',20,'cm','VGND'),('xrp2',28,'ap','txp'),('xrn2',28,'an','txn'),('xrt',20,'tail','VGND')]:DEV.append((inst,f'res_high_po_0p35_w0p35_l{l}',dict(R1=a,R2=b,B='VGND')))
NETS=sorted({v for _,_,pins in DEV for v in pins.values()}-{'VDPWR','VGND'})+['VDPWR','VGND']
LOW={n:15+1.6*i for i,n in enumerate(NETS)};HIGH={n:112+1.6*i for i,n in enumerate(NETS)}
records={};instances=[];access=[]
def rect(layer,x1,y1,x2,y2):
 r=tuple(round(z*200) for z in (min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2)))
 assert r[0]<r[2] and r[1]<r[3],r
 records.setdefault(layer,[]).append(r)
def wire(layer,x1,y1,x2,y2,w):
 assert x1==x2 or y1==y2
 rect(layer,min(x1,x2)-w/2,min(y1,y2)-w/2,max(x1,x2)+w/2,max(y1,y2)+w/2)
def via(n,x,y):
 if n==1:
  rect('via1',x-.13,y-.13,x+.13,y+.13)
  for layer in ['metal1','metal2']:rect(layer,x-.13,y-.16,x+.13,y+.16)
 elif n==2:
  rect('via2',x-.14,y-.14,x+.14,y+.14);rect('metal2',x-.15,y-.2,x+.15,y+.2);rect('metal3',x-.2,y-.2,x+.2,y+.2)
 else:
  rect('via3',x-.16,y-.16,x+.16,y+.16)
  for layer in ['metal3','metal4']:rect(layer,x-.2,y-.2,x+.2,y+.2)
def cell(name):
 s=(SRC/(name+'.mag')).read_text()
 geom={};labels={};layer=''
 for line in s.splitlines():
  if line.startswith('<< '):layer=line[3:-3]
  elif line.startswith('rect ') and layer!='checkpaint':geom.setdefault(layer,[]).append(tuple(int(z)/200 for z in line.split()[1:]))
  elif line.startswith('rlabel '):
   a=line.split();labels[a[-1]]=((int(a[2])+int(a[4]))/400,(int(a[3])+int(a[5]))/400)
 bbox=(min(r[0] for rr in geom.values() for r in rr),min(r[1] for rr in geom.values() for r in rr),max(r[2] for rr in geom.values() for r in rr),max(r[3] for rr in geom.values() for r in rr))
 if name.startswith('res_high'):
  poly=geom['xpolycontact']+geom['ppolyres']
  y1=round((min(a[1] for a in poly)-.3)*200);y2=round((max(a[3] for a in poly)+.3)*200)
  # Widen RPM over field only; preserve resistor poly W/L and contact geometry.
  s=s.replace('<< properties >>','<< properties >>\nstring MASKHINTS_RPM -127 '+str(y1)+' 127 '+str(y2))
 (OUT/(name+'.mag')).write_text(s)
 return geom,labels,bbox
for i,(inst,name,pins) in enumerate(DEV):
 cx,cy=12+7.6*i,78
 geom,labels,bbox=cell(name);instances.append((inst,name,cx,cy,bbox))
 guards=[r for layer,rs in geom.items() if layer in ('psubdiffcont','nsubdiffcont') for r in rs if r[0]>0 and r[3]-r[1]>.5]
 g=max(guards,key=lambda r:r[3]-r[1]);body=((g[0]+g[2])/2,0)
 for pin,net in pins.items():
  x,y=body if pin=='B' else labels[pin]
  if pin=='B':
   for layer in ['locali','metal1']:rect(layer,cx+x-.17,cy+y-.17,cx+x+.17,cy+y+.17)
   rect('viali',cx+x-.085,cy+y-.085,cx+x+.085,cy+y+.085)
  if pin=='G':y+=.1
  if pin in ['R1','R2']:
   target=-.6 if pin=='R1' else .6
   # The PDK resistor already has MCON/M1 at its labelled terminals.
   wire('metal1',cx+x,cy+y,cx+target,cy+y,.34);x=target
  x+=cx;y+=cy;via(1,x,y)
  ty=HIGH[net] if pin in ['G','B'] else LOW[net]
  wire('metal2',x,y,x,ty,.14);via(2,x,ty)
  access.append(dict(instance=inst,pin=pin,net=net,x=x,y=y,track_y=ty))
for i,net in enumerate(NETS):
 x=2+1.6*i
 for y in [LOW[net],HIGH[net]]:wire('metal3',2,y,236,y,.4);via(3,x,y)
 wire('metal4',x,LOW[net],x,HIGH[net],.4)
ports=['din','boost','rxp','rxn','txp','txn','dout','VDPWR','VGND']
labels='<< labels >>\n'
for i,net in enumerate(ports):
 y=HIGH[net];x=235
 labels+=f'rlabel metal3 {round((x-.5)*200)} {round((y-.2)*200)} {round((x+.5)*200)} {round((y+.2)*200)} 0 {net}\nport {i+1} nsew '+('power bidirectional' if net=='VDPWR' else 'ground bidirectional' if net=='VGND' else 'signal output' if net in ['txp','txn','dout'] else 'signal input')+'\n'
text='magic\ntech sky130A\nmagscale 1 2\ntimestamp 0\n'
for layer,rs in records.items():text+='<< '+layer+' >>\n'+''.join('rect '+' '.join(map(str,r))+'\n' for r in rs)
for inst,name,x,y,bbox in instances:text+=f'use {name} {inst}\ntimestamp 0\ntransform 1 0 {round(x*200)} 0 1 {round(y*200)}\nbox '+' '.join(str(round(z*200)) for z in bbox)+'\n'
text+=labels+'<< properties >>\nstring FIXED_BBOX 0 0 48000 32000\n<< end >>\n'
(OUT/(TOP+'.mag')).write_text(text)
(OUT/'routing.json').write_text(json.dumps({'nets':NETS,'access':access,'ports':ports,'bbox_um':[0,0,240,160]},indent=2)+'\n')
cmd=f"""load {TOP} -silent
select top cell
drc check
drc catchup
puts "DRC_TOTAL=[drc list count total]"
puts "DRC_WHY=[drc listall why]"
extract all
ext2spice lvs
ext2spice
save {TOP}.mag
gds write {TOP}.gds
lef write {TOP}.lef -hide
quit -noprompt
"""
(OUT/'check.tcl').write_text(cmd)
p=subprocess.run(['docker','run','--rm','--tmpfs','/tmp:rw,size=512m','-e','PDK_ROOT=/pdk','-v',str(ROOT.parents[1]/'toolchain/pdk')+':/pdk:ro','-v',str(OUT)+':/work','sky26e-eda:local','magic','-dnull','-noconsole','-rcfile','/pdk/sky130A/libs.tech/magic/sky130A.magicrc','check.tcl'],capture_output=True,text=True,timeout=120)
log=p.stdout+p.stderr;(OUT/'magic.log').write_text(log)
print(log[-6000:]);raise SystemExit(0 if p.returncode==0 and 'DRC_TOTAL=0\n' in log else 1)
