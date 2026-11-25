# SKY26e differential byte transceiver and self-test

Status: complete SKY130 2×2 physical flow and independent exported-GDS checks pass. The full byte transceiver, PHY and 32-bit self-test interface are implemented. See verification/STATUS.md for exact evidence and qualification limits. The development repository root remains GF180 reference material and must not be submitted as SKY130.

## Target and scope

Target TTSKY26e, published close date 2026-11-30. User reports 15 analog slots and 211 tiles available on 2026-11-24; no slot has been reserved or purchased by this agent. Focus only on the differential project. IR, FSK and microphone projects are out of scope.

Implemented area: one 2×2 analog frame (four tiles), 334.88 × 225.76 µm, and four analog pins. Digital utilization is 67.3515%, and total core occupancy including the 140 × 90 µm PHY is 73.1172%. The original verified 4×2 candidate remains archived. Confirm contiguous allocation with Tiny Tapeout; no allocation is reserved.

Preserve a separate, unchanged GF180 checkout. SKY130 sign-off must use the SKY26e pinned PDK 0536d02d875c8f67dd7cca3902ac457e62f20005. Official tt-gds-action ttsky26e resolves to df73a1e7b52e940423ff55f9354b2b8140d38cb7 as checked on 2026-11-24. No Pages or public publishing.

## Recommended architecture

- One on-die differential transmitter and one differential receiver constitute the PHY. A second PHY is unnecessary for single-chip loopback.
- An 8-bit transmit register feeds a UART-style serializer: idle high, start bit, eight data bits least significant first, stop bit (8N1). Nominal line rate is 100 kbit/s; payload throughput is at most 10 kbyte/s before any higher-level protocol overhead.
- An independently framing receive engine synchronizes the recovered logic signal, detects a start edge, samples at 16x baud with a center-sample majority decision, and reports received bytes plus framing errors. It must not simply reuse the TX byte-valid strobe.
- Proposed 1.6 MHz external system clock gives a 100 kbit/s bit rate. Faster/lower rates can be selected by a programmable divider. Clock source comes from the TT controller; no on-chip oscillator or high-speed CDR is proposed.
- Normal mode accepts user bytes and returns received bytes through a small register interface, with explicit TX-ready, RX-valid and overrun handling.
- Self-test mode generates deterministic data, serializes it through the real analog TX, receives it through the real analog RX, and compares the decoded bytes against an independently maintained expected sequence.
- Patterns: alternating bits, walking ones/zeros, a deterministic pseudorandom byte sequence, and user-specified bytes. Account for startup synchronization before counting test data.
- Report checked bytes, checked payload bits, mismatched payload bits, mismatched bytes, framing errors, missing-byte timeouts, and receive overruns. Counters saturate with an overflow flag rather than silently wrapping.
- PASS requires completion of a programmed nonzero test length, expected receive progress, and zero error/timeout/overrun conditions. A dead or disconnected receiver must fail, not show a misleading zero-error pass. Keep RUNNING and PASS distinct.
- Expose sticky FAIL, test-complete PASS, heartbeat, raw RX and TX logic for simple board LEDs/debug. A USB-connected controller reads counters and configures tests. The implemented SPI register bus and pin map are documented in REGISTERS.md; a host protocol driver and wiring guide are under host/.

## Functional test without an oscilloscope

External analog connections (project ua indices, not assigned PCB connector numbers):

- ua[0] TX+ to ua[2] RX+.
- ua[1] TX- to ua[3] RX-.

Use short paired wires and high-impedance loading; do not add a 100-ohm termination. This exercises the actual analog pad/switch path as well as TX/RX. A purely internal digital loopback is useful only to isolate digital-controller faults and must be clearly labelled as bypassing the analog PHY.

