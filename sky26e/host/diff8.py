"""Control driver for Diff8 register protocol v1, CPython/MicroPython compatible.
Supply transfer(command, value) returning the second received SPI byte.
Use mode 0, MSB first, CS low for exactly 16 clocks, >=8 core clocks per
SCK half-period, and >=8 core clocks CS high between transactions.
The board adapter must select the project, supply clk/reset and map pins.
"""
class Diff8:
    COUNTERS = (('checked_bytes', 0x10), ('checked_bits', 0x14),
                ('error_bytes', 0x18), ('error_bits', 0x1c),
                ('framing_errors', 0x20), ('timeouts', 0x24),
                ('overruns', 0x28))

    def __init__(self, transfer):
        self.transfer = transfer
        if self.read(0) != 0xd8 or self.read(1) != 1:
            raise ValueError('Diff8 identity/version mismatch')

    def read(self, address):
        return self.transfer(address & 0x7f, 0) & 0xff

    def write(self, address, value):
        self.transfer(0x80 | (address & 0x7f), value & 0xff)

    def status(self):
        value = self.read(6)
        names = ('running', 'done', 'passed', 'failed', 'tx_busy',
                 'rx_ready', 'overflow', 'command_error')
        return {name: bool(value & (1 << i)) for i, name in enumerate(names)}

    def configure(self, count=1024, pattern=0, boost=False, divisor=1, fixed=0xa5):
        if not 1 <= count <= 0x1fffffff:
            raise ValueError('count must fit the 32-bit payload bit counter')
        if not 0 <= pattern <= 4 or not 1 <= divisor <= 0xffff:
            raise ValueError('invalid pattern or baud divisor')
        s = self.status()
        if s['running'] or s['tx_busy']:
            raise RuntimeError('wait for the transmitter to become idle')
        self.write(3, 2)
        self.write(2, int(bool(boost)))
        self.write(7, pattern)
        self.write(4, fixed)
        for i in range(4):
            self.write(8+i, count >> (8*i))
        # Intermediate divider must stay nonzero for both directions.
        self.write(12, 1)
        self.write(13, divisor >> 8)
        self.write(12, divisor)
        if self.status()['command_error']:
            raise RuntimeError('configuration rejected; ensure RX is idle')

    def start(self):
        self.write(3, 1)

    def snapshot(self):
        self.write(3, 16)
        data = {name: sum(self.read(base+i) << (8*i) for i in range(4))
                for name, base in self.COUNTERS}
        data['status'] = self.status()
        data['bad_expected'] = self.read(0x2c)
        data['bad_actual'] = self.read(0x2d)
        return data

    def send(self, byte):
        if not 0 <= byte <= 255:
            raise ValueError('byte out of range')
        s = self.status()
        if s['running'] or s['tx_busy']:
            raise RuntimeError('transmitter busy')
        self.write(4, byte)
        self.write(3, 4)
        if self.status()['command_error']:
            raise RuntimeError('send rejected')

    def receive(self):
        return self.read(5) if self.status()['rx_ready'] else None

    def abort(self):
        self.write(3, 8)
