from nmigen import Elaboratable, Signal, Module
from nmigen.sim.pysim import Simulator, Tick

CLOCK_PERIOD = 1/12_000_000


class JoyBusHost(Elaboratable):
    def __init__(self):
        self.counter = Signal(10)
        self.output = Signal(reset=1)
        self.write = Signal()

    def ports(self):
        return [self.output, self.write]

    def elaborate(self, platform):
        m = Module()
        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += self.output.eq(1)
                m.d.sync += self.counter.eq(0)
                with m.If(self.write == 1):
                    m.next = "0"
            with m.State("0"):
                with m.If(self.counter == 48):
                    m.d.sync += self.counter.eq(0)
                    m.next = "IDLE"
                with m.Elif(self.counter > 36):
                    m.d.comb += self.output.eq(1)
                    m.d.sync += self.counter.eq(self.counter + 1)
                with m.Else():
                    m.d.comb += self.output.eq(0)
                    m.d.sync += self.counter.eq(self.counter + 1)
        return m


if __name__ == "__main__":
    joybushost = JoyBusHost()
    sim = Simulator(joybushost)

    # There is a sim.run_until() that should let me run without a process,
    # but I can't figure out how to get it working.
    def process():
        for i in range(3000):
            if (i == 10):
                yield joybushost.write.eq(1)
            elif (i == 11):
                yield joybushost.write.eq(0)
            yield Tick()
    sim.add_sync_process(process)
    sim.add_clock(CLOCK_PERIOD)
    with sim.write_vcd("joybushost_sim.vcd", "joybushost_sim.gtkw", traces=joybushost.ports()):
        sim.run()
