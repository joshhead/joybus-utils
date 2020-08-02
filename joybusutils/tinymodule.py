# This is an example module to help me get started with nmigen
# It should be a module that sets a signal high after 5 clock cycles.

from nmigen import Elaboratable, Shape, Signal, Module, ClockDomain
from nmigen.sim.pysim import Simulator, Tick, Delay
from tabulate import tabulate


class TinyModule(Elaboratable):
    def __init__(self):
        self.counter = Signal(5)
        self.output = Signal()

    def ports(self):
        return [self.output]

    def elaborate(self, platform):
        m = Module()
        m.d.sync += self.counter.eq(self.counter + 1)
        # Once high, output should stay high.
        with m.If(self.output == 1):
            m.d.sync += self.output.eq(1)
        # Otherwise, wait for 5 clock ticks
        with m.Elif(self.counter == 5):
            m.d.sync += self.output.eq(1)
        return m


if __name__ == "__main__":
    tinymodule = TinyModule()
    sim = Simulator(tinymodule)

    sim_results = []

    def process():
        # Enough ticks for the counter to overflow
        for i in range(35):
            sim_results.append([i, (yield tinymodule.counter), (yield tinymodule.output)])
            yield Tick()
    sim.add_sync_process(process)
    # 12mhz clock
    sim.add_clock(1/1_200_000)
    with sim.write_vcd("tinymodule_sim.vcd", "tinymodule_sim.gtkw", traces=tinymodule.ports()):
        sim.run()

    print(tabulate(sim_results, headers=["Clock", "Counter", "Output"]))
