import cocotb
from cocotb.triggers import RisingEdge, Event, First

from pyuvm import ConfigDB, uvm_component, uvm_driver, uvm_fatal
from .cl_mem_config import cl_mem_config


class cl_mem_base_driver(uvm_driver):
    """Base driver class for memory interface with common functionality."""

    def __init__(self, name: str = "cl_mem_base_driver", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.cfg: cl_mem_config | None = None
        self.main_proc = None
        self.reset_event: Event = Event()

    def build_phase(self):
        super().build_phase()
        self.cfg = ConfigDB().get(self, "", "cfg")
        if self.cfg is None:
            uvm_fatal("MEM_DRV", "No config passed to MEM driver")

    async def run_phase(self):
        await super().run_phase()
        await self.main_loop()

    async def main_loop(self):
        main_proc = cocotb.start_soon(self.driver_loop())
        rst_proc = cocotb.start_soon(self.handle_reset())
        
        await First(main_proc, rst_proc)

    async def driver_loop(self) -> None:
        """Main driver loop. Override in subclasses."""
        uvm_fatal("DRV_BASE", "Error! driver_loop must be overwritten")

    async def handle_reset(self) -> None:
        """Main reset handler. Override in subclasses."""
        uvm_fatal("DRV_BASE", "Error! handle_reset must be overwritten")

    def drive_reset(self):
        """Drive reset signals. Implemented by subclasses."""
        uvm_fatal("DRV_BASE", "Error! drive_reset must be overwritten in subclasses")
