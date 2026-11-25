#!/usr/bin/env python3
"""Prove full-width arithmetic and guarded-transition identities with Yosys SAT."""
from pathlib import Path
import hashlib,json,re,subprocess
root=Path(__file__).resolve().parents[1]
out=root/'build/area';out.mkdir(parents=True,exist_ok=True)
source=root/'sim/counter_reduction_properties.sv'
script=f'read_verilog -formal -sv {source}\nprep -top counter_reduction_properties\nflatten\nchformal -lower\nsat -verify -prove-asserts -set-assumes -show-inputs\n'
(out/'counter-proofs.ys').write_text(script)
p=subprocess.run(['yosys','-Q','-s',str(out/'counter-proofs.ys')],capture_output=True,text=True,timeout=120)
(out/'counter-proofs.log').write_text(p.stdout+p.stderr)
passed=p.returncode==0 and 'SAT proof finished - no model found: SUCCESS!' in p.stdout
result={'passed':passed,'scope':'Universal 32-bit combinational identities and guarded target-state induction step; not full-core formal equivalence','properties':['Saturating checked_bits equals min(8*checked_bytes,2^32-1) before and after increment/clear/reset','Coherent snapshot bits derive from snapshot bytes including saturation','target_active==target_count while running or potentially PASS is preserved by guarded control transitions','PASS predicate unchanged under the target invariant','Before a legal launch sent<target<=2^32-1, so the transmitted pattern index can use modulo8 state'], 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rtl_sha256':hashlib.sha256((root/'rtl/diff8_digital.v').read_bytes()).hexdigest()}
(out/'counter-proofs.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if passed else 1)
