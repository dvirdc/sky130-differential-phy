# Verified local SKY26e layout candidate

This directory contains the SKY130 candidate, not a shuttle submission. The root of this Git repository remains the preserved GF180 project. Do not submit the repository root as SKY130.

The design uses the official 4×2 analog frame (682.64 × 225.76 µm), four analog pins, a 1.6 MHz digital clock, and a 100 kbit/s initial byte rate. The user reported 15 analog slots and 211 available tiles; this does not reserve a contiguous allocation. Tiny Tapeout's larger-analog-project accounting still applies.

- `gds/`: final GDS and routed powered Verilog, with the analog boundary declared.
- `lef/`: exact official signal-pin geometry and full-height power stripes.
- `analog/`: connected PHY GDS/LEF, extracted connectivity and distributed RC netlists.
- `spice/`: independently extracted full final-chip connectivity netlist.
- `spef/`: min/nom/max integrated routing parasitics; gzip uses a fixed timestamp.
- `constraints/`: tighter implementation targets and separate PDK-limit signoff constraints.
- `../verification/layout/`: reports, tool versions, limitations, and SHA-256 manifest.

The exact final GDS SHA-256 is `809c431cd63fc6d6051d58ce6e96feceab01ba851b958ce50a1d4d3042cf82dd`.

## Checked locally

All 17 unmodified Tiny Tapeout prechecks pass. Independent final-GDS LVS matches the transistor-level reference, including all 20 MOS devices and nine PDK resistors in the PHY. All 44 external-pin tests pass on the actual routed digital netlist. Thirty analog macro RC loopback cases pass across five MOS corners, three paired temperature/supply points, and both boost settings. Nine digital timing corners pass setup, hold, library slew and capacitance limits; antenna and disconnected-power checks pass.

The implementation run used intentionally tighter 1 ns / 0.10 pF electrical targets. Some of those margin targets remained exceeded after routing, so final STA was run separately against the original library limits. It reports zero electrical or setup/hold violations. This does not characterize the analog block in STA; that block is checked separately by SPICE.

The routed GDS received one physical correction: reducing the resistor RPM mask width to 1.27 µm to avoid guard contacts. Independent layer XOR proves all other layers unchanged. GDS paths were converted to identical polygons because the official analog-pin checker reads polygons only. The exported result was independently re-extracted, passed full transistor-level LVS, and passed all prechecks. The corrected macro RC netlist is identical to the previous extraction.

## Reproduction on this Mac

Use the pinned tools described in `../tools/README.md`. Build products are ignored; choose fresh run tags and output folders.

```sh
python3 sky26e/scripts/make_cells.py
python3 sky26e/scripts/route_phy.py
python3 sky26e/scripts/refine_phy_lef.py
python3 sky26e/scripts/verify_phy.py sky26e/build/physical/phy-v2
python3 sky26e/scripts/test_phy_pex.py sky26e/build/physical/phy-v2
python3 sky26e/tools/run_openlane.py python3 -m openlane --manual-pdk --pdk-root /pdk --pdk sky130A --scl sky130_fd_sc_hd --run-tag NEW_TAG sky26e/physical/integrated.json
python3 sky26e/scripts/test_routed.py sky26e/physical/runs/NEW_TAG
python3 sky26e/scripts/run_precheck.py --python /work/sky26e/scripts/export_candidate.py /work/sky26e/physical/runs/NEW_TAG /work/sky26e/build/NEW_CANDIDATE
python3 sky26e/scripts/verify_integrated.py sky26e/physical/runs/NEW_TAG sky26e/build/NEW_CANDIDATE
python3 sky26e/scripts/run_precheck.py sky26e/build/NEW_CANDIDATE/gds/tt_um_dvirdc_sky130_diff8.gds
```

The new integration configuration directly consumes the corrected `phy-v2` macro. The historical `integrated_04` run used the earlier implant mask; its recorded exporter received the corrected macro as its optional third argument. `package_layout.py` archives this specific verified checkpoint and deliberately requires its original local run/report paths.

## What remains

Actual shuttle switch/pad/package parasitics, mixed-signal noise under digital activity, and post-fill checks are not covered by these results. Analog RC simulation assumes 1 kΩ per external loopback leg, 20 pF receive loading, 1 MΩ differential loading, and 5 pF digital output loading. It does not simulate the whole digital chip at transistor level or a measured board.

The controller adapter and final carrier pin mapping need validation. The design supports functional testing with a USB controller and two loopback wires; no oscilloscope is needed to read counters. Connect logical TX+ `ua[0]` to RX+ `ua[2]`, and TX− `ua[1]` to RX− `ua[3]`; use the final carrier documentation to locate those signals. The host protocol is in `../host/` and `../REGISTERS.md`.

No new remote checks, reservation, purchase, submission, publication, or visibility changes were made. A separate SKY-specific repository/root configuration and exact-commit remote physical/Docs checks remain required.
