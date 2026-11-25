# Compact SKY26e candidate

Verified local 2×2 analog layout, 334.88 × 225.76 µm, four analog pins. Full byte TX/RX, on-chip pattern checking and the 32-bit public counters remain. Digital utilization is 67.35%; combined core occupancy is 73.12%.

GDS SHA-256: `3e3c5d49441ae6847526168564dae89b2dee7286302094004a529dab48d5b24d`.

The complete physical flow, 17 official prechecks, full exported-GDS transistor LVS, 44 routed functional tests, 30 analog macro RC cases and nine STA corners pass. Hold uncertainty is the official 0.25 ns default; setup uncertainty and clock transition remain 2 ns. Actual shuttle/board/post-fill qualification remains.

See [verification status](../verification/STATUS.md) and [compact experiment history](../COMPACT_2X2.md). The original 4×2 candidate remains in `../layout/`.

Reproduction configuration: `physical/compact_hold025.json`. Export with `scripts/export_candidate.py`, run independent LVS with `scripts/verify_integrated.py`, functional tests with `scripts/test_routed.py`, and official checks with `scripts/run_precheck.py`. `scripts/package_compact.py` archives a checked candidate and refuses to overwrite an existing archive.
