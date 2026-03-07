import cocotb
from cocotb.triggers import RisingEdge, First, Event

from pyuvm import ConfigDB, uvm_component, uvm_monitor, uvm_fatal, uvm_analysis_port
from .cl_mem_config import cl_mem_config
from .cl_mem_seq_item import cl_mem_seq_item
from .cl_mem_types import MemOp


class cl_mem_monitor(uvm_monitor):
    """Monitor for memory interface signals (uio pins).

    Monitors the memory FSM handshake:
    - Detects 0x69 handshake (MEM_DRIVE state)
    - Samples uio_in when bus is released (MEM_SAMPLE state)
    """

    HANDSHAKE_PATTERN = 0x69

    def __init__(self, name: str = "cl_mem_monitor", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.cfg: cl_mem_config | None = None
        self.ap: uvm_analysis_port | None = None
        self.main_proc = None
        self.reset_event: Event = Event()

    def build_phase(self):
        super().build_phase()
        self.cfg = ConfigDB().get(self, "", "cfg")
        if self.cfg is None:
            uvm_fatal("MEM_MON", "No config passed to MEM monitor")
        self.ap = uvm_analysis_port("ap", self)

    async def run_phase(self):
        await super().run_phase()
        self.main_proc = cocotb.start_soon(self.monitor_loop())
        cocotb.start_soon(self.handle_reset())

    async def monitor_loop(self) -> None:
        """Main monitor loop - collect transactions."""
        # Wait until reset is deasserted (rst_n goes high)
        while self.cfg.vif.rst_n.value == 0:
            await RisingEdge(self.cfg.vif.clk)
        self.reset_event.clear()

        while True:
            item = await self.collect_transaction()
            if item is not None:
                self.ap.write(item)

    async def handle_reset(self) -> None:
        """Handle reset - restart monitor loop after reset."""
        while True:
            await RisingEdge(self.cfg.vif.clk)
            if self.cfg.vif.rst_n.value == 0:
                self.logger.info("Reset detected in monitor")
                self.reset_event.set()
                if self.main_proc:
                    self.main_proc.cancel()
                while self.cfg.vif.rst_n.value == 0:
                    await RisingEdge(self.cfg.vif.clk)
                # Restart monitor loop after reset
                self.main_proc = cocotb.start_soon(self.monitor_loop())

    async def _do_collect(self) -> cl_mem_seq_item:
        """Perform the actual transaction collection."""
        timeout_cycles = self.cfg.params.response_timeout_cycles
        cycle_count = 0

        # Wait for handshake (uio_oe = 0xFF, uio_out = 0x69)
        while True:
            await RisingEdge(self.cfg.vif.clk)


            uio_oe_val = int(self.cfg.vif.uio_oe.value)
            uio_out_val = int(self.cfg.vif.uio_out.value)

            if uio_oe_val == 0xFF and uio_out_val == self.HANDSHAKE_PATTERN:
                self.logger.debug(f"Monitor detected handshake: uio_out=0x{uio_out_val:02x}")
                break

            cycle_count += 1
            if cycle_count >= timeout_cycles:
                # Return empty item on timeout
                return cl_mem_seq_item("timeout_item")

        # Wait for bus release (MEM_SAMPLE state - uio_oe = 0x00)
        cycle_count = 0
        while True:
            await RisingEdge(self.cfg.vif.clk)


            uio_oe_val = int(self.cfg.vif.uio_oe.value)
            if uio_oe_val == 0x00:
                break

            cycle_count += 1
            if cycle_count >= timeout_cycles:
                return cl_mem_seq_item("timeout_item")

        # Sample uio_in (response data being driven by external agent)
        item = cl_mem_seq_item("mon_item")
        item.data = int(self.cfg.vif.uio_in.value)
        item.op = MemOp.READ  # Memory transactions are reads from cache perspective
        item.resp_valid = True

        self.logger.debug(f"Collected transaction: {item}")
        return item

    async def collect_transaction(self) -> cl_mem_seq_item | None:
        """Monitor the memory interface and collect transactions.

        Returns None if reset occurs during transaction.
        """
        collect_task = cocotb.start_soon(self._do_collect())

        # Wait for either collection to complete or reset
        await First(collect_task, self.reset_event.wait())

        if self.reset_event.is_set():
            collect_task.cancel()
            return None

        return collect_task.result()
