# SKY26e differential byte transceiver

Private SKY130 candidate for Tiny Tapeout SKY26e: an 8-bit transceiver with a differential PHY, built-in pattern generator, independent receiver and loopback error counters. The design uses a 2x2 analog frame (four tiles), four analog pins and a 1.6 MHz clock, initially targeting 100 kbit/s.

## Candidate and evidence

The root `info.yaml`, `gds/`, `lef/` and `src/` contain the verified SKY130 candidate. No GF180 implementation or GF180 workflow is included. `src/project.v` is the analog macro interface; complete digital RTL, analog SPICE, layout generators, host protocol and tests are under `sky26e/`.

This repository starts from local checkpoint `5d3f92859005d81356f3cb697f7acd5fb4d9bc6f`. The complete `sky26e/` directory is retained byte-for-byte as the source/evidence snapshot. Its historical references to a preserved GF180 repository root describe the original development checkout, not this standalone repository.

- [Verification status](sky26e/verification/STATUS.md): 17/17 local prechecks, full transistor-level LVS, 44 routed digital tests, 30 extracted analog loopback cases and nine timing corners passed.
- [Exact artifact hashes and tool versions](sky26e/verification/compact-layout/summary.json)
- [Register interface](sky26e/REGISTERS.md)
- [Host protocol and test setup](sky26e/host/README.md)
- [Project documentation](docs/info.md)

Digital utilization is **67.35%**, with **73.12% combined core occupancy** including the 140×90 µm analog macro. All 32-bit public counters and full byte TX/RX and loopback features remain. The original verified 4×2 version is preserved in Git history and `sky26e/layout/`. The compact design uses the official 0.25 ns hold uncertainty; setup uncertainty and clock transition remain 2 ns.

The GDS SHA-256 is `3e3c5d49441ae6847526168564dae89b2dee7286302094004a529dab48d5b24d`. Root candidate files are exact copies of `sky26e/layout_compact/` artifacts. `PROVENANCE.json` records the source checkpoint and root file hashes.

## Scope-free functional test

Connect logical TX+ `ua[0]` to RX+ `ua[2]`, and TX- `ua[1]` to RX- `ua[3]`. A compatible USB controller can start the generator and read checked-byte and error counters over SPI. No oscilloscope is needed for functional pass/fail readout. Final carrier pin mapping and controller firmware still need validation.

This is not submission approval or silicon qualification. Contiguous analog allocation, actual shuttle switch/package behavior, board validation, exact-commit remote physical/Docs checks and final post-fill integration remain. No slots have been reserved and no design has been submitted.

## GitHub Actions artifacts

The official [SKY analog template](https://github.com/TinyTapeout/ttsky-analog-template) workflows are adapted to SKY26e with immutable action/tool revisions and read-only repository permissions. Every push to `main`, or a manual dispatch, runs:

- **gds**: packages the existing verified analog layout into `tt_submission` (GDS, OAS, LEF and powered Verilog), renders `gds_render` (PNG), and runs the official SKY130 precheck with `precheck_reports`.
- **docs**: validates metadata/documentation and generates the `PDF` datasheet artifact.

Download artifacts from the completed [Actions runs](https://github.com/dvirdc/sky130-differential-phy/actions). No GitHub Pages deployment is configured. This analog flow packages the committed custom layout; it does not re-synthesize or re-route the PHY.
