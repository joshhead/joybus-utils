from nmigen import Elaboratable, Signal, Module
from nmigen.sim.pysim import Simulator, Tick

CLOCK_PERIOD = 1/12_000_000


class JoyBusHost(Elaboratable):
    def __init__(self):
        self.counter = Signal(10)
        self.output = Signal(reset=1)

    def ports(self):
        return [self.output]

    def elaborate(self, platform):
        m = Module()
        m.d.sync += self.counter.eq(self.counter + 1)
        # Once high, output should stay high.
        with m.If(self.output == 0):
            m.d.sync += self.output.eq(0)
        # Otherwise, wait for 5 clock ticks
        with m.Elif(self.counter == 5):
            m.d.sync += self.output.eq(0)
        return m


if __name__ == "__main__":
    joybushost = JoyBusHost()
    sim = Simulator(joybushost)

    # There is a sim.run_until() that should let me run without a process,
    # but I can't figure out how to get it working.
    def process():
        for _ in range(3000):
            yield Tick()
    sim.add_sync_process(process)
    sim.add_clock(CLOCK_PERIOD)
    with sim.write_vcd("joybushost_sim.vcd", "joybushost_sim.gtkw", traces=joybushost.ports()):
        sim.run()
