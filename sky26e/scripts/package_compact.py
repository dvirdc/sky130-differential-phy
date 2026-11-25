#!/usr/bin/env python3
"""Archive a fully checked 2x2 candidate without replacing the 4x2 evidence."""
from pathlib import Path
import argparse, gzip, hashlib, json, shutil, xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('run', type=Path)
parser.add_argument('candidate', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
run, candidate = args.run.resolve(), args.candidate.resolve()
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
name = 'tt_um_dvirdc_sky130_diff8'
gds = candidate / 'gds' / (name + '.gds')
lvs = load(candidate / 'verification/summary.json')
analog = load(root / 'verification/compact-analog.json')
routed_dir = root / 'build/rtl' / run.name
routed = load(routed_dir / 'summary.json')
export = load(candidate / 'export.json')
info = load(candidate / 'info.yaml')
assert info['project']['tiles'] == '2x2'
assert lvs['passed'] and lvs['gds_sha256'] == sha(gds) == export['gds_sha256']
assert export['conductive_geometry_unchanged'] and not export['changed_layers']
assert analog['passed'] and analog['pvt_cases_passed'] == 30
for rel, digest in analog['sha256'].items():
    assert sha(root / rel) == digest, rel
assert routed['passed'] and routed['tests'] == 44
for rel, digest in routed['inputs_sha256'].items():
    assert sha(Path(rel)) == digest, rel
report_dir = root / 'build/tools/tt/precheck/reports'
xml = ET.parse(report_dir / 'results.xml')
assert len(xml.findall('.//testcase')) == 17
assert not xml.findall('.//error') and not xml.findall('.//failure')
sta_paths = list(run.glob('*-openroad-stapostpnr/state_out.json'))
assert len(sta_paths) == 1
sta = load(sta_paths[0])['metrics']
for key, value in sta.items():
    if any(token in key for token in ['max_slew_violation__count', 'max_cap_violation__count', 'hold_vio__count', 'setup_vio__count']):
        assert value == 0, (key, value)
corners = sorted(key.split('__corner:')[1] for key in sta if key.startswith('timing__setup_vio__count__corner:'))
assert len(corners) == 9, corners
assert sta['antenna__violating__pins'] == 0
assert sta['design__power_grid_violation__count'] == 0
config = load(run / 'resolved.json') if (run / 'resolved.json').exists() else load(sta_paths[0].parent / 'config.json')
out, evidence = root / 'layout_compact', root / 'verification/compact-layout'
assert not out.exists() and not evidence.exists(), 'Do not overwrite an archived candidate'

def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)

for folder in ['gds', 'lef', 'src']:
    for p in (candidate / folder).iterdir():
        copy(p, out / folder / p.name)
copy(candidate / 'info.yaml', out / 'info.yaml')
copy(candidate / 'export.json', evidence / 'export.json')
for p in (candidate / 'verification').iterdir():
    if p.is_file() and p.suffix != '.ext':
        copy(p, (out / 'spice' / p.name) if p.suffix == '.spice' else evidence / ('full-' + p.name))
phy = root / 'build/physical/phy-v2'
for filename in ['sky130_diff_phy.gds', 'sky130_diff_phy.lef', 'sky130_diff_phy.spice', 'verification.json']:
    copy(phy / filename, out / 'analog' / filename)
copy(phy / 'pex/phy_pex.spice', out / 'analog/phy_pex.spice')
copy(root / 'verification/compact-analog.json', evidence / 'analog-pex.json')
copy(routed_dir / 'summary.json', evidence / 'routed-tests.json')
copy(routed_dir / 'simulation.log', evidence / 'routed-tests.log')
for p in report_dir.iterdir():
    if p.suffix in ['.xml', '.md']:
        copy(p, evidence / 'precheck' / p.name)
(evidence / 'timing-metrics.json').write_text(json.dumps(sta, indent=2) + '\n')
(evidence / 'resolved-config.json').write_text(json.dumps(config, indent=2) + '\n')
for p in run.glob('*-openroad-rcx/*/*.spef'):
    target = out / 'spef' / (p.name + '.gz')
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(gzip.compress(p.read_bytes(), mtime=0))
copy(root / 'physical/signoff_hold025.sdc', out / 'constraints/signoff.sdc')
summary = {
    'status': 'LOCAL_LAYOUT_CHECKS_PASS_NOT_SUBMISSION_READY',
    'target': 'ttsky26e', 'tiles': '2x2', 'die_um': [334.88, 225.76],
    'analog_pins': 4, 'clock_hz': 1600000, 'run': run.name,
    'gds_sha256': sha(gds),
    'pdk_revision': analog['pdk_revision'],
    'precheck_pass': 17, 'routed_tests_pass': 44, 'analog_macro_rc_cases_pass': 30,
    'full_transistor_lvs': True, 'sta_corners': corners,
    'setup_uncertainty_ns': 2, 'hold_uncertainty_ns': 0.25, 'clock_transition_ns': 2,
    'worst_setup_slack_ns': min(sta['timing__setup__ws__corner:' + c] for c in corners),
    'worst_hold_slack_ns': min(sta['timing__hold__ws__corner:' + c] for c in corners),
    'stdcell_area_um2': sta['design__instance__area__stdcell'],
    'analog_area_um2': sta['design__instance__area__macros'],
    'core_area_um2': sta['design__core__area'],
    'digital_utilization': sta['design__instance__utilization__stdcell'],
    'combined_core_occupancy': sta['design__instance__utilization'],
    'notes': [
        'Full 32-bit public counters and byte-transceiver protocol retained.',
        'Hold uncertainty uses the official SKY130 default of 0.25 ns; prior 4x2 used 0.5 ns hold uncertainty in total. Setup uncertainty remains 2 ns and clock transition remains 2 ns.',
        'Actual library electrical limits and all physical acceptance checks remain enabled.',
        'Macro RC simulations use assumed loads and do not qualify the shuttle switch/package, noise, mismatch or post-fill integration.',
        'External-pin digital regression uses functional cell models with uniform 1 ns delay, not SDF simulation.',
        'Original 4x2 layout and verification/layout evidence remain archived separately.'
    ],
    'remaining': ['Exact-commit remote artifact, precheck and Docs verification.', 'Actual shuttle/package/board load and noise validation.', 'Final carrier/controller firmware validation.', 'Shuttle post-fill/integration verification and silicon testing.']
}
(evidence / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
manifest = {str(p.relative_to(root)): sha(p) for folder in [out, evidence] for p in sorted(folder.rglob('*')) if p.is_file()}
(evidence / 'sha256.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(summary, indent=2))
