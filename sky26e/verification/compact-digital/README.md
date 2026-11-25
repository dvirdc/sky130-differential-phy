# Functional-preserving digital area reduction

The public SPI register layout, all 32-bit counts/targets, saturating arithmetic, snapshot coherence, normal byte TX/RX and BIST fault behavior are preserved. The source hash and same-flow mapped areas are recorded in summary.json. All 44 external-pin RTL and 44 mapped-cell tests pass without editing the existing regression.

Checked payload bits are exactly min(8*checked_bytes, 0xffffffff); the snapshot bits are the same function of the simultaneously captured snapshot byte count. This removes two 32-bit registers and their separate arithmetic. The SAT test proves the full-width increment/reset/clear and snapshot identities, including saturation boundaries.

Target configuration writes are rejected while running. A valid start captures target_count in the old target_active register; that value therefore equals target_count while running. After completion, every accepted configuration write or normal send invalidates DONE. Clear resets DONE; abort and error paths force FAIL. Thus target_active equals target_count whenever its value can affect a future running transition or a potential PASS. The SAT test proves the guarded transition invariant and PASS identity; its reset base holds because RUNNING and DONE are zero.

Sent count is only used for the low three pattern-index bits. There is one outstanding BIST frame: a launch occurs in state1, a receive in state2 increments checked_bytes, and a later launch waits through state3. A run ends when checked_bytes reaches its nonzero 32-bit target. Therefore before any launch, sent==checked<target<=0xffffffff; sent cannot already be saturated. A three-bit modulo8 counter has the same transmitted pattern index. The SAT test checks the full-width bounded-increment identity under that guard.

Run scripts/test_counter_reductions.py for the targeted SAT proofs. These are arithmetic/control-invariant proofs, not a full-core formal equivalence result. The independent full-core Yosys equivalence experiment left 29 control/data nodes unproven with its default cutpoints, so it is not presented as a pass. Normal RTL/mapped regressions remain unchanged and passed.