Start with a short fixed-pattern test, then run pseudorandom traffic in normal and boost settings. Longer tests report the measured error count and tested bit count, not an unsupported zero-BER guarantee. With 8N1 framing, 10 million payload bits take at least 125 seconds at 100 kbit/s line rate, plus acquisition and inter-frame gaps.

A TT-compatible USB controller/board provides power, project selection, the system clock, control and counter readout. Confirm the exact GF/SKY board compatibility and final shuttle pin map before specifying a carrier or wiring numbers. No oscilloscope is needed for these digital functional tests. They do not measure analog swing, common-mode range, noise, timing eye or supply-transient margins. A multimeter can optionally check static levels and current.

Two independently clocked copies can later communicate over separate pairs for full duplex. Same-chip loopback is not evidence of independent-clock interoperability: test baud-rate mismatch, framing, reset and disconnect behavior separately.

## SKY130 port requirements

Use SKY130 device models, resistor primitives, layout rules and official analog frame. Assess a 1.8 V VDPWR-only implementation first to keep the digital engine and analog I/O internally compatible; that changes nominal common mode to approximately 0.9 V and requires fresh receiver bias and TX attenuation design. Preserve the functional intent, not GF180 transistor dimensions or the prior simulated swing. Do not reuse 3.3 V core assumptions. If 3.3 V analog power is needed, add the proper VAPWR frame and verified level shifting; do not connect 3.3 V analog nodes directly to 1.8 V digital cells.

Integrate the digital controller and analog macro in the same custom-GDS design. Provide clock/control isolation and deliberate supply/ground routing; check switching-noise coupling into the receiver. All unused output and output-enable ports must be physically tied low.

## Acceptance gates

1. RTL simulation with an independent receiver clock model, randomized payloads and reset; deliberately inject bit flips, stuck-high/low, missing returns, bad stop bits and clock mismatch. Demonstrate that each appropriate failure is detected.
2. SKY130 schematic nominal/PVT simulations, TX boost, receiver sensitivity and load tests using the pinned PDK. No ideal replacement for the active analog blocks in claimed PHY tests.
3. Digital synthesis/timing, integrated layout, pinned-PDK DRC and unique LVS; independent exported-GDS reimport checks.
4. Exact-GDS extraction and mixed-signal loopback, including documented TT analog-switch/pad loading and digital activity.
5. Official SKY26e physical precheck and Docs on the exact candidate commit. GF180 results are historical evidence only.
6. Post-fill and final shuttle integration remain separate qualification gates.

## Implementation and tool status

The digital implementation includes independently clocked UART reception, five BIST patterns, saturating counters, explicit timeout/framing/overrun flags, and SPI control. Forty-four external-pin tests pass at RTL and against synthesized SKY130 HD cells with uniform 1 ns model delays. Neither run models extracted analog behavior or routed timing. The compact integrated layout additionally passes all 44 tests against its actual routed netlist; nine-corner STA independently checks timing.

Earlier tool bring-up: The exact SKY26e PDK is installed separately from the older native PDK. Native ngspice 46 runs the schematic. Magic 8.3.706 was built from official commit 1d42dfcdf6cd91df7a59198477324c2ca78ba439 in an isolated container and loads this PDK. Nine generated primitive cell types pass local Magic DRC after outward gate-contact M1 landing-pad extensions; this does not establish connected-PHY DRC, LVS or qualification. The native OpenLane install has an incompatible x86_64 libparse extension on this ARM Mac. An official ARM64 OpenLane 3.0.0.dev21 tool archive is staged on host disk and mounted read-only into the container because the Docker data disk is full.

See verification/STATUS.md for checkpoint evidence, hashes and outstanding gates. Build products and transient simulation waves are in the ignored build/ directory. Root GF180 files remain historical reference only.

## Sources

- https://tinytapeout.com/chips/
- https://tinytapeout.com/specs/analog/
- https://github.com/TinyTapeout/ttsky-analog-template
- https://github.com/TinyTapeout/tt-gds-action/tree/ttsky26e
