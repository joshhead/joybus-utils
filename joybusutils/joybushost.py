from nmigen import Elaboratable, Signal, Module
from nmigen.sim.pysim import Simulator, Tick

CLOCK_PERIOD = 1/12_000_000
DATA_WIDTH = 4

class JoyBusHost(Elaboratable):
    def __init__(self):
        self.counter = Signal(10) # For timing
        self.data = Signal(DATA_WIDTH)
        self.tx_bit_counter = Signal(DATA_WIDTH)
        self.tx = Signal(reset=1) # Serialized output
        self.data_in = Signal(DATA_WIDTH) # Data in, to serialize
        self.write_enable = Signal() # Strobe high to latch data and send
        self.busy = Signal() # High while transmitting

    def ports(self):
        return [self.tx, self.data_in, self.write_enable, self.busy]

    def elaborate(self, platform):
        m = Module()
        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += self.busy.eq(0)
                m.d.comb += self.tx.eq(1) # Idle high
                m.d.sync += self.counter.eq(0)
                m.d.sync += self.data.eq(self.data_in)
                m.d.sync += self.tx_bit_counter.eq(0)
                with m.If(self.write_enable == 1):
                    with m.If(self.data_in[0] == 0):
                        m.next = "TX_0"
                    with m.Else():
                        m.next = "TX_1"
            with m.State("TX_0"):
                m.d.comb += self.busy.eq(1)
                with m.If(self.counter == 48):
                    m.d.sync += self.counter.eq(0)
                    m.d.sync += self.tx_bit_counter.eq(self.tx_bit_counter + 1)
                    next_data = self.data.shift_right(1)
                    m.d.sync += self.data.eq(next_data)
                    with m.If(self.tx_bit_counter == DATA_WIDTH - 1):
                        m.next = "IDLE"
                    with m.Elif(next_data[0] == 0):
                        m.next = "TX_0"
                    with m.Else():
                        m.next = "TX_1"
                with m.Elif(self.counter > 36):
                    m.d.comb += self.tx.eq(1)
                    m.d.sync += self.counter.eq(self.counter + 1)
                with m.Else():
                    m.d.comb += self.tx.eq(0)
                    m.d.sync += self.counter.eq(self.counter + 1)
            with m.State("TX_1"):
                m.d.comb += self.busy.eq(1)
                with m.If(self.counter == 48):
                    m.d.sync += self.counter.eq(0)
                    m.d.sync += self.tx_bit_counter.eq(self.tx_bit_counter + 1)
                    next_data = self.data.shift_right(1)
                    m.d.sync += self.data.eq(next_data)
                    with m.If(self.tx_bit_counter == DATA_WIDTH - 1):
                        m.next = "IDLE"
                    with m.Elif(next_data[0] == 0):
                        m.next = "TX_0"
                    with m.Else():
                        m.next = "TX_1"
                with m.Elif(self.counter > 12):
                    m.d.comb += self.tx.eq(1)
                    m.d.sync += self.counter.eq(self.counter + 1)
                with m.Else():
                    m.d.comb += self.tx.eq(0)
                    m.d.sync += self.counter.eq(self.counter + 1)
        return m


if __name__ == "__main__":
    joybushost = JoyBusHost()
    sim = Simulator(joybushost)

    # There is a sim.run_until() that should let me run without a process,
    # but I can't figure out how to get it working.
    def process():
        yield joybushost.data_in.eq(0b1101)
        for i in range(3000):
            if (i == 10):
                yield joybushost.write_enable.eq(1)
            elif (i == 11):
                yield joybushost.write_enable.eq(0)
            yield Tick()
    sim.add_sync_process(process)
    sim.add_clock(CLOCK_PERIOD)
    with sim.write_vcd("joybushost_sim.vcd", "joybushost_sim.gtkw", traces=joybushost.ports()):
        sim.run()
