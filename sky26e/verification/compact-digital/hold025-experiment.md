# Isolated 2x2 0.25 ns hold-uncertainty experiment

This experiment changes only the explicitly selected clock hold uncertainty from
0.5 ns to 0.25 ns relative to `compact_library.json` / `signoff.sdc`.
It retains 625 ns clock period (1.6 MHz), 2 ns setup uncertainty, 2 ns clock
transition, all false-path exclusions, output delays, loads, library electrical
limits, repair margins, corners, and verification checks. It is a different
reported timing envelope, not evidence of closure under the prior 0.5 ns hold
assumption. The official default alone does not establish the actual external
clock jitter or slew.

The configuration is `sky26e/physical/compact_hold025.json`, and both PNR and
signoff use `sky26e/physical/signoff_hold025.sdc`. It uses production RTL with
full 32-bit public counters, the 334.88 x 225.76 um 2x2 frame (75,602.5088 um2), PHY at (185, 90),
4 um macro halos, 75% target placement density and zero global-route reserve.
The production digital RTL SHA-256 at launch is `3c68ad1452199b820d4a9e9732ead0e4162d7204bb80581a686308aff3042d96`.
No snapshot RTL or changes to running configurations are involved.

## Primary sources

- [Official SKY26e GDS action](https://github.com/TinyTapeout/tt-gds-action/blob/ttsky26e/action.yml#L50-L58)
  selects LibreLane 3.0.14 for SKY130.
- [Pinned LibreLane 3.0.14 SKY130 defaults](https://github.com/librelane/librelane/blob/f24e0ea5db2260719e9a0c7d51d07db74a87fa23/librelane/config/pdk_compat.py#L323-L334)
  use 0.25 ns clock uncertainty and 0.15 ns clock transition. The experiment
  adopts only the hold uncertainty; setup and transition remain more conservative.
- [Pinned base SDC](https://github.com/librelane/librelane/blob/f24e0ea5db2260719e9a0c7d51d07db74a87fa23/librelane/scripts/base.sdc#L65-L73)
  applies the default uncertainty to setup and hold.
- [Official SKY digital template](https://github.com/TinyTapeout/ttsky-verilog-template/blob/main/src/config.json)
  has no uncertainty or transition override. Its 0.1 ns placement and 0.05 ns
  routing hold-repair margins are separate from clock uncertainty.

## Execution and status

Run tag: `compact_hold025`. Fresh Classic full flow, four jobs, with the same
production RTL and analog macro files. Command:

```sh
python3 sky26e/tools/run_openlane.py python3 -m openlane --manual-pdk \
  --pdk sky130A -j 4 --run-tag compact_hold025 --hide-progress-bar \
  sky26e/physical/compact_hold025.json
```

Status: **local physical flow PASS**, exit code 0. OpenLane reported `Flow complete`.
The mandatory route, antenna, Magic DRC, KLayout DRC, LVS and nine-corner
setup/hold/slew/capacitance checkers passed. Exported-candidate checks and
remote verification are separate steps, outside this bounded flow audit.

## Intermediate area comparison

These are standard-cell-only metrics from physical checkpoints, excluding the
12,600 um2 PHY macro. Digital utilization divides standard-cell area by
71,348.4 - 12,600 um2; it is not percentage of the whole die.

| Checkpoint | Prior 0.5 ns hold | Experimental 0.25 ns hold | Reduction |
|---|---:|---:|---:|
| Post-CTS stdcell area | 48,231.3 um2 | 39,475.4 um2 | 18.15% |
| Post-GRT stdcell area | 48,388.9 um2 | 39,545.4 um2 | 18.28% |
| Post-GRT stdcell count | 5,007 | 4,089 | 918 cells |
| Post-GRT timing-repair buffers | 1,152 | 275 | 877 buffers |
| Post-GRT timing-repair-buffer area | 11,638.7 um2 | 2,841.48 um2 | 8,797.22 um2 |
| Post-GRT digital utilization | 82.3663% | 67.3132% | 15.0531 percentage points |

Baseline checkpoints: `compact_library/37-openroad-resizertimingpostcts` and
`compact_library_02/06-openroad-resizertimingpostgrt`. Experimental checkpoints:
`compact_hold025/37-openroad-resizertimingpostcts` and
`compact_hold025/44-openroad-resizertimingpostgrt`. Values use
`design__instance__area__stdcell` and cumulative `class:timing_repair_buffer`
metrics; step-local `count__hold_buffer` has a different meaning.

Post-GRT powered-netlist audit confirms the only four uses of `ua[0:3]` are
`.txp(ua[0])`, `.txn(ua[1])`, `.rxp(ua[2])`, `.rxn(ua[3])`, with no inserted
buffer or additional digital load on these analog paths.

Intermediate TT STA is not a substitute for final nine-corner extracted STA.
Per-corner entries in intermediate cumulative `state_out.json` can be stale;
final signoff must be read from the freshly executed corner reports.


## Final physical-flow evidence

Final standard-cell area is **39,567.9 um2**, with **4,098 standard cells**.
Digital utilization is **67.3515%** of core area excluding the PHY macro;
combined standard-cell plus macro occupancy is **73.1172%** of core area.
The PHY remains 12,600 um2 and the exact die area is 75,602.5088 um2.
There are 275 timing-repair buffers, occupying 2,841.48 um2.

Routing DRC, Magic DRC, KLayout DRC, streamout XOR differences, OpenLane LVS
errors, antenna violations, power-grid violations and critical disconnected
pins are all zero. The 17 noncritical disconnected pins are the intentionally
unused top-level ports `ua[4:7]`, `ui_in[3:7]` and `uio_in[0:7]`.
The filled powered-netlist analog-pin audit again confirms direct PHY-to-pad
connections without inserted digital cells or extra loads.

The table below uses fresh extracted-STA corner reports, cross-checked against
each corner's `ws.min.rpt` and `ws.max.rpt`. All nine corners have zero setup,
hold, slew and capacitance violations. The analog macro is black-boxed for
this digital STA; its analog characterization remains separate.

| Corner | Setup slack (ns) | Hold slack (ns) |
|---|---:|---:|
| max_ff_n40C_1v95 | 518.053142 | 0.116014 |
| max_ss_100C_1v60 | 504.475068 | 0.880987 |
| max_tt_025C_1v80 | 514.727859 | 0.310642 |
| min_ff_n40C_1v95 | 518.212417 | 0.109336 |
| min_ss_100C_1v60 | 504.877633 | 0.865480 |
| min_tt_025C_1v80 | 514.962452 | 0.301967 |
| nom_ff_n40C_1v95 | 518.137441 | 0.112302 |
| nom_ss_100C_1v60 | 504.683001 | 0.872717 |
| nom_tt_025C_1v80 | 514.851209 | 0.305914 |

Worst setup slack is +504.475068 ns; worst hold slack is +0.109336 ns under
this experiment's stated 0.25 ns hold uncertainty.

`hold025-result.json` preserves the bounded audit, per-corner results and
source GDS/LEF/netlist hashes. `hold025-final-metrics.json` is an exact copy
of the completed flow's `final/metrics.json`, including the physical check
counts. The independent exported candidate may have a different GDS hash
because export changes metadata/pin labels; its geometry-XOR and separate
verification belong to that candidate's evidence.

The prior production and snapshot detailed-route experiments were intentionally
interrupted as superseded, rather than classified as terminal failed flows.
No remote push, submission or account changes were performed by this experiment.
