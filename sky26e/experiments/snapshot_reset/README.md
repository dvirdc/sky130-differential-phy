# Optional snapshot-reset area experiment

This is an isolated experiment, not the production RTL or a qualified layout. It was superseded while routing by a more promising production trial using the official default hold uncertainty. No hardware was submitted and no remote candidate was changed by this experiment.

The baseline is the optimized full 32-bit public register/counter design. The trial replaces asynchronous reset on the 192-bit snapshot payload bank with one resettable `snapshot_valid` flag. Snapshot addresses 16–43 return zero until the first snapshot after reset. Snapshot acquisition remains unconditional on BIST/transceiver activity, and start/clear/send/configuration commands retain previous snapshots as before. The snapshot bank uses ordinary enabled flops.

Native mapped area decreased from 32,389.8144 to 31,058.5376µm² (4.11%). The unchanged 44 RTL and 44 mapped tests pass. A supplementary copy of the testbench adds 1,204 explicit SPI byte reads verifying zero snapshot data after resets; its 44 original cases also pass. Original testbench and production RTL were not edited by this experiment.

Physical results were less decisive:

- Density 75%, halo 4µm: postCTS detailed placement could not place 14 reported instance entries after insertion of 1,211 hold buffers.
- Density 70%, halo 4µm: postCTS placement passed; GRT at 0.1 adjustment stopped with 43 total overflow.
- Resume at GRT adjustment 0: global routing passed and detailed routing began. It was stopped as **superseded/interrupted**, not a completed pass/failure. All timing and DRC acceptance limits remained enabled.

The snapshot variant's physical area advantage after repair was only about 412µm² (47,977.3µm² standard cells versus 48,388.9µm² for the concurrent production trial), due to additional timing-repair buffers. Do not infer routed feasibility from synthesis area alone.

Run the portable isolated regressions from the repository root:

```sh
python3 sky26e/experiments/snapshot_reset/verify.py
```

The script requires native Yosys, Icarus and the pinned PDK; outputs go to `sky26e/build/snapshot_reset_reproduced/`. `summary.json` and logs record the original measured outcomes. Three copied configs use the archived trial RTL explicitly; they reference the compact macro and shared SKY130 physical inputs without replacing production RTL.

To reproduce a fresh physical trial with the staged OpenLane toolchain:

```sh
python3 sky26e/tools/run_openlane.py python3 -m openlane --manual-pdk --pdk-root /pdk --pdk sky130A --scl sky130_fd_sc_hd -j4 --run-tag NEW_TAG sky26e/experiments/snapshot_reset/compact_snapshot_density70.json
```

The `compact_snapshot_03.json` configuration uses GRT adjustment 0. The original attempt resumed from saved postCTS state, as recorded in `summary.json`; a fresh run is also possible with that config. Keep all acceptance checks enabled.
