# SKY26e 2×2 local layout checkpoint — 2026-11-25

The compact candidate passes the complete physical flow and independent exported-GDS checks. It occupies four tiles and retains the full 32-bit register/counter interface, byte transceiver and loopback self-test. This is a checked layout candidate; shuttle integration and silicon qualification remain.

| Check | Result |
|---|---|
| Official 2×2 analog frame | 334.88 × 225.76 µm; four analog pins |
| Digital standard-cell area | 39,567.9 µm²; 67.3515% of core excluding the analog macro |
| Analog macro | 140 × 90 µm; 12,600 µm² |
| Combined core occupancy | 73.1172% of 71,348.4 µm² |
| Complete physical flow | Pass; routing, antenna, Magic/KLayout DRC and LVS clear |
| Official exported-GDS precheck | 17/17 pass |
| Independent exported-GDS transistor LVS | Unique match; PHY includes 20 MOS and 9 resistors, no black box |
| Actual routed digital netlist | 44/44 external-pin tests pass |
| Extracted analog macro RC simulation | 30/30 loopback cases pass |
| Final digital STA | Nine corners pass setup, hold and library slew/capacitance limits |
| Worst setup / hold slack | +504.475068 ns / +0.109336 ns |

Exact GDS SHA-256: `3e3c5d49441ae6847526168564dae89b2dee7286302094004a529dab48d5b24d`. See [compact summary](compact-layout/summary.json), [artifact hashes](compact-layout/sha256.json), [full flow audit](compact-digital/hold025-result.json), and [layout package](../layout_compact/README.md).

## Timing envelope and reductions

Clock period is 625 ns (1.6 MHz). Hold uncertainty is 0.25 ns, the official SKY130 default; the earlier 4×2 candidate used 0.5 ns total. Setup uncertainty remains 2 ns and clock transition remains 2 ns. This is an explicit change in the timing envelope, not a claim of closure under the previous hold margin. See [pinned official source evidence](compact-digital/hold025-experiment.md).

The analog devices retain their sizes and connectivity in a more compact layout. Digital optimization removes 125 redundant state bits without changing the public protocol. Targeted arithmetic/transition proofs and RTL/mapped regressions pass; whole-core formal equivalence is not claimed. The optional snapshot-reset experiment was not adopted.

## Verification scope

The 30 analog RC cases cover five MOS corners × three paired temperature/supply points × two boost settings. They use the compact macro's 745 resistance and 275 capacitance elements, assumed 1 kΩ loopback legs and 20 pF receive load. TX differential magnitude is approximately 87–242 mV across those cases. Actual shuttle switch/pad/package loads, mismatch, digital coupling/noise and post-fill integration are not qualified by this sweep.

The 44 routed digital tests use functional standard-cell models with uniform 1 ns delay and a behavioral PHY boundary; they are not SDF or whole-chip transistor simulations. Analog timing is checked separately in SPICE and is not included in digital STA. Independent final-GDS LVS includes the analog devices explicitly.

The complete physical flow uses OpenLane 3.0.0.dev21, pinned SKY130 PDK `0536d02d875c8f67dd7cca3902ac457e62f20005`, and final library electrical limits. Independent Magic is 8.3.706, Netgen 1.5.287. Official local precheck uses pinned TT tools `7d2d2ef5261eb1df16d0bc342834d48a8a276881`, KLayout CLI 0.29.9 and Python API 0.30.14. Remote official checks and artifact generation are recorded on each exact commit in the private repository's Actions runs.

## Preserved evidence and remaining work

The [4×2 checkpoint](STATUS_4X2.md), `layout/` and `verification/layout/` remain intact, with source checkpoint `9e7a25e8635dfb594bdffb2d8d872ecba0faff75`. They qualify that older candidate only. The earlier source and schematic evidence remain historical records.

Remaining work is contiguous analog allocation, actual switch/package/board and controller validation, final shuttle/post-fill integration checks, and silicon characterization. No slot has been reserved, design submitted, purchase made, visibility changed, or Pages deployment enabled.
