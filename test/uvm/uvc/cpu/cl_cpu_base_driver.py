import cocotb
from cocotb.triggers import RisingEdge, Event, First

from pyuvm import ConfigDB, uvm_component, uvm_driver, uvm_fatal
from .cl_cpu_config import cl_cpu_config


class cl_cpu_base_driver(uvm_driver):
    """Base driver class for CPU interface with common functionality."""

    def __init__(self, name: str = "cl_cpu_base_driver", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.cfg: cl_cpu_config | None = None
        self.main_proc = None
        self.reset_event: Event = Event()

    def build_phase(self):
        super().build_phase()
        self.cfg = ConfigDB().get(self, "", "cfg")
        if self.cfg is None:
            uvm_fatal("CPU_DRV", "No config passed to CPU driver")

    async def run_phase(self):
        await super().run_phase()
        await self.main_loop()

    async def main_loop(self):
        # Start both coroutines - driver_loop handles reset internally via nested loops
        # handle_reset just monitors for reset and sets the event
        main_proc = cocotb.start_soon(self.driver_loop())
        rst_proc = cocotb.start_soon(self.handle_reset())
        
        # Wait for both to complete (they run forever)
        await First(main_proc, rst_proc)

    async def driver_loop(self) -> None:
        """Main driver loop. Override in subclasses."""
        uvm_fatal("DRV_BASE","Error! driver_loop must be overwritten")

    async def handle_reset(self) -> None:
        """Main reset handler. Override in subclasses"""
        uvm_fatal("DRV_BASE","Error! handle_reset must be overwritten")

    def drive_reset(self):
        """Drive reset signals. Implemented by subclasses"""
        uvm_fatal("DRV_BASE","Error! drive_reset must be overwritten in subclasses")
