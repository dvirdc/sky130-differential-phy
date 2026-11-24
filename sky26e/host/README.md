# Testing Diff8 after fabrication

This is a control-protocol driver, not yet a validated Tiny Tapeout board adapter. The exact shuttle board, project selector and physical connector mapping must be known before wiring. No hardware has been fabricated or tested.

Use a compatible Tiny Tapeout controller to power/select/reset the project and supply 1.6 MHz. Connect the project's analog TX+ ua[0] to RX+ ua[2], and TX- ua[1] to RX- ua[3], with short paired wires. These are logical project pins, not PCB connector numbers. Do not attach 3.3 V GPIO to the analog pair or install a 100-ohm termination.

The controller connects ui[0]=CSn, ui[1]=SCK, ui[2]=MOSI, and reads uo[0]=MISO. Set SPI mode 0, MSB first, with one command byte and one data byte per CS assertion. Allow at least 8 core clocks per SCK half-period and 8 clocks CS high between transactions. At a 1.6 MHz core clock, 50 kHz SPI is a conservative starting point. Supply a `transfer(command, value)` function to `Diff8` that returns the second received byte. Clock and reset are separate from SPI. Unused ui bits should be held at zero.

```python
from diff8 import Diff8
phy = Diff8(transfer)
phy.configure(count=1024, pattern=0, boost=False)
phy.start()
# Poll status at a modest rate; allow about 0.2 seconds plus host overhead.
# Wait until status()['running'] is false, with a finite host timeout.
result = phy.snapshot()
print(result)
```

A valid completed test must show `done=True`, `passed=True`, no failed/overflow/command_error flag, checked_bytes equal to the requested count, checked_bits equal to eight times that count, and all error counters zero. Repeat for boost=True and patterns 1 through 4. A controller communication timeout is a failed test, never PASS. Wait for tx_busy=False before reconfiguration: DONE can precede the last stop bit finishing.

As a negative control, disconnect one loopback leg and verify that a fresh test fails; reconnect and restart. A physical open input is analog and may behave differently from the high-impedance digital simulation. The transistor/layout implementation must be qualified before fabrication.

A 1,250,000-byte test checks 10,000,000 payload bits. At 100 kbit/s, the implemented two-bit inter-frame gap makes this approximately 150 seconds plus small controller overhead. Zero errors is a measured result for those bits and conditions, not a guarantee of zero BER. The 32-bit checked-bit counter limits one unsaturated run to 536,870,911 bytes.

Normal mode uses `send(byte)` and `receive()`. RX holds only one unread byte; another byte sets an overrun and sticky FAIL. SPI polling and USB latency cannot sustain arbitrary back-to-back full-rate traffic. Use paced request/reply, lower baud, or add a FIFO in a future revision. Autonomous BIST does not depend on USB readout speed.

Functional readout needs a USB controller, compatible TT carrier, USB cable, and the two loopback wires; it does not require an oscilloscope. A multimeter helps power checks. This does not replace analog swing, common-mode, noise and timing-eye measurements.
