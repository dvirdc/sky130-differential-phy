# Diff8 register interface v1

SPI mode 0, MSB first, exactly 16 SCK pulses while CSn is low. First byte is write flag in bit 7 and address in bits 6:0. Second byte is write data or returned read data. One register per transaction; there is no auto-increment. Keep each half SCK period and the CS-high interval at least 8 system clocks. ui[0:2] are CSn/SCK/MOSI; uo[0] is MISO. Reads of undefined registers return zero. A truncated transaction has no write effect.

| Address (hex) | Access | Meaning |
|---|---|---|
| 00 | R | Identity D8 |
| 01 | R | Protocol version 01 |
| 02 | RW | Boost, 0 or 1 |
| 03 | W | Command (one exact value, not a bitmask) |
| 04 | RW | TX byte / fixed-pattern byte |
| 05 | R | RX byte; completed read clears RX ready |
| 06 | R | Status, defined below |
| 07 | RW | Pattern: 0 PRBS8, 1 alternating 55/AA, 2 walking ones, 3 walking zeros, 4 fixed |
| 08–0B | RW | Target bytes, 32-bit little endian, reset 32 |
| 0C–0D | RW | Baud divisor, 16-bit little endian, reset 1; zero rejected |
| 10–13 | R | Snapshot checked bytes |
| 14–17 | R | Snapshot checked payload bits |
| 18–1B | R | Snapshot mismatched bytes |
| 1C–1F | R | Snapshot mismatched payload bits |
| 20–23 | R | Snapshot framing errors |
| 24–27 | R | Snapshot receive timeouts |
| 28–2B | R | Snapshot normal-mode receive overruns |
| 2C | R | Expected byte at last payload mismatch |
| 2D | R | Actual byte at last payload mismatch |

Command values: 01 start BIST; 02 clear results; 04 transmit TX byte; 08 abort BIST with failure; 10 snapshot all counters. Start/clear/send require idle TX and no running BIST; start also requires idle RX. Configuration writes require idle TX/RX and no BIST. Invalid commands or guarded writes set command_error and sticky FAIL. Start rejects a zero target. A valid start clears prior errors and counters. Abort stops the checker, but an already launched UART frame can finish. Wait for TX idle before reconfiguration.

Status bits from LSB: RUNNING, DONE, PASS, FAIL, TX_BUSY, RX_READY, OVERFLOW, COMMAND_ERROR. PASS requires DONE, nonzero active target, exact checked-byte count, no FAIL and no OVERFLOW. Configuration changes and normal send invalidate an old PASS. Snapshot counters are coherent with each other at the snapshot command; status is live. For a final report wait until RUNNING clears, then snapshot.

Counters saturate at FFFFFFFF. Overflow is sticky and disqualifies PASS. A run longer than 536,870,911 bytes saturates the payload-bit counter; split long tests into multiple runs. UART framing bits are excluded from payload-bit counters. Wrong payload counts errors and continues; framing errors/timeouts stop the BIST. RX timeout is 512 oversample ticks, or 32 bit periods. The inter-frame gap is 32 oversample ticks after TX becomes idle. PRBS polynomial x^8+x^6+x^5+x^4+1, seed A5, left shift; feedback is the XOR of old bits 7,5,4,3. TX and expected RX sequence states advance independently.

Rate = clk / (16 × divisor). Default clk 1.6 MHz gives 100 kbit/s. RX uses an independent synchronizer/start detector and three center samples, not a TX valid strobe. Receiver clock tolerance is verified behaviorally at ±2% for the tested frames, not an analog interoperability guarantee.

Output pins: uo[0] MISO; uo[1] raw RX; uo[2] RUNNING; uo[3] PASS; uo[4] FAIL; uo[5] heartbeat; uo[6] raw TX serial; uo[7] one-clock RX-valid pulse. uio[0] drives boost monitor; uio[7:1] outputs and output enables are zero. Input ui[7:3] and uio inputs are unused. Heartbeat toggles every 2^19 clock cycles (about 1.53 Hz at 1.6 MHz).

Normal receive holds one byte. An unread byte overwritten by a new frame sets overrun and FAIL. External software must pace transfers; no FIFO or flow control is implemented. Reset or ena=0 clears digital state. Physical power isolation and reset release timing still require integration verification.
