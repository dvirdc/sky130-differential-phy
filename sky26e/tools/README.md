# Isolated toolchain

The PDK must be sky130A at open_pdks 0536d02d875c8f67dd7cca3902ac457e62f20005. It is installed in ../toolchain/pdk relative to the checkout using Ciel 3.2.0. Do not substitute the older native Mac PDK.

Build `docker build -t sky26e-eda:local sky26e/tools`. The Dockerfile compiles official Magic 8.3.706 at commit 1d42dfcdf6cd91df7a59198477324c2ca78ba439. Set PDK_ROOT=/pdk when mounting the pinned PDK at /pdk. The bundled Debian Netgen version is not being presented as a completed LVS signoff flow.

Native ngspice 46, Icarus Verilog 12.0, Verilator 5.028 and Yosys 0.53+39 ran the recorded schematic/RTL/mapping checks. The mapped gate regression uses the pinned HD TT 1.8 V liberty and standard-cell functional models with a uniform 1 ns UNIT_DELAY; it is not SDF timing verification.

The native OpenLane install could not load its x86_64 libparse module on the ARM Mac. The official ARM64 OpenLane 3.0.0.dev21 image is identified by manifest sha256:77c4c5a02b802ec7c5a584622d3ee34c686b003419910ef60ef97499f3f9ee2f. Docker image extraction failed because Docker's data disk is full. `fetch_openlane.py` downloads and hash-verifies the official manifest, config and layers onto the Mac's host disk. The verified first layer is extracted under ../toolchain/openlane/rootfs; its /nix tree contains the tools. The second layer's sudo overlay is not needed for these unprivileged tool executions; overwriting its read-only files was not used as a success criterion. No existing Docker images, volumes, user data or account permissions were removed or changed.

`run_openlane.py` mounts that /nix tree read-only into sky26e-eda:local, uses the official tool PATH and NIX_PYTHONPATH, mounts the worktree writable and PDK read-only, and puts temporary files in tmpfs. Version startup and a real global-placement run succeeded. It is a host-backed tool execution environment, not a claim of a fully recreated official container filesystem.

Run the bounded placement trial:

```
python3 sky26e/tools/run_openlane.py python3 -m openlane --manual-pdk --pdk-root /pdk --pdk sky130A --scl sky130_fd_sc_hd --run-tag NEW_UNIQUE_TAG --to OpenROAD.GlobalPlacement sky26e/physical/core_trial_large.json
```

Always use --manual-pdk here, preventing OpenLane from selecting/installing a different PDK. This trial is only the digital sub-block; generic fallback timing constraints, a non-shuttle pin arrangement and incomplete physical flow prevent signoff claims. The full mixed-signal design must use the exact official analog frame, no met5, proper power rails, verified analog integration and final DRC/LVS/PEX/prechecks.

## Integrated layout checks

The new mixed-signal flow is `physical/integrated.json`; see `layout/README.md` for the commands and limitations. The runner now completed actual routing, RC extraction, independent GDS checks and netgen LVS using Netgen 1.5.287 from the host-backed official image. Do not use the older Debian Netgen for the recorded result.

Tiny Tapeout support tools are staged in `build/tools/tt` at `7d2d2ef5261eb1df16d0bc342834d48a8a276881`. `run_precheck.py` uses isolated Python 3.11 packages in `build/precheck-deps` (from that checkout's requirements), Qhull runtime libraries in `build/qhull-root`, and the Nix KLayout CLI. The CLI is 0.29.9; the Python KLayout API is 0.30.14. All 17 SKY130 checks ran and passed; this is not a claim that the environment matches the newer remote CLI exactly. The current TT Nix note explains that the newer CLI is needed for GF180-specific APIs. Exact remote-version checks remain a separate gate.

This Mac's staged Python dependency installation required host-backed compilation of gdstk 0.9.52 against Qhull because the Docker data disk is full. `build/precheck-deps/bin/yowasp-yosys` invokes the installed `yowasp_yosys._run_yosys_argv` console entrypoint. Recreating this environment on another machine requires installing the pinned precheck requirements and CLI tools; no claim is made that the ignored staging directories are embedded in Git.
