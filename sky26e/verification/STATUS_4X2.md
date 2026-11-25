# SKY26e local layout checkpoint — 2026-11-24

Local layout checks pass. This is not submission approval or silicon qualification. The isolated SKY130 candidate is in [../layout](../layout/README.md); repository-root GF180 results remain separate.

## Current evidence

| Check | Result |
|---|---|
| Official 4×2 analog template | 682.64 × 225.76 µm, four used analog pins |
| Unmodified TT precheck | 17/17 pass |
| Independent exact-GDS transistor LVS | Unique match; PHY explicitly includes 20 MOS and 9 resistors |
| Actual routed digital netlist | 44/44 external-pin tests pass |
| Extracted analog macro RC simulation | 30/30 loopback cases pass |
| Digital STA | Nine corners pass setup/hold and library slew/capacitance limits |
| Worst setup / hold slack | +505.603 ns / +0.126 ns at a 625 ns clock period |
| Antenna / disconnected power | Zero violations |

The GDS hash, source/artifact hashes, individual reports, tool versions, and scope limits are in [layout/summary.json](layout/summary.json) and [layout/sha256.json](layout/sha256.json). GDS SHA-256: `809c431cd63fc6d6051d58ce6e96feceab01ba851b958ce50a1d4d3042cf82dd`.

The 30 extracted cases cover five MOS corners × three paired temperature/supply points × both boost settings. The pairings are 27 °C/1.8 V, −40 °C/1.95 V, and 125 °C/1.62 V; this is not a Cartesian temperature/voltage sweep. Each case checks 120 bit-center decisions from twelve 8N1 bytes. The macro extraction has 750 resistance and 276 capacitance elements. TX differential magnitude across these cases ranges approximately 88–242 mV, including both boost states. These are model results, not silicon guarantees.

Routed digital tests use functional standard-cell models with uniform 1 ns delays and a behavioral analog boundary. They exercise normal byte transmission, self-test patterns, PRBS, corrupted data/framing, disconnect/stuck/invalid inputs, asynchronous source baud offsets, reset/deselection, overrun, SPI faults, and stale-PASS invalidation. They are not SDF or whole-chip analog simulations. Analog timing is absent from STA and checked separately in SPICE.

## Earlier preserved evidence

Checkpoint `85cf059` on `sky26e-port` preserves 44 RTL tests, 44 mapped-gate tests, 56 schematic cases and placement experiments. The schematic matrix includes 30 loopback cases, 15 receiver common-mode cases, ten mismatch samples and one repeated seed. The mismatch seed repeatability repair and per-case provenance remain recorded in `analog*.json`. The expanded 30-case RC sweep does not repeat the receiver common-mode or mismatch matrix; five schematic seeds are not yield qualification.

The current branch adds connected macro layout, full integration, routed checks and evidence. The historical GF180 root and original GF180 checkout remain unchanged.

## Physical-check details

A resistor RPM mask overlap was corrected without changing resistor W/L, contacts, or conductive geometry. The exported GDS differs from the routed design only on layer 86/20. Full exact-GDS LVS and all prechecks were run after this correction. GDS PATH conversion to polygons is independently checked by geometric XOR. Exported LEF pin rectangles are checked against both real GDS metal and pin layers.

Implementation used tighter 1 ns / 0.10 pF margin targets. Final signoff uses the original PDK-library limits; all nine corners pass. The stricter-target implementation run's deferred errors are retained in its logs and are not claimed as a successful one-command flow. Future runs use the corrected macro and separate implementation/signoff constraints directly.

The pinned PDK is `0536d02d875c8f67dd7cca3902ac457e62f20005`; TT tools are `7d2d2ef5261eb1df16d0bc342834d48a8a276881`. Independent Magic is 8.3.706 and Netgen is 1.5.287. The unmodified precheck passed with KLayout CLI 0.29.9 and Python API 0.30.14. Current TT Nix pins a newer CLI for GF180-specific deck APIs; no remote exact-version result is claimed for this SKY candidate.

## Remaining gates

1. Confirm contiguous 4×2 analog allocation and larger-project accounting. User-reported availability is 15 analog slots and 211 tiles; nothing is reserved.
2. Validate actual TT switch/pad/package behavior, digital-activity coupling/noise, and final post-fill integration. RC tests currently assume external loads and cover the analog macro, not the whole-chip transient response.
3. Prepare a separate SKY-specific repository/root metadata/workflow configuration and run remote physical and Docs checks at its exact commit.
4. Validate the controller adapter and final carrier/board pin map, then characterize silicon. `host/diff8.py` is a protocol driver, not a validated complete board firmware package.

No reservation, purchase, submission, publication, GitHub Pages action, or repository visibility change was performed.
