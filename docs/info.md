# How it works

A custom 1.8 V differential transmitter and receiver connect to a digital 8N1 byte transceiver. SPI registers control normal byte transfers or an on-chip pattern generator and independent receive checker. The initial target is 100 kbit/s from a 1.6 MHz system clock. The design occupies a 4x2 analog frame and uses four analog pins.

This is a SKY26e candidate with verified local layout checks, not a submitted or fabricated design. It is not qualified as LVDS or RS-485. Analog models use assumed external loads; actual shuttle switches, package, board, noise coupling and post-fill integration still require validation.

# How to test

Connect TX+ (ua[0]) to RX+ (ua[2]), and TX- (ua[1]) to RX- (ua[3]). Use the final carrier pin map to locate these signals. Supply the board-approved power and a 1.6 MHz clock, reset the project, and select it. A USB controller can configure self-tests and read counters over SPI, so functional testing does not require an oscilloscope.

SPI mode 0 uses ui[0] for CSn, ui[1] for SCK, ui[2] for MOSI and uo[0] for MISO. Transactions contain a write flag/address byte followed by a data byte. Keep each SCK half-period and the CS-high interval at least eight system clocks. Read identity D8 at address 00 and version 01 at address 01. Configure a nonzero byte count at addresses 08-0B, choose a pattern at 07, then write 01 to command register 03 to start. Wait for DONE in status register 06, write 10 hex to register 03 to snapshot counters, and inspect status and checked/error counters. PASS requires completed checking with no failure or overflow. Full protocol details and fault tests are in sky26e/REGISTERS.md and sky26e/host/.

# External hardware

A compatible Tiny Tapeout carrier/controller, USB host and two short loopback wires are needed. Board-specific firmware and connector mapping are not yet validated. Do not add a standard differential termination or assume standard-interface electrical compatibility. No oscilloscope is required for digital pass/fail and counter readout; electrical waveform characterization is a separate step.
