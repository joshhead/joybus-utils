from nmigen import Module
from nmigen.sim.pysim import Simulator, Tick
from tinymodule import TinyModule
from nmigen.test.utils import FHDLTestCase
import unittest

CLOCK_PERIOD = 1/12_000_000


class TinyModuleTest(FHDLTestCase):
    def setUp(self):
        self.tinymodule = TinyModule()
        self.sim = Simulator(self.tinymodule)
        self.sim.add_clock(CLOCK_PERIOD)

    def test_output_starts_at_0(self):
        def process():
            self.assertEqual((yield self.tinymodule.output), 0)
        self.sim.add_sync_process(process)
        self.sim.run()

    def test_output_toggles_after5_ticks(self):
        def process():
            for _ in range(4):
                yield Tick()
                self.assertEqual((yield self.tinymodule.output), 0)
            for _ in range(32):
                yield Tick()
                self.assertEqual((yield self.tinymodule.output), 1)
        self.sim.add_sync_process(process)
        self.sim.run()


if __name__ == "__main__":
    unittest.main()
