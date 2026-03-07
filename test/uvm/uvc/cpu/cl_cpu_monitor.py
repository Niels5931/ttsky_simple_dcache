import cocotb
from cocotb.triggers import RisingEdge, ReadOnly, First, Event

from pyuvm import ConfigDB, uvm_component, uvm_monitor, uvm_fatal, uvm_analysis_port
from .cl_cpu_config import cl_cpu_config
from .cl_cpu_seq_item import cl_cpu_seq_item
from .cl_cpu_types import CpuOp


class cl_cpu_monitor(uvm_monitor):
    """Monitor for CPU interface signals."""

    def __init__(self, name: str = "cl_cpu_monitor", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.cfg: cl_cpu_config | None = None
        self.ap: uvm_analysis_port | None = None
        self.main_proc = None
        self.reset_event: Event = Event()

    def build_phase(self):
        super().build_phase()
        self.cfg = ConfigDB().get(self, "", "cfg")
        if self.cfg is None:
            uvm_fatal("CPU_MON", "No config passed to CPU monitor")
        self.ap = uvm_analysis_port("ap", self)

    async def run_phase(self):
        await super().run_phase()
        self.main_proc = cocotb.start_soon(self.monitor_loop())
        cocotb.start_soon(self.handle_reset())

    async def monitor_loop(self) -> None:
        while self.cfg.vif.rst_n.value == 0:
            await RisingEdge(self.cfg.vif.clk)
        self.reset_event.clear()
        while True:
            item = await self.collect_transaction()
            if item is not None:
                self.ap.write(item)

    async def handle_reset(self) -> None:
        while True:
            await RisingEdge(self.cfg.vif.clk)
            if self.cfg.vif.rst_n.value == 0:
                self.logger.info("Reset detected in monitor")
                self.reset_event.set()
                if self.main_proc:
                    self.main_proc.cancel()
                while self.cfg.vif.rst_n.value == 0:
                    await RisingEdge(self.cfg.vif.clk)
                self.main_proc = cocotb.start_soon(self.monitor_loop())

    async def _do_collect(self) -> cl_cpu_seq_item:
        while True:
            await RisingEdge(self.cfg.vif.clk)
            ui_val = int(self.cfg.vif.ui_in.value)
            if (ui_val >> 5) & 1:
                break

        await ReadOnly()

        item = cl_cpu_seq_item("mon_item")
        item.addr = ui_val & 0x1F
        item.op = CpuOp.WRITE if (ui_val >> 6) & 1 else CpuOp.READ

        while True:
            await RisingEdge(self.cfg.vif.clk)
            uo_val = int(self.cfg.vif.uo_out.value)
            if (uo_val >> 4) & 1:
                break

        while True:
            await RisingEdge(self.cfg.vif.clk)
            uo_val = int(self.cfg.vif.uo_out.value)
            if (uo_val >> 5) & 1:
                break

        await ReadOnly()
        item.resp_valid = True
        if item.op == CpuOp.READ:
            item.data = uo_val & 0xF

        self.logger.debug(f"Collected transaction: {item}")
        return item

    async def collect_transaction(self) -> cl_cpu_seq_item | None:
        collect_task = cocotb.start_soon(self._do_collect())

        await First(collect_task, self.reset_event.wait())

        if self.reset_event.is_set():
            collect_task.cancel()
            return None

        return collect_task.result()
