import cocotb
import pyuvm
from cocotb.triggers import Timer

@pyuvm.test()
class hello_world(pyuvm.uvm_test):
    """Simple test that verifies clock and reset initialization."""

    async def run_phase(self):
        self.raise_objection()

        await self.test_body()

        self.drop_objection()

    async def test_body(self):

        self.logger.info("Hello World!")
